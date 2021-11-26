# pylint: disable=abstract-method
import time

import tango
from ska_tango_base import SKABaseDevice
from ska_tango_base.base import BaseComponentManager
from ska_tango_base.base.task_queue_manager import QueueManager
from ska_tango_base.commands import ResponseCommand, ResultCode
from tango.server import command, run


class TileComponentManager(BaseComponentManager):
    def __init__(
        self, max_queue_size, num_workers, logger=None, push_change_event=None
    ):
        self.max_queue_size = max_queue_size
        self.num_workers = num_workers
        self.logger = logger
        self.push_change_event = push_change_event
        super().__init__(None)

    def create_queue_manager(self) -> QueueManager:
        return QueueManager(
            max_queue_size=self.max_queue_size,
            num_workers=self.num_workers,
            logger=self.logger,
            push_change_event=self.push_change_event,
        )

    def on(self):
        # Switching On takes long
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

    class OnCommand(ResponseCommand):
        def __init__(self, target, logger=None):
            """"""
            super().__init__(target=target, logger=logger)

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

    class OffCommand(ResponseCommand):
        def __init__(self, target, logger=None):
            """"""
            super().__init__(target=target, logger=logger)

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

    class ScanCommand(ResponseCommand):
        def __init__(self, target, logger=None):
            """"""
            super().__init__(target=target, logger=logger)

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
