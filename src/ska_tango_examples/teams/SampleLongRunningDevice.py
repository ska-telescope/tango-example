"""
This module covers a potential reference implementation for long running
commands.
The general idea is to allow Tango commands that will not complete
within the default timeout period to be placed in a queue
and be executed sequentially by a backround thread. Thus leaving the device
responsive to commands and attribute read/writes.

Find the design doc here:
https://confluence.skatelescope.org/pages/viewpage.action?
spaceKey=SWSI&title=SKA+Tango+Base+design+to+support+long+running+commands

Once the design/implementation have been approved, much of this work will be
moved into `ska_tango_base`.

QueueManager
    - Manages the queue and worker thread.
LongRunningCommand
    - Subclass BaseCommand
    - Implementors to implement `do` and `is_allowed`, command queued behind
      the scenes
    - `is_allowed` should either throw a CommandError or return False when
       not allowed.
LongRunningCommandDevice
    - Subclass SkaBaseDevice
    - Contains all the logic to start/manage the queue and status attributes
SampleLongRunningDevice
    - Sample implementation of what an implementor would do
    - Subclass LongRunningCommandDevice
    - Some test commands implemented

"""
import enum
import threading
import time
import traceback
from dataclasses import dataclass
from queue import Empty, Queue

from ska_tango_base import SKABaseDevice
from ska_tango_base.commands import BaseCommand, ResponseCommand
from ska_tango_base.faults import CommandError
from tango import DebugIt, EnsureOmniThread, ErrSeverity, Except
from tango.server import attribute, command, run


class ResultCode(enum.IntEnum):
    """Based on ska_tango_base.commands.ResultCode
    REJECTED and NOT_ALLOWED should be moved there once approved
    """

    OK = 0
    STARTED = 1
    QUEUED = 2
    FAILED = 3
    UNKNOWN = 4
    REJECTED = 5
    NOT_ALLOWED = 6
    ABORTED = 7


class LongRunningCommandState(enum.IntEnum):
    """The state of the long running command"""

    QUEUED = 0
    IN_PROGRESS = 1
    ABORTED = 2
    NOT_FOUND = 3
    OK = 4
    FAILED = 5
    NOT_ALLOWED = 6


@dataclass
class LongRunningRequestResponse:
    """Convenience class to parse the long running command response"""

    response_code: ResultCode
    command_id: str
    command_name: str

    def __init__(self, request_response):
        """Create the LongRunningRequestResponse dataclass

        :param request_response: The response from a Long Running
          Request Command
        :type request_response: list
        """
        self.response_code = request_response[0][0]
        self.command_id = request_response[1][0]
        self.command_name = self.command_id.split("_")[1]


