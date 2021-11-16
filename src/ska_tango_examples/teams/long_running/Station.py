# pylint: disable=abstract-method
import time

import tango
from ska_tango_base import SKABaseDevice
from ska_tango_base.base import BaseComponentManager
from ska_tango_base.base.task_queue_manager import QueueManager
from ska_tango_base.commands import ResponseCommand, ResultCode
from ska_tango_base.utils import LongRunningDeviceInterface
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
        self.scanning = False
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

    def off(self):
        for proxy in self.get_tile_proxies():
            proxy.Off()

    def _wait_for_state(self, state: tango.DevState, timeout: int = 5):
        while timeout > 0:
            if all(
                proxy.State() == state for proxy in self.get_tile_proxies()
            ):
                return True
            timeout -= 1
            time.sleep(1)
        return False

    def wait_for_on(self, timeout=5):
        return self._wait_for_state(tango.DevState.ON, timeout=timeout)

    def wait_for_off(self, timeout=5):
        return self._wait_for_state(tango.DevState.OFF, timeout=timeout)

    def _scan_complete(self, command_name, command_ids):
        assert command_name == "Scan"
        assert len(command_ids) == 2
        self.scanning = False

    def scan(self):
        self.logger.info("Scan started")
        self.scanning = True
        tiles_interface = LongRunningDeviceInterface(
            tango_devices=self.tiles, logger=self.logger
        )
        tiles_interface.execute_long_running_command(
            "Scan", on_completion_callback=self._scan_complete
        )
        self.logger.info("Scan done")

    def wait_for_scan_completion(self, timeout=5):
        while timeout > 0:
            if not self.scanning:
                return True
            timeout -= 1
            time.sleep(1)
        return False


class Station(SKABaseDevice):

    tiles = device_property(
        dtype=[
            str,
        ],
        mandatory=False,
        default_value=["test/lrctile/1", "test/lrctile/2"],
    )

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

    class OffCommand(ResponseCommand):
        def __init__(self, target, logger=None):
            """"""
            super().__init__(target=target, logger=logger)

        def do(self):
            """"""
            device = self.target
            device.component_manager.off()
            if device.component_manager.wait_for_off(timeout=10):
                device.set_state(tango.DevState.OFF)
                return ResultCode.OK, "Controller Off completed"
            else:
                raise RuntimeError("Not all stations turned off")

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
            if component_manager.wait_for_scan_completion(timeout=10):
                return ResultCode.OK, "Station Scan completed"
            else:
                raise RuntimeError("Scan did not complete in time")

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
    return run((Station,), args=args, **kwargs)


if __name__ == "__main__":
    main()
