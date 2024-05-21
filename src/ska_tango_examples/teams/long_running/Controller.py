# pylint: disable=abstract-method
import json
import threading
import time
from typing import Callable, Optional

import tango
from ska_control_model import PowerState, TaskStatus
from ska_tango_base import SKABaseDevice
from ska_tango_base.commands import ResultCode, SubmittedSlowCommand
from ska_tango_base.executor import TaskExecutorComponentManager
from tango.server import command, device_property, run


class LRComponentManager(TaskExecutorComponentManager):
    def __init__(
        self,
        max_queue_size,
        logger=None,
        push_change_event=None,
        stations=(),
        state_change_callback=None,
    ):
        self.stations = stations
        self.max_queue_size = max_queue_size
        self.push_change_event = push_change_event
        self.scanning = False
        super().__init__(
            logger=logger,
            # Provide a callback for the inherited _update_component_state
            component_state_callback=state_change_callback,
            # Remaining kwargs are inital device states. If they are not
            # provided, calls to _update_component_state will cause an
            # exception
            power=PowerState.UNKNOWN,
        )
        self.logger.info("Controller component manager initialised")

        self.station_on_cmds = {}
        self.station_off_cmds = {}

    def get_station_proxies(self):
        stations = [tango.DeviceProxy(station) for station in self.stations]
        return stations, len(stations)

    def station_on_event(self, event: tango.EventData):
        # event.attr_value will be empty if the event is in error.
        if not event.err:
            id = event.attr_value.value[0]
            if event.attr_value.value[1]:
                result = json.loads(event.attr_value.value[1])
                if id in self.station_on_cmds and result[0] == int(
                    ResultCode.OK
                ):
                    self.station_on_cmds[id] = True

        return

    def station_off_event(self, event: tango.EventData):
        # event.attr_value will be empty if the event is in error.
        if not event.err:
            id = event.attr_value.value[0]
            if event.attr_value.value[1]:
                result = json.loads(event.attr_value.value[1])
                if id in self.station_off_cmds and result[0] == int(
                    ResultCode.OK
                ):
                    self.station_off_cmds[id] = True

        return

    def _wait_for_stations_event(self, station_events: dict, timeout: int = 5):
        while timeout > 0:
            if all(station_events.values()):
                return True
            timeout -= 1
            time.sleep(1)
        return False

    def wait_for_stations_on(self, timeout=5):
        return self._wait_for_stations_event(
            self.station_on_cmds, timeout=timeout
        )

    def wait_for_stations_off(self, timeout=5):
        return self._wait_for_stations_event(
            self.station_off_cmds, timeout=timeout
        )

    def on(
        self,
        task_callback: Optional[Callable] = None,
        is_cmd_allowed: Optional[Callable] = None,
    ) -> tuple[TaskStatus, str]:
        """"""
        return self.submit_task(
            self._on,
            is_cmd_allowed=is_cmd_allowed,
            task_callback=task_callback,
        )

    def _on(
        self,
        task_callback: Optional[Callable] = None,
        task_abort_event: Optional[threading.Event] = None,
    ):
        if task_callback:
            task_callback(status=TaskStatus.IN_PROGRESS, progress=0)

        self.station_on_cmds = {}

        (
            stations,
            num_stations,
        ) = self.get_station_proxies()
        count = 0
        for station in stations:
            count += 1
            if task_abort_event and task_abort_event.is_set():
                message = "Controller On aborted"
                if task_callback:
                    task_callback(
                        status=TaskStatus.ABORTED,
                        result=(ResultCode.ABORTED, message),
                    )

                return

            station.subscribe_event(
                "longRunningCommandResult",
                tango.EventType.CHANGE_EVENT,
                self.station_on_event,
            )
            return_code, id_or_msg = station.On()
            # TODO add a method to ska-tango-base to prevent race condition
            # when calling long running commands.
            # There is a race condition where a submitted task (e.g. _on())
            # can finish execution before the submit task method returns (e.g.
            # on()).
            # The long running commands in this example are sufficiently slow
            # that they do not complete execution before the submit task
            # finishes.
            if return_code[0] == ResultCode.QUEUED:
                self.station_on_cmds[id_or_msg[0]] = False
                if task_callback:
                    # Progress is a percentage
                    task_callback(progress=int((count / num_stations) * 50))
            else:
                if task_callback:
                    result = (
                        ResultCode.FAILED,
                        f"Could not queue station {station.name()} On command",
                    )
                    if task_callback is not None:
                        task_callback(
                            status=TaskStatus.COMPLETED, result=result
                        )

                return

        if self.wait_for_stations_on(timeout=10):
            result = (ResultCode.OK, "Controller On completed")
            self._update_component_state(power=PowerState.ON)
            if task_callback is not None:
                task_callback(
                    status=TaskStatus.COMPLETED,
                    progress=100,
                    result=result,
                )

            return

        # Although the command execution has failed, the TaskStatus is
        # COMPLETED, as this is a normal failure. The normal failure is
        # instead reported by the ResultCode.
        # An abnormal failure from a Python exception is caught and
        # reported by inheriting from the TaskExecutorComponentManager.
        result = (ResultCode.FAILED, "Not all stations turned on")
        if task_callback is not None:
            task_callback(
                status=TaskStatus.COMPLETED,
                result=result,
            )

        return

    def off(
        self,
        task_callback: Optional[Callable] = None,
        is_cmd_allowed: Optional[Callable] = None,
    ) -> tuple[TaskStatus, str]:
        return self.submit_task(
            self._off,
            is_cmd_allowed=is_cmd_allowed,
            task_callback=task_callback,
        )

    def _off(
        self,
        task_callback: Optional[Callable] = None,
        task_abort_event: Optional[threading.Event] = None,
    ):
        if task_callback:
            task_callback(status=TaskStatus.IN_PROGRESS, progress=0)

        self.station_off_cmds = {}

        (
            stations,
            num_stations,
        ) = self.get_station_proxies()
        count = 0
        for station in stations:
            count += 1
            if task_abort_event and task_abort_event.is_set():
                message = "Controller Off aborted"
                if task_callback:
                    task_callback(
                        status=TaskStatus.ABORTED,
                        result=(ResultCode.ABORTED, message),
                    )

                return

            station.subscribe_event(
                "longRunningCommandResult",
                tango.EventType.CHANGE_EVENT,
                self.station_off_event,
            )
            return_code, id_or_msg = station.Off()
            # TODO add a method to ska-tango-base to prevent race condition
            # when calling long running commands.
            # There is a race condition where a submitted task (e.g. _off())
            # can finish execution before the submit task method returns (e.g.
            # off()).
            # The long running commands in this example are sufficiently slow
            # that they do not complete execution before the submit task
            # finishes.
            if return_code[0] == ResultCode.QUEUED:
                self.station_off_cmds[id_or_msg[0]] = False
                if task_callback:
                    # Progress is a percentage
                    task_callback(progress=int((count / num_stations) * 50))
            else:
                if task_callback:
                    result = (
                        ResultCode.FAILED,
                        f"Could not queue station {station.name()} Off command",
                    )
                    if task_callback is not None:
                        task_callback(
                            status=TaskStatus.COMPLETED, result=result
                        )

                return

        if self.wait_for_stations_off(timeout=10):
            result = (ResultCode.OK, "Controller Off completed")
            self._update_component_state(power=PowerState.OFF)
            if task_callback is not None:
                task_callback(
                    status=TaskStatus.COMPLETED,
                    progress=100,
                    result=result,
                )

            return

        # Although the command execution has failed, the TaskStatus is
        # COMPLETED, as this is a normal failure. The normal failure is
        # instead reported by the ResultCode.
        # An abnormal failure from a Python exception is caught and
        # reported by inheriting from the TaskExecutorComponentManager.
        result = (ResultCode.FAILED, "Not all stations turned off")
        if task_callback is not None:
            task_callback(
                status=TaskStatus.COMPLETED,
                result=result,
            )

        return