class QueueManager:
    """Manages the worker thread and the attributes that will communicate the
    state of the queue.
    """

    def __init__(
        self, logger, tango_device, max_queue_size, queue_fetch_timeout
    ):
        """QueryManager init

        Creates the queue and starts the thread that will execute commands
        from it.

        :param logger: Python logger
        :type logger: logging.Logger
        :param tango_device: Tango device server that this queue belongs to
        :type tango_device: LongRunningCommandDevice subclass instance
        :param max_queue_size: The maximum size of the queue
        :type max_queue_size: int
        :param max_queue_size: The time to wait for items in the queue
        :type max_queue_size: float
        """
        self._logger = logger
        self._max_queue_size = max_queue_size
        self._work_queue = Queue(self._max_queue_size)
        self._queue_fetch_timeout = queue_fetch_timeout
        self.is_aborting = threading.Event()
        self.is_stopping = threading.Event()
        self.command_queue_lock = threading.Lock()
        self._worker_thread = threading.Thread(
            target=self._worker,
            daemon=True,
        )
        self._tango_device = tango_device
        self._command_result = []
        self._command_ids_in_queue = []
        self._commands_in_queue = []
        self._command_status = []
        self._command_progress = []
        self._currently_executing_id = None
        self._worker_thread.start()

    @property
    def queue_full(self):
        return self._work_queue.full()

    @property
    def command_result(self):
        return self._command_result

    @command_result.setter
    def command_result(self, value):
        self._command_result = value
        self._tango_device.push_change_event(
            "longRunningCommandResult",
            self._command_result,
        )

    @property
    def command_ids_in_queue(self):
        return self._command_ids_in_queue

    @command_ids_in_queue.setter
    def command_ids_in_queue(self, value):
        self._command_ids_in_queue = value
        self._tango_device.push_change_event(
            "longRunningCommandIDsInQueue",
            self._command_ids_in_queue,
        )

    @property
    def commands_in_queue(self):
        return self._commands_in_queue

    @commands_in_queue.setter
    def commands_in_queue(self, value):
        self._commands_in_queue = value
        self._tango_device.push_change_event(
            "longRunningCommandsInQueue",
            self._commands_in_queue,
        )

    @property
    def command_status(self):
        return self._command_status

    @command_status.setter
    def command_status(self, value):
        self._command_status = value
        self._tango_device.push_change_event(
            "longRunningCommandStatus",
            self._command_status,
        )

    @property
    def command_progress(self):
        return self._command_progress

    @command_progress.setter
    def command_progress(self, value):
        if self._currently_executing_id and value:
            self._command_progress = [
                f"{self._currently_executing_id}",
                f"{value}",
            ]
        else:
            self._command_progress = []
        self._tango_device.push_change_event(
            "longRunningCommandProgress",
            self._command_progress,
        )

    def _worker(self):
        """The worker function that runs in the thread.

        Continually:
        - Checks self.is_aborting, if it's set then it drains the commands
          off the queue
            New tasks will be rejected while is_aborting is set.
        - Tries to get a command off the queue to execute. Once a command is
          fetched the `is_allowed` is executed and then the command itself.

        Once a task is completed it executes a callback that updates all the
        attributes relating to the queue.
        """

        with EnsureOmniThread():
            while not self.is_stopping.is_set():
                if self.is_aborting.is_set():
                    # Drain the Queue since self.is_aborting is set
                    while not self._work_queue.empty():
                        (
                            command_object,
                            _,
                            unique_id,
                        ) = self._work_queue.get()
                        self._logger.warning(
                            "Aborting task ID [%s]", unique_id
                        )
                        result = (
                            ResultCode.ABORTED,
                            f"{command_object.command_name} Aborted",
                        )
                        self.result_callback(result, unique_id)
                    self.is_aborting.clear()
                try:
                    (command_object, argin, unique_id,) = self._work_queue.get(
                        block=True, timeout=self._queue_fetch_timeout
                    )
                    self._currently_executing_id = unique_id
                    self.command_status = [f"{unique_id}", "IN PROGRESS"]

                    result = None
                    # Check is_allowed
                    if hasattr(command_object, "is_allowed"):
                        try:
                            command_allowed = command_object.is_allowed(
                                raise_if_disallowed=True
                            )
                            if not command_allowed:
                                result = (
                                    ResultCode.NOT_ALLOWED,
                                    "",
                                )
                        except CommandError as err:
                            result = (
                                ResultCode.NOT_ALLOWED,
                                f"Error: {err} {traceback.format_exc()}",
                            )

                    # If allowed, execute the work
                    if not result:
                        try:
                            if argin is None:
                                result = command_object.do()
                            else:
                                result = command_object.do(argin)
                        except Exception as err:
                            result = (
                                ResultCode.FAILED,
                                f"Error: {err} {traceback.format_exc()}",
                            )
                    self._work_queue.task_done()
                    self.result_callback(result, unique_id)
                except Empty:
                    continue

    def enqueue_command(self, command_object, argin):
        """Adds the Command to the queue.

        :param command_object: Instance of LongRunningCommand
        :type command_object: LongRunningCommand
        :param argin: The argument to the Tango command
        :type argin: Any
        :return: The unique ID of the command
        :rtype: string
        """
        unique_id = self.get_unique_id(command_object.command_name)
        self._work_queue.put([command_object, argin, unique_id])

        with self.command_queue_lock:
            self._command_ids_in_queue.append(unique_id)
            self.command_ids_in_queue = self._command_ids_in_queue
            self._commands_in_queue.append(command_object.command_name)
            self.commands_in_queue = self._commands_in_queue
        return unique_id

    def result_callback(self, result, unique_id):
        """Called when the command, taken from the queue have completed to
        update the appropriate attributes

        :param result: The result of the command
        :type result: tuple, (result_code, result_string)
        :param: The unique ID of the command
        :type: string
        """
        self.command_progress = None
        self.command_result = [f"{unique_id}", f"{result}"]

        if self.commands_in_queue:
            with self.command_queue_lock:
                self.command_ids_in_queue.pop(0)
                self.commands_in_queue.pop(0)
        self.command_status = []

    def abort_commands(self):
        """Start aborting commands"""
        self.is_aborting.set()

    def exit_worker(self):
        """Exit the worker thread
        NOTE: Long running commands in progress should complete
        """
        self.is_stopping.set()

    def get_unique_id(self, command_name):
        """Generate a unique ID for the command

        :param command_name: The name of the command
        :type command_name: string
        :return: The unique ID of the command
        :rtype: string
        """
        return f"{time.time()}_{command_name}"


