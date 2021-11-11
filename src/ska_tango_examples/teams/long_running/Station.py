# pylint: disable=abstract-method
import time

import tango
from ska_tango_base import SKABaseDevice
from ska_tango_base.base import BaseComponentManager
from ska_tango_base.base.task_queue_manager import QueueManager
from ska_tango_base.commands import ResponseCommand, ResultCode
from tango.server import command, device_property, run


class StationComponentManager(BaseComponentManager):
    def __init__(
        self,
        max_queue_size,
        num_workers,
        logger=None,
        push_change_event=None,
        tiles=(),
    ):
        self.max_queue_size = max_queue_size
        self.num_workers = num_workers
        self.logger = logger
        self.push_change_event = push_change_event
        self.tiles = tiles
        super().__init__(None)

    def create_queue_manager(self) -> QueueManager:
        return QueueManager(
            max_queue_size=self.max_queue_size,
            num_workers=self.num_workers,
            logger=self.logger,
            push_change_event=self.push_change_event,
        )

    def get_tile_proxies(self):
        return [tango.DeviceProxy(tile) for tile in self.tiles]

    def on(self):
        for proxy in self.get_tile_proxies():
            proxy.On()

    def wait_for_on(self, timeout=5):
        while timeout > 0:
            if all(
                [
                    proxy.State() == tango.DevState.ON
                    for proxy in self.get_tile_proxies()
                ]
            ):
                return True
            timeout -= 1
            time.sleep(1)
        return False


class Station(SKABaseDevice):

    tiles = device_property(
        dtype=[
            str,
        ],
        mandatory=True,
    )

    def init_command_objects(self):
        self._command_objects = {}
        self.register_command_object(
            "On", self.OnCommand(target=self, logger=self.logger)
        )

    def create_component_manager(self):
        return StationComponentManager(
            max_queue_size=2,
            num_workers=2,
            logger=self.logger,
            push_change_event=self.push_change_event,
            tiles=self.tiles,
        )

    class OnCommand(ResponseCommand):
        def __init__(self, target, logger=None):
            """"""
            super().__init__(target=target, logger=logger)

        def do(self):
            """"""
            device = self.target
            device.component_manager.on()
            if device.component_manager.wait_for_on(timeout=5):
                device.set_state(tango.DevState.ON)
                return ResultCode.OK, "On completed"
            else:
                raise RuntimeError("Not all tiles turned on")

    @command(
        dtype_in=None,
        dtype_out="DevVarLongStringArray",
        doc_out="([Command ResultCode], [Unique ID of the command])",
    )
    def On(self):
        handler = self.get_command_object("On")
        unique_id, return_code = self.component_manager.enqueue(handler)
        return [return_code], [unique_id]


def main(args=None, **kwargs):
    return run((Station,), args=args, **kwargs)


if __name__ == "__main__":
    main()
