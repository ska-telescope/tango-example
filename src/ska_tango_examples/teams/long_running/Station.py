# pylint: disable=abstract-method
import threading
import time
from typing import Callable, Optional

import tango
from ska_control_model import TaskStatus
from ska_tango_base import SKABaseDevice
from ska_tango_base.commands import ResultCode, SubmittedSlowCommand
from ska_tango_base.executor import TaskExecutorComponentManager
from tango.server import command, device_property, run


class StationComponentManager(TaskExecutorComponentManager):
    def __init__(
        self,
        device,
        max_queue_size,
        logger=None,
        push_change_event=None,
        tiles=(),
    ):
        self.device = device
        self.max_queue_size = max_queue_size
        self.push_change_event = push_change_event
        self.tiles = tiles
        self.scanning = False
        super().__init__(logger=logger)

        self.tile_on_cmds = {}
        self.tile_off_cmds = {}

    def get_tile_proxies(self):
        return [tango.DeviceProxy(tile) for tile in self.tiles]

    def _wait_for_event(self, tile_events: dict, timeout: int = 5):
        while timeout > 0:
            if all(tile_events.values()):
                return True
            timeout -= 1
            time.sleep(1)
        return False

    def tile_on_event(self, event: tango.EventData):
        id = event.attr_value.value[0]
        if (
            id in self.tile_on_cmds
            and event.attr_value.value[1]
            == f'[{int(ResultCode.OK)}, "On completed"]'
        ):
            self.tile_on_cmds[id] = True
        return

    def tile_off_event(self, event: tango.EventData):
        id = event.attr_value.value[0]
        if (
            id in self.tile_on_cmds
            and event.attr_value.value[1]
            == f'[{int(ResultCode.OK)}, "Off completed"]'
        ):
            self.tile_off_cmds[id] = True
        return

    def wait_for_tiles_on(self, timeout=5):
        return self._wait_for_event(self.tile_on_cmds, timeout=timeout)

    def wait_for_tiles_off(self, timeout=5):
        return self._wait_for_event(self.tile_off_cmds, timeout=timeout)

    def is_on_cmd_allowed(self) -> bool:
        return self.device.get_state() in [
            tango.DevState.OFF,
            tango.DevState.STANDBY,
            tango.DevState.ON,
            tango.DevState.UNKNOWN,
        ]

    def on(
        self,
        task_callback: Optional[Callable] = None,
    ) -> tuple[TaskStatus, str]:
        return self.submit_task(
            self._on,
            is_cmd_allowed=self.is_on_cmd_allowed,
            task_callback=task_callback,
        )

    def _on(
        self,
        task_callback: Optional[Callable] = None,
        task_abort_event: Optional[
            threading.Event
        ] = None,  # pylint: disable=unused-argument
    ):
        """"""
        self.tile_on_cmds = {}
        tiles = self.get_tile_proxies()
        for tile in tiles:
            tile.subscribe_event(
                "longRunningCommandResult",
                tango.EventType.CHANGE_EVENT,
                self.tile_on_event,
            )
            return_code, id_or_msg = tile.On()
            if return_code[0] == ResultCode.QUEUED:
                self.tile_on_cmds[id_or_msg[0]] = False
            else:
                if task_callback:
                    result = (
                        ResultCode.FAILED,
                        f"Could not turn tile {tile.name()} on",
                    )
                    if task_callback is not None:
                        task_callback(result=result)
                return

        if self.wait_for_tiles_on(timeout=10):
            self.device.set_state(tango.DevState.ON)
            result = ResultCode.OK, "On completed"
            if task_callback is not None:
                task_callback(result=result)

            return
        else:
            result = ResultCode.FAILED, "Not all tiles turned on"
            if task_callback is not None:
                task_callback(result=result)

            return

    def is_off_cmd_allowed(self) -> bool:
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
            is_cmd_allowed=self.is_off_cmd_allowed,
            task_callback=task_callback,
        )

    def _off(
        self,
        task_callback: Optional[Callable] = None,
        task_abort_event: Optional[
            threading.Event
        ] = None,  # pylint: disable=unused-argument
    ):
        """"""
        self.tile_off_cmds = {}
        tiles = self.get_tile_proxies()
        for tile in tiles:
            tile.subscribe_event(
                "longRunningCommandResult",
                tango.EventType.CHANGE_EVENT,
                self.tile_off_event,
            )
            return_code, id_or_msg = tile.Off()
            if return_code[0] == ResultCode.QUEUED:
                self.tile_off_cmds[id_or_msg[0]] = False
            else:
                if task_callback:
                    result = (
                        ResultCode.FAILED,
                        f"Could not turn tile {tile.name()} off",
                    )
                    if task_callback is not None:
                        task_callback(result=result)
                return

        if self.wait_for_tiles_off(timeout=5):
            self.device.set_state(tango.DevState.OFF)
            result = ResultCode.OK, "Off completed"
            if task_callback is not None:
                task_callback(result=result)

            return
        else:
            result = ResultCode.FAILED, "Not all tiles turned off"
            if task_callback is not None:
                task_callback(result=result)

            return


class Station(SKABaseDevice):

    tiles = device_property(
        dtype=[
            str,
        ],
        mandatory=False,
        default_value=["test/lrctile/1", "test/lrctile/2"],
    )

    class InitCommand(SKABaseDevice.InitCommand):
        """
        A class for the Station init_device()
        """

        def do(self):
            self._device.set_state(tango.DevState.INIT)
            super().do()
            self._device.set_state(tango.DevState.STANDBY)

    def init_command_objects(self):
        super().init_command_objects()
        self.register_command_object(
            "On",
            SubmittedSlowCommand(
                command_name="On",
                command_tracker=self._command_tracker,
                component_manager=self.component_manager,
                method_name="on",
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
                logger=self.logger,
            ),
        )

    def create_component_manager(self):
        return StationComponentManager(
            self,
            max_queue_size=2,
            logger=self.logger,
            push_change_event=self.push_change_event,
            tiles=self.tiles,
        )

    @command(
        dtype_in=None,
        dtype_out="DevVarLongStringArray",
        doc_out="([Command ResultCode], [Unique ID of the command])",
    )
    def On(self):
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

    @command(
        dtype_in=None,
        dtype_out="DevVarLongStringArray",
        doc_out="([Command ResultCode], [Unique ID of the command])",
    )
    def Off(self):
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


def main(args=None, **kwargs):
    return run((Station,), args=args, **kwargs)


if __name__ == "__main__":
    main()