class LongRunningCommand(BaseCommand):
    def __init__(self, tango_device, target=None):
        """Init LongRunningCommand

        :param tango_device: The Tango device
        :type tango_device: LongRunningCommandDevice
        :param target: the object that this command acts upon; for
            example, a component manager, defaults to None
        :type target: object, optional
        """
        self.command_name = self.__class__.__name__.replace("Command", "")
        self.tango_device = tango_device
        super().__init__(target=target, logger=self.tango_device.logger)

    @property
    def is_aborting(self):
        """Whether aborting is in progress, triggered by AbortCommands

        :return: Whether or not aborting is in progress
        :rtype: bool
        """
        return self.tango_device.queue_manager.is_aborting.is_set()

    @property
    def current_command_progress(self):
        """Indicates the progress of a command

        The value should be a percentage indicator

        :return: [command ID, progress percentage (0-100)]
        :rtype: list
        """
        return self.tango_device.queue_manager.command_progress

    @current_command_progress.setter
    def current_command_progress(self, value):
        self.tango_device.queue_manager.command_progress = value

    def _call_do(self, argin=None):
        """Puts the command onto the queue and updates relevant attributes.
        :param argin: The `do` command argument, defaults to None
        :type argin: Any, optional
        :return: (result_code, result_string)
        :rtype: tuple
        """
        queue_manager = self.tango_device.queue_manager
        if queue_manager.queue_full:
            Except.throw_exception(
                "Command rejected because queue is full",
                "",
                "",
                ErrSeverity.WARN,
            )
        if queue_manager.is_aborting.is_set():
            Except.throw_exception(
                "Command rejected because queue is aborting",
                "",
                "",
                ErrSeverity.WARN,
            )

        unique_id = queue_manager.enqueue_command(self, argin)

        return (ResultCode.QUEUED, f"{unique_id}")

    def do(self, argin=None):
        """"""
        raise NotImplementedError(
            "BaseCommand is abstract; do() must be subclassed not called."
        )


