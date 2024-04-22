# pylint: disable=abstract-method
import threading
import time
from typing import Callable, Optional

import tango
from ska_control_model import TaskStatus
from ska_tango_base import SKABaseDevice
from ska_tango_base.commands import (
    ResultCode,
    SlowCommand,
    SubmittedSlowCommand,
)
from ska_tango_base.executor import TaskExecutorComponentManager
from tango.server import command, device_property, run


class LRComponentManager(TaskExecutorComponentManager):
    def __init__(
        self,
        device,
        max_queue_size,
        num_workers,
        logger=None,
        push_change_event=None,
        stations=(),
    ):
        self.device = device
        self.stations = stations
        self.max_queue_size = max_queue_size
        self.num_workers = num_workers
        self.push_change_event = push_change_event
        self.scanning = False
        super().__init__(logger=logger)
        self.logger.info("Component manager initialised")

        self.station_on_cmds = {}
        self.station_off_cmds = {}

    def get_station_proxies(self):
        stations = [tango.DeviceProxy(station) for station in self.stations]
        return stations, len(stations)

    def station_on_event(self, event: tango.EventData):
        id = event.attr_value.value[0]
        if (
            id in self.station_on_cmds
            and event.attr_value.value[1]
            == f'[{int(ResultCode.OK)}, "On completed"]'
        ):
            self.station_on_cmds[id] = True

        return

    def station_off_event(self, event: tango.EventData):
        id = event.attr_value.value[0]
        if (
            id in self.station_off_cmds
            and event.attr_value.value[1]
            == f'[{int(ResultCode.OK)}, "Off completed"]'
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

    class OnCommand(SlowCommand):
        def __init__(self, target, logger, completed_callback):
            """"""
            self.target = target
            super().__init__(callback=completed_callback, logger=logger)

        def is_on_command_allowed(self) -> bool:
            return self.target.get_state() in [
                tango.DevState.OFF,
                tango.DevState.STANDBY,
                tango.DevState.ON,
                tango.DevState.UNKNOWN,
            ]

        def do(
            self,
        ):
            """"""
            command_id = self.target._command_tracker.new_command(
                "LRController OnCommand"
            )

            def _callback(*args, **kwargs):
                return self.target._command_tracker.update_command_info(
                    command_id, *args, **kwargs
                )

            status, message = self.target.component_manager.submit_task(
                self._on_command,
                is_cmd_allowed=self.is_on_command_allowed,
                task_callback=_callback,
            )

            if status == TaskStatus.QUEUED:
                return ResultCode.QUEUED, command_id
            if status == TaskStatus.REJECTED:
                return ResultCode.REJECTED, message

        def _on_command(
            self,
            task_callback: Optional[Callable] = None,
            task_abort_event: Optional[threading.Event] = None,
        ):
            if task_callback:
                task_callback(status=TaskStatus.IN_PROGRESS, progress=0)

            device = self.target
            device.component_manager.station_on_cmds = {}

            (
                stations,
                num_stations,
            ) = device.component_manager.get_station_proxies()
            count = 0
            for station in stations:
                count += 1
                if task_abort_event and task_abort_event.is_set():
                    message = f"Controller {device.get_name()} On aborted"
                    if task_callback:
                        task_callback(
                            status=TaskStatus.ABORTED,
                            result=(ResultCode.ABORTED, message),
                        )

                    return

                station.subscribe_event(
                    "longRunningCommandResult",
                    tango.EventType.CHANGE_EVENT,
                    device.component_manager.station_on_event,
                )
                return_code, id_or_msg = station.On()
                if return_code[0] == ResultCode.QUEUED:
                    device.component_manager.station_on_cmds[
                        id_or_msg[0]
                    ] = False
                    if task_callback:
                        # Progress is a percentage
                        task_callback(
                            progress=int((count / num_stations) * 50)
                        )
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

            if device.component_manager.wait_for_stations_on(timeout=10):
                device.set_state(tango.DevState.ON)
                result = (ResultCode.OK, "Controller On completed")
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

    def is_off_command_allowed(self) -> bool:
        return self.device.get_state() in [
            tango.DevState.OFF,
            tango.DevState.STANDBY,
            tango.DevState.ON,
            tango.DevState.UNKNOWN,
        ]

    def off(
        self,
        task_callback: Optional[Callable] = None,
    ) -> tuple[TaskStatus, str]:
        return self.submit_task(
            self._off,
            is_cmd_allowed=self.is_off_command_allowed,
            task_callback=task_callback,
        )

    def _off(
        self,
        task_callback: Optional[Callable] = None,
        task_abort_event: Optional[threading.Event] = None,
    ):
        if task_callback:
            task_callback(status=TaskStatus.IN_PROGRESS, progress=0)

        device = self.device
        device.component_manager.station_off_cmds = {}

        stations, num_stations = device.component_manager.get_station_proxies()
        count = 0
        for station in stations:
            count += 1
            if task_abort_event and task_abort_event.is_set():
                message = f"Controller {device.get_name()} Off aborted"
                if task_callback:
                    task_callback(
                        status=TaskStatus.ABORTED,
                        result=(ResultCode.ABORTED, message),
                    )

                return

            station.subscribe_event(
                "longRunningCommandResult",
                tango.EventType.CHANGE_EVENT,
                device.component_manager.station_off_event,
            )
            return_code, id_or_msg = station.Off()
            if return_code[0] == ResultCode.QUEUED:
                device.component_manager.station_off_cmds[id_or_msg[0]] = False
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

        if device.component_manager.wait_for_stations_on(timeout=10):
            device.set_state(tango.DevState.OFF)
            result = (ResultCode.OK, "Controller Off completed")
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
            self._device.set_state(tango.DevState.INIT)
            super().do()
            self._device.set_state(tango.DevState.STANDBY)

    def create_component_manager(self):
        return LRComponentManager(
            self,
            max_queue_size=5,
            num_workers=1,
            logger=self.logger,
            push_change_event=self.push_change_event,
            stations=self.stations,
        )

    def init_command_objects(self):
        super().init_command_objects()
        self.register_command_object(
            "On",
            self.component_manager.OnCommand(
                target=self,
                logger=self.logger,
                completed_callback=self.on_completed_callback,
            ),
        )
        self.register_command_object(
            "Off",
            SubmittedSlowCommand(
                command_name="Off",
                command_tracker=self._command_tracker,
                component_manager=self.component_manager,
                method_name="off",
                logger=self.logger,
            ),
        )

    @command(
        dtype_in=None,
        dtype_out="DevVarLongStringArray",
        doc_out="([Command ResultCode], [Unique ID of the command])",
    )
    def On(self):
        """
        An example of a SlowCommand implementation, with all the necessary
        boilerplate code that is factored into SubmittedSlowCommand.
        It is NOT recommended to follow this example, instead follow one of
        the examples registered using SubmittedSlowCommand e.g. Off.
        """
        handler = self.get_command_object("On")
        return_code, id_or_message = handler()
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
        if started:
            self.logger.info("Controller On command has been invoked.")
        else:
            self.logger.info("Controller On command has finished executing.")

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
        return_code, id_or_message = handler()
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
        if started:
            self.logger.info("Controller Off command has been invoked.")
        else:
            self.logger.info("Controller Off command has finished executing.")


def main(args=None, **kwargs):
    return run((LRController,), args=args, **kwargs)


if __name__ == "__main__":
    main()