class LRController(SKABaseDevice):

    stations = device_property(
        dtype=[
            str,
        ],
        mandatory=False,
        default_value=["test/lrcstation/1"],
    )

    class InitCommand(SKABaseDevice.InitCommand):
        """
        A class for the LRController init_device()
        """

        def do(self):
            super().do()
            self._device._component_state_changed(power=PowerState.STANDBY)

    def create_component_manager(self):
        return LRComponentManager(
            max_queue_size=5,
            logger=self.logger,
            push_change_event=self.push_change_event,
            stations=self.stations,
            state_change_callback=self._component_state_changed,
        )

    def init_command_objects(self):
        super().init_command_objects()
        self.register_command_object(
            "On",
            SubmittedSlowCommand(
                command_name="On",
                command_tracker=self._command_tracker,
                component_manager=self.component_manager,
                method_name="on",
                callback=self.on_completed_callback,
                logger=self.logger,
            ),
        )
        self.register_command_object(
            "Off",
            SubmittedSlowCommand(
                command_name="Off",
                command_tracker=self._command_tracker,
                component_manager=self.component_manager,
                method_name="off",
                callback=self.off_completed_callback,
                logger=self.logger,
            ),
        )

    def is_On_command_allowed(self) -> bool:
        return self.get_state() in [
            tango.DevState.OFF,
            tango.DevState.STANDBY,
            tango.DevState.ON,
            tango.DevState.UNKNOWN,
        ]

    @command(
        dtype_in=None,
        dtype_out="DevVarLongStringArray",
        doc_out="([Command ResultCode], [Unique ID of the command])",
    )
    def On(self):
        """
        An example of a SubmittedSlowCommand.
        """
        handler = self.get_command_object("On")
        return_code, id_or_message = handler(
            is_cmd_allowed=self.is_On_command_allowed
        )
        return ([return_code], [id_or_message])

    def is_On_allowed(self) -> bool:
        """
        Overriding base class check. The Tango auto-detect is_<cmd>_allowed
        must always return true for a SlowCommand as the check happens before
        the command is queued. Instead supply an is_cmd_allowed argument to
        the component manager submit_task method.
        """
        return True

    def on_completed_callback(self, started: bool) -> None:
        # It is not recommended to use completed callbacks as the "invoked"
        # path happens synchronously as part of the command submission to the
        # LRC queue, not when it is dequeued and executed asynchronously.
        if started:
            self.logger.info("Controller On command has been invoked.")
        else:
            self.logger.info("Controller On command has finished executing.")

    def is_Off_command_allowed(self) -> bool:
        return self.get_state() in [
            tango.DevState.OFF,
            tango.DevState.STANDBY,
            tango.DevState.ON,
            tango.DevState.UNKNOWN,
        ]

    @command(
        dtype_in=None,
        dtype_out="DevVarLongStringArray",
        doc_out="([Command ResultCode], [Unique ID of the command])",
    )
    def Off(self):
        """
        An example of a SubmittedSlowCommand.
        """
        handler = self.get_command_object("Off")
        return_code, id_or_message = handler(
            is_cmd_allowed=self.is_Off_command_allowed
        )
        return ([return_code], [id_or_message])

    def is_Off_allowed(self) -> bool:
        """
        Overriding base class check. The Tango auto-detect is_<cmd>_allowed
        must always return true for a SlowCommand as the check happens before
        the command is queued. Instead supply an is_cmd_allowed argument to
        the component manager submit_task method.
        """
        return True

    def off_completed_callback(self, started: bool) -> None:
        # It is not recommended to use completed callbacks as the "invoked"
        # path happens synchronously as part of the command submission to the
        # LRC queue, not when it is dequeued and executed asynchronously.
        if started:
            self.logger.info("Controller Off command has been invoked.")
        else:
            self.logger.info("Controller Off command has finished executing.")


def main(args=None, **kwargs):
    return run((LRController,), args=args, **kwargs)


if __name__ == "__main__":
    main()