class LongRunningCommandDevice(SKABaseDevice):
    """The Tango device LongRunningCommandDevice"""

    MAX_QUEUE_SIZE = 1
    QUEUE_FETCH_TIMEOUT = 0.1

    class InitCommand(SKABaseDevice.InitCommand):
        """A class for the SKAObsDevice's init_device() "command"."""

        def do(self):
            """Init device"""
            super().do()

            device = self.target

            device.queue_manager = QueueManager(
                logger=self.logger,
                tango_device=device,
                max_queue_size=device.MAX_QUEUE_SIZE,
                queue_fetch_timeout=device.QUEUE_FETCH_TIMEOUT,
            )

            message = "LongRunningCommandDevice Init command completed OK"
            return (ResultCode.OK, message)

    def init_command_objects(self):
        """Initialises the command handlers for commands supported by
        this device.
        """
        super().init_command_objects()

        self.register_command_object(
            "AbortCommands",
            self.AbortCommandsCommand(self.queue_manager, self.logger),
        )
        self.register_command_object(
            "CheckLongRunningCommandStatus",
            self.CheckLongRunningCommandStatusCommand(
                self.queue_manager, self.logger
            ),
        )

    def delete_device(self):
        """Exit the worker thread on QueueManager

        Note, if there are long running commands executing they will continue
        """
        # If the `do` implementation checks whether we are aborting it will
        # exit out cleanly
        self.queue_manager.abort_commands()
        self.queue_manager.exit_worker()

        # A new QueueManager will be created
        super().delete_device()

    @attribute(dtype=[str], max_dim_x=98, polling_period=1000)
    def longRunningCommandIDsInQueue(self):
        return self.queue_manager.command_ids_in_queue

    @attribute(dtype=[str], max_dim_x=98, polling_period=1000)
    def longRunningCommandsInQueue(self):
        return self.queue_manager.commands_in_queue

    @attribute(dtype=[str], max_dim_x=2, polling_period=1000)
    def longRunningCommandStatus(self):
        return self.queue_manager.command_status

    @attribute(dtype=[str], max_dim_x=2, polling_period=1000)
    def longRunningCommandResult(self):
        return self.queue_manager.command_result

    @attribute(dtype=[str], max_dim_x=2, polling_period=1000)
    def longRunningCommandProgress(self):
        return self.queue_manager.command_progress

    class AbortCommandsCommand(ResponseCommand):
        """The command class for the AbortCommand command."""

        def __init__(self, queue_manager, logger=None):
            self.queue_manager = queue_manager
            super().__init__(target=None, logger=logger)

        def do(self):
            """ """
            self.logger.warning("Start aborting long running commands")
            self.queue_manager.abort_commands()
            return (
                ResultCode.OK,
                (
                    "Abort command completed, but the items in the queue may"
                    " still be in the process of being removed"
                ),
            )

    @command(
        dtype_out="DevVarLongStringArray",
    )
    @DebugIt()
    def AbortCommands(self):
        """Empty out long running comands in queue"""
        handler = self.get_command_object("AbortCommands")
        (return_code, message) = handler()
        return [[return_code], [message]]

    class CheckLongRunningCommandStatusCommand(ResponseCommand):
        """The command class for the CheckLongRunningCommandStatus command."""

        def __init__(self, queue_manager, logger=None):
            self.queue_manager = queue_manager
            super().__init__(target=None, logger=logger)

        def do(self, argin):
            """Determine the status of the command ID passed in, if any

            - Check `command_result` to see if it's finished.
            - Check `command_status` to see if it's in progress
            - Check `command_ids_in_queue` to see if it's queued

            :param argin: The command ID
            :type argin: str
            :return: The resultcode for this command and the code for the state
            :rtype: tuple
                (ResultCode.OK, LongRunningCommandState)
            """
            command_id = argin

            with self.queue_manager.command_queue_lock:
                if self.queue_manager.command_result:
                    if command_id == self.queue_manager.command_result[0]:
                        command_result = self.queue_manager.command_result[1]
                        if "ABORTED" in command_result:
                            return (
                                ResultCode.OK,
                                LongRunningCommandState.ABORTED,
                            )
                        if "OK" in command_result:
                            return (ResultCode.OK, LongRunningCommandState.OK)
                        if "FAILED" in command_result:
                            return (
                                ResultCode.OK,
                                LongRunningCommandState.FAILED,
                            )
                        if "NOT_ALLOWED" in command_result:
                            return (
                                ResultCode.OK,
                                LongRunningCommandState.NOT_ALLOWED,
                            )

                if self.queue_manager.command_status:
                    if command_id == self.queue_manager.command_status[0]:
                        return (
                            ResultCode.OK,
                            LongRunningCommandState.IN_PROGRESS,
                        )
                if command_id in self.queue_manager.command_ids_in_queue:
                    return (ResultCode.OK, LongRunningCommandState.QUEUED)

            return (ResultCode.OK, LongRunningCommandState.NOT_FOUND)

    @command(
        dtype_in=str,
        dtype_out="DevVarShortArray",
    )
    @DebugIt()
    def CheckLongRunningCommandStatus(self, argin):
        """Check the status of a long running command by ID"""
        handler = self.get_command_object("CheckLongRunningCommandStatus")
        (return_code, command_state) = handler(argin)
        return [return_code, command_state]


