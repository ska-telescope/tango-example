import logging
import uuid
from dataclasses import dataclass
from typing import Any, Callable, Dict, List

import tango
from ska_tango_base import SKABaseDevice
from ska_tango_base.commands import ResponseCommand, ResultCode
from tango import DebugIt, EventData, EventType
from tango.server import attribute, command, device_property, run

from ska_tango_examples.teams.SampleLongRunningDevice import (
    LongRunningRequestResponse,
)


@dataclass
class StoredCommand:
    """Used to keep track of commands scheduled across devices.

    command_name: The Tango command to execute across devices.
    command_id: Every Tango device will return the command ID for the
        long running command submitted to it.
    is_completed: Whether the command is done or not
    """

    command_name: str
    command_id: str
    is_completed: bool


class LongRunningDeviceInterface:
    """This class is a convenience class to be used by clients of
    devices that implement long running commands.

    The intent of this class is that clients should not have to keep
    track of command IDs or the various attributes
    to determine long running command progress/results.

    This class is also useful when you want to run a long running
    command across various devices. Once they all complete a callback
    supplied by the user is fired.

    Using this class, a client would need to:
    - Supply the Tango devices to connect to that implements long
      running commands
    - The Long running commands to run (including parameter)
    - Optional callback that should be executed when the command
      completes

    The callback will be executed once the command completes across all
    devices. Thus there's no need to watch attribute changes or keep
    track of commands IDs. They are handled here.
    """

    def __init__(
        self, tango_devices: List[str], logger: logging.Logger
    ) -> None:
        self._logger = logger
        self._tango_devices = tango_devices
        self._long_running_device_proxies = []
        self._result_subscriptions = []
        self._stored_commands: Dict[str, List[StoredCommand]] = {}
        self._stored_callbacks: Dict[str, Callable] = {}

    def setup(self):
        """Only create the device proxy and subscribe when a
        command is invoked.
        """
        if not self._long_running_device_proxies:
            for device in self._tango_devices:
                self._long_running_device_proxies.append(
                    tango.DeviceProxy(device)
                )

        if not self._result_subscriptions:
            for device_proxy in self._long_running_device_proxies:
                self._result_subscriptions.append(
                    device_proxy.subscribe_event(
                        "longRunningCommandResult",
                        EventType.CHANGE_EVENT,
                        self,
                        wait=True,
                    )
                )

    def push_event(self, ev: EventData):
        """Handles the attribute change events

        For every event that comes in:

        - Update command state:
            - Make sure that it's a longrunningcommandresult
            - Check to see if the command ID we get from the event
                is one we are keeping track of.
            - If so, set that command to completed

        - Check if we should fire the callback:
            Once the command across all devices have completed
            (for that command)
            - Check whether all have completed
            - If so, fire the callback
            - Clean up
        """
        if ev.attr_value.name == "longrunningcommandresult":
            if ev.attr_value.value:
                event_command_id = ev.attr_value.value[0]
                for stored_commands in self._stored_commands.values():
                    for stored_command in stored_commands:
                        if stored_command.command_id == event_command_id:
                            stored_command.is_completed = True

        completed_group_keys = []
        for key, stored_command_group in self._stored_commands.items():
            if stored_command_group:
                # Determine if all the commands in this group have completed
                commands_are_completed = [
                    stored_command.is_completed
                    for stored_command in stored_command_group
                ]
                if all(commands_are_completed):
                    completed_group_keys.append(key)

                    # Get the command IDs
                    command_ids = [
                        stored_command.command_id
                        for stored_command in stored_command_group
                    ]
                    command_name = stored_command_group[0].command_name

                    # Trigger the callback, send command_name and command_ids
                    # as paramater
                    self._stored_callbacks[key](command_name, command_ids)
                    # Remove callback as the group completed

        # Clean up
        # Remove callback and commands no longer needed
        for key in completed_group_keys:
            del self._stored_callbacks[key]
            del self._stored_commands[key]

    def execute_long_running_command(
        self,
        command_name: str,
        command_arg: Any = None,
        on_completion_callback: Callable = None,
    ):
        """Execute the long running command with an argument if any.

        Once the commmand completes, then the `on_completion_callback`
        will be executed with the EventData as parameter.
        This class keeps track of the command ID and events
        used to determine when this commmand has completed.

        :param command_name: A long running command that exists on the
            target Tango device.
        :type command_name: str
        :param command_arg: The argument to be used in the long running
            command method.
        :type command_arg: Any, optional
        :param on_completion_callback: The method to execute when the
            long running command has completed.
        :type on_completion_callback: callable, optional
        """
        self.setup()
        unique_id = uuid.uuid4()
        self._stored_callbacks[unique_id] = on_completion_callback
        self._stored_commands[unique_id] = []
        for device_proxy in self._long_running_device_proxies:
            response = LongRunningRequestResponse(
                device_proxy.command_inout(command_name, command_arg)
            )
            self._stored_commands[unique_id].append(
                StoredCommand(
                    command_name,
                    response.command_id,
                    False,
                )
            )


