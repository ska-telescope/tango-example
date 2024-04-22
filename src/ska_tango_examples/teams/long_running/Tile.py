# pylint: disable=abstract-method
import logging
import threading
import time
from typing import Callable, Optional

import tango
from ska_control_model import TaskStatus
from ska_tango_base import SKABaseDevice
from ska_tango_base.commands import ResultCode, SubmittedSlowCommand
from ska_tango_base.executor import TaskExecutorComponentManager
from tango.server import command, run


class TileComponentManager(TaskExecutorComponentManager):
    def __init__(
        self,
        device,
        *args,
        max_workers: int | None = None,
        logger: logging.Logger = None,
        **kwargs,
    ):
        """Init TileComponentManager."""
        self.device = device
        super().__init__(
            *args, max_workers=max_workers, logger=logger, **kwargs
        )

    def lr_on(self):
        # Switching on takes long
        time.sleep(4)

    def lr_off(self):
        # Switching off takes long
        time.sleep(4)

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
        self.lr_on()
        self.device.set_state(tango.DevState.ON)
        result = (ResultCode.OK, "On completed")
        if task_callback:
            task_callback(status=TaskStatus.COMPLETED, result=result)
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
        self.lr_off()
        self.device.set_state(tango.DevState.OFF)
        result = (ResultCode.OK, "Off completed")
        if task_callback:
            task_callback(status=TaskStatus.COMPLETED, result=result)

        return


class Tile(SKABaseDevice):
    class InitCommand(SKABaseDevice.InitCommand):
        """
        A class for the Tile init_device()
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
        return TileComponentManager(
            self,
            max_queue_size=2,
            num_workers=1,
            logger=self.logger,
            push_change_event=self.push_change_event,
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
    return run((Tile,), args=args, **kwargs)


if __name__ == "__main__":
    main()