class SampleLongRunningDevice(LongRunningCommandDevice):
    """Implementation of a device that uses long running commands"""

    MAX_QUEUE_SIZE = 3

    def init_command_objects(self):
        """Initialises the command handlers for commands supported by this
        device.
        """
        super().init_command_objects()

        self.register_command_object(
            "Short",
            self.ShortCommand(self.logger),
        )
        self.register_command_object(
            "NonAbortingLongRunning",
            self.NonAbortingLongRunningCommand(self),
        )
        self.register_command_object(
            "AbortingLongRunning", self.AbortingLongRunningCommand(self)
        )
        self.register_command_object(
            "LongRunningException",
            self.LongRunningExceptionCommand(self),
        )
        self.register_command_object(
            "TestA",
            self.TestACommand(self),
        )
        self.register_command_object(
            "TestB",
            self.TestBCommand(self),
        )
        self.register_command_object(
            "TestC",
            self.TestCCommand(self),
        )
        self.register_command_object(
            "TestProgress",
            self.TestProgressCommand(self),
        )
        self.register_command_object(
            "NotAllowedExc",
            self.NotAllowedExcCommand(self),
        )

        self.register_command_object(
            "NotAllowedBool",
            self.NotAllowedBoolCommand(self),
        )

    class ShortCommand(ResponseCommand):
        """The command class for the Short command."""

        def do(self):
            """ """
            self.logger.info("In ShortCommand")
            time.sleep(0.5)  # Emulate  work being done
            return (ResultCode.OK, "ShortCommand completed")

    @command(
        dtype_in=None,
        dtype_out="DevVarLongStringArray",
    )
    @DebugIt()
    def Short(self):
        """ """
        handler = self.get_command_object("Short")
        (return_code, message) = handler()
        return [[return_code], [message]]

    class NonAbortingLongRunningCommand(LongRunningCommand):
        """The command class for the NonAbortingLongRunning command."""

        def do(self, argin):
            """NOTE This is an example of what _not_ to do.

            Always check self.is_aborting periodically so that the command
            will exit out if long running commands are aborted.

            See the implementation of AnotherLongRunningCommand.
            """
            self.logger.info("In NonAbortingLongRunningCommand")
            retries = 45
            while retries > 0:
                retries -= 1
                time.sleep(argin)  # This command takes long
                self.logger.info(
                    "In NonAbortingLongRunningCommand repeating %s",
                    retries,
                )
            return (
                ResultCode.OK,
                f"NonAbortingLongRunningCommand done {argin}",
            )

        def is_allowed(self, raise_if_disallowed=True):
            """Command is allowed"""
            self.logger.info("raise_if_disallowed %s", raise_if_disallowed)
            return True

    @command(
        dtype_in=float,
        dtype_out="DevVarLongStringArray",
    )
    @DebugIt()
    def NonAbortingLongRunning(self, argin):
        """ """
        handler = self.get_command_object("NonAbortingLongRunning")
        (return_code, message) = handler(argin)
        return [[return_code], [message]]

    class AbortingLongRunningCommand(LongRunningCommand):
        """The command class for the AbortingLongRunning command."""

        def do(self, argin):
            """ """
            self.logger.info("In AbortingLongRunningCommand")

            retries = 45
            while not self.is_aborting and retries > 0:
                retries -= 1
                time.sleep(argin)  # This command takes long
                self.logger.info(
                    "In AbortingLongRunningCommand repeating %s", retries
                )

            if retries == 0:  # Normal finish
                return (
                    ResultCode.OK,
                    f"AbortingLongRunningCommand completed {argin}",
                )
            else:  # Aborted finish
                return (
                    ResultCode.ABORTED,
                    f"AbortingLongRunningCommand Aborted {argin}",
                )

    @command(
        dtype_in=float,
        dtype_out="DevVarLongStringArray",
    )
    @DebugIt()
    def AbortingLongRunning(self, argin):
        """ """
        handler = self.get_command_object("AbortingLongRunning")
        (return_code, message) = handler(argin)
        return [[return_code], [message]]

    class LongRunningExceptionCommand(LongRunningCommand):
        """The command class for the LongRunningException command."""

        def do(self):
            """ """
            self.logger.info("In LongRunningExceptionCommand")
            raise Exception("Something went wrong")

    @command(
        dtype_in=None,
        dtype_out="DevVarLongStringArray",
    )
    @DebugIt()
    def LongRunningException(self):
        """ """
        handler = self.get_command_object("LongRunningException")
        (return_code, message) = handler()
        return [[return_code], [message]]

    class TestACommand(LongRunningCommand):
        """The command class for the TestA command."""

        def do(self):
            """ """
            time.sleep(1)
            return (ResultCode.OK, "Done TestACommand")

    @command(
        dtype_in=None,
        dtype_out="DevVarLongStringArray",
    )
    @DebugIt()
    def TestA(self):
        """ """
        handler = self.get_command_object("TestA")
        (return_code, message) = handler()
        return [[return_code], [message]]

    class TestBCommand(LongRunningCommand):
        """The command class for the TestB command."""

        def do(self):
            """ """
            time.sleep(1)
            return (ResultCode.OK, "Done TestBCommand")

    @command(
        dtype_in=None,
        dtype_out="DevVarLongStringArray",
    )
    @DebugIt()
    def TestB(self):
        """ """
        handler = self.get_command_object("TestB")
        (return_code, message) = handler()
        return [[return_code], [message]]

    class TestCCommand(LongRunningCommand):
        """The command class for the TestC command."""

        def do(self):
            """ """
            time.sleep(1)
            return (ResultCode.OK, "Done TestCCommand")

    @command(
        dtype_in=None,
        dtype_out="DevVarLongStringArray",
    )
    @DebugIt()
    def TestC(self):
        """ """
        handler = self.get_command_object("TestC")
        (return_code, message) = handler()
        return [[return_code], [message]]

    class TestProgressCommand(LongRunningCommand):
        """The command class for the TestProgress command."""

        def do(self, argin):
            """Use self.command_progress to indicate progress"""
            for progress in [1, 25, 50, 74, 100]:
                self.current_command_progress = progress
                time.sleep(argin)

            return (ResultCode.OK, "Done TestProgressCommand")

    @command(
        dtype_in=float,
        dtype_out="DevVarLongStringArray",
    )
    @DebugIt()
    def TestProgress(self, argin):
        """Command to test the progress indicator"""
        handler = self.get_command_object("TestProgress")
        (return_code, message) = handler(argin)
        return [[return_code], [message]]

    class NotAllowedExcCommand(LongRunningCommand):
        """The command class for the NotAllowedExc command."""

        def is_allowed(self, raise_if_disallowed=True):
            """Raises a CommandError to mark as not allowed"""
            if raise_if_disallowed:
                raise CommandError("Command not allowed")

        def do(self):
            """Don't do anything, commmand should be rejected"""
            return (ResultCode.OK, "Done NotAllowedExcCommand")

    @command(
        dtype_in=None,
        dtype_out="DevVarLongStringArray",
    )
    @DebugIt()
    def NotAllowedExc(self):
        """Command to test not allowed with exception"""
        handler = self.get_command_object("NotAllowedExc")
        (return_code, message) = handler()
        return [[return_code], [message]]

    class NotAllowedBoolCommand(LongRunningCommand):
        """The command class for the NotAllowedBoolCommand command."""

        def is_allowed(self, raise_if_disallowed=True):
            """Return True or False depending on the
            is_allowed_return_value attribute
            """
            self.logger.info("raise_if_disallowed %s", raise_if_disallowed)
            return getattr(self.tango_device, "is_allowed_return_value")

        def do(self, argin):
            """Simulate some work done"""
            time.sleep(0.5)
            return (ResultCode.OK, "Done NotAllowedExcCommand")

    @command(
        dtype_in=bool,
        dtype_out="DevVarLongStringArray",
    )
    @DebugIt()
    def NotAllowedBool(self, argin):
        """Command to test not_allowed returning
        true or false in not_allowed
        """
        setattr(self, "is_allowed_return_value", argin)
        handler = self.get_command_object("NotAllowedBool")
        (return_code, message) = handler(argin)
        return [[return_code], [message]]


def main(args=None, **kwargs):
    """Run LongRunningCommandDevice"""
    return run((SampleLongRunningDevice,), args=args, **kwargs)


if __name__ == "__main__":
    main()