class SampleLongRunningDeviceClient(SKABaseDevice):

    client_devices = device_property(dtype="DevVarStringArray")

    class InitCommand(SKABaseDevice.InitCommand):
        """A class for the SampleLongRunningDeviceClient's init_device()
        command"""

        def do(self):
            """Init device"""
            super().do()
            device = self.target

            device._last_result_command_ids = []
            device._last_result_command_name = ""
            device.long_running_device_interface = LongRunningDeviceInterface(
                device.client_devices, device.logger
            )

            message = "Init command completed OK"
            return (ResultCode.OK, message)

    def init_command_objects(self):
        """Initialises the command handlers for commands supported by
        this device.
        """
        super().init_command_objects()

        self.register_command_object(
            "ExecuteTestA",
            self.ExecuteTestACommand(target=self, logger=self.logger),
        )

        self.register_command_object(
            "ExecuteTestB",
            self.ExecuteTestBCommand(target=self, logger=self.logger),
        )

        self.register_command_object(
            "ExecuteTestC",
            self.ExecuteTestCCommand(target=self, logger=self.logger),
        )

        self.register_command_object(
            "ExecuteNonAbortingLongRunning",
            self.ExecuteNonAbortingLongRunningCommand(
                target=self, logger=self.logger
            ),
        )

    class ExecuteTestACommand(ResponseCommand):
        """The command class for the ExecuteTestACommand command."""

        def do(self):
            """Execute something on the long running device"""
            self.long_running_device_proxy = tango.DeviceProxy(
                "test/longrunning/1"
            )
            self.long_running_device_proxy.TestA()
            self.logger.info("In ExecuteTestACommand")
            return (ResultCode.OK, "Done ExecuteTestACommand")

    @command(
        dtype_in=None,
        dtype_out="DevVarLongStringArray",
    )
    @DebugIt()
    def ExecuteTestA(self):
        """Command to execute the TestA command on the long running
        command device without LongRunningDeviceInterface.
        """
        handler = self.get_command_object("ExecuteTestA")
        (return_code, message) = handler()
        return [[return_code], [message]]

    class ExecuteTestBCommand(ResponseCommand):
        """The command class for the ExecuteTestBCommand command."""

        def do(self):
            """Execute something on the long running device"""
            interface = self.target.long_running_device_interface
            interface.execute_long_running_command(
                "TestB", None, self.target.handle_command_result
            )
            self.logger.info("In ExecuteTestBCommand")
            return (ResultCode.OK, "Done ExecuteTestBCommand")

    @command(
        dtype_in=None,
        dtype_out="DevVarLongStringArray",
    )
    @DebugIt()
    def ExecuteTestB(self):
        """Command to execute the TestB command on the long running
        command device with the LongRunningDeviceInterface.
        """
        handler = self.get_command_object("ExecuteTestB")
        (return_code, message) = handler()
        return [[return_code], [message]]

    class ExecuteTestCCommand(ResponseCommand):
        """The command class for the ExecuteTestCCommand command."""

        def do(self):
            """Execute something on the long running device"""
            interface = self.target.long_running_device_interface
            interface.execute_long_running_command(
                "TestC", None, self.target.handle_command_result
            )
            self.logger.info("In ExecuteTestCCommand")
            return (ResultCode.OK, "Done ExecuteTestCCommand")

    @command(
        dtype_in=None,
        dtype_out="DevVarLongStringArray",
    )
    @DebugIt()
    def ExecuteTestC(self):
        """Command to execute the TestC command on the long running
        command device with the LongRunningDeviceInterface.
        """
        handler = self.get_command_object("ExecuteTestC")
        (return_code, message) = handler()
        return [[return_code], [message]]

    class ExecuteNonAbortingLongRunningCommand(ResponseCommand):
        """The command class for the ExecuteNonAbortingLongRunning
        command."""

        def do(self, argin):
            """Execute something on the long running device"""
            interface = self.target.long_running_device_interface
            interface.execute_long_running_command(
                "NonAbortingLongRunning",
                1.0,
                self.target.handle_command_result,
            )
            self.logger.info("In ExecuteNonAbortingCommand")
            return (ResultCode.OK, "Done ExecuteNonAborting")

    @command(
        dtype_in=float,
        dtype_out="DevVarLongStringArray",
    )
    @DebugIt()
    def ExecuteNonAbortingLongRunning(self, argin):
        """Command to execute the NonAbortingLongRunning command on the
        long runnning command device with the LongRunningDeviceInterface.
        """
        handler = self.get_command_object("ExecuteNonAbortingLongRunning")
        (return_code, message) = handler(argin)
        return [[return_code], [message]]

    @attribute(dtype=[str], max_dim_x=98, polling_period=1000)
    def lastResultCommandIDs(self):
        """An attribute to keep track of the set of command IDs that
        have completed last.

        Used to illustrate how you would update your device via the callback
        and used in tests.

        :return: The set of last completed long running command IDs
        :rtype: str
        """
        return self._last_result_command_ids

    @attribute(dtype=str, max_dim_x=98, polling_period=1000)
    def lastResultCommandName(self):
        """An attribute to keep track of the name of the last completed
        command.

        Used to illustrate how you would update your device via the callback
        and used in tests.

        :return: The last completed long running command name
        :rtype: str
        """
        return self._last_result_command_name

    def handle_command_result(self, command_name: str, command_ids: List[str]):
        """This method is executed when the long running device
           command completed across all devices.

        Update self._last_result_command_ids to the latest completed long
        running command IDs.

        :param command_name: The command name executed across all devices
        :type command_name: str
        :param command_ids: The list of command IDs completed
        :type command_ids: List[str]
        """
        self._last_result_command_ids = command_ids
        self._last_result_command_name = command_name


def main(args=None, **kwargs):
    """Run SampleLongRunningDeviceClient"""
    return run((SampleLongRunningDeviceClient,), args=args, **kwargs)


if __name__ == "__main__":
    main()
