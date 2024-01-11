# pylint: disable=abstract-method
import logging
import time

import tango
from ska_tango_base import SKABaseDevice
from ska_tango_base.commands import ResultCode, SlowCommand
from ska_tango_base.executor import TaskExecutorComponentManager
from tango.server import command, run


class TileComponentManager(TaskExecutorComponentManager):
    def __init__(
        self,
        *args,
        max_workers: int | None = None,
        logger: logging.Logger = None,
        **kwargs,
    ):
        """Init TileComponentManager."""
        super().__init__(
            *args, max_workers=max_workers, logger=logger, **kwargs
        )

    def on(self):
        time.sleep(4)

    def off(self):
        # Switching Off takes long
        time.sleep(4)

    def scan(self):
        self.logger.info("Scan started")
        # Scanning takes long
        time.sleep(4)
        self.logger.info("Scan done")


class Tile(SKABaseDevice):
    def init_command_objects(self):
        self._command_objects = {}
        self.register_command_object(
            "On", self.OnCommand(target=self, logger=self.logger)
        )
        self.register_command_object(
            "Off", self.OffCommand(target=self, logger=self.logger)
        )
        self.register_command_object(
            "Scan",
            self.ScanCommand(
                target=self.component_manager, logger=self.logger
            ),
        )

    def create_component_manager(self):
        return TileComponentManager(
            2,
            2,
            logger=self.logger,
            push_change_event=self.push_change_event,
        )

    class OnCommand(SlowCommand):
        def __init__(self, target, logger=None):
            """"""
            self.target = target
            super().__init__(callback=None, logger=logger)

        def do(self):
            """"""
            device = self.target
            device.component_manager.on()
            device.set_state(tango.DevState.ON)
            return ResultCode.OK, "On completed"

    @command(
        dtype_in=None,
        dtype_out="DevVarLongStringArray",
        doc_out="([Command ResultCode], [Unique ID of the command])",
    )
    def On(self):
        handler = self.get_command_object("On")
        unique_id, return_code = self.component_manager.enqueue(handler)
        return [return_code], [unique_id]

    class OffCommand(SlowCommand):
        def __init__(self, target, logger=None):
            """"""
            self.target = target
            super().__init__(callback=None, logger=logger)

        def do(self):
            """"""
            device = self.target
            device.component_manager.off()
            device.set_state(tango.DevState.OFF)
            return ResultCode.OK, "Tile Off completed"

    @command(
        dtype_in=None,
        dtype_out="DevVarLongStringArray",
        doc_out="([Command ResultCode], [Unique ID of the command])",
    )
    def Off(self):
        handler = self.get_command_object("Off")
        unique_id, return_code = self.component_manager.enqueue(handler)
        return [return_code], [unique_id]

    class ScanCommand(SlowCommand):
        def __init__(self, target, logger=None):
            """"""
            self.target = target
            super().__init__(callback=None, logger=logger)

        def do(self):
            """"""
            component_manager = self.target
            component_manager.scan()
            return ResultCode.OK, "Tile Scan completed"

    @command(
        dtype_in=None,
        dtype_out="DevVarLongStringArray",
        doc_out="([Command ResultCode], [Unique ID of the command])",
    )
    def Scan(self):
        handler = self.get_command_object("Scan")
        unique_id, return_code = self.component_manager.enqueue(handler)
        return [return_code], [unique_id]


def main(args=None, **kwargs):
    return run((Tile,), args=args, **kwargs)


if __name__ == "__main__":
    main()
