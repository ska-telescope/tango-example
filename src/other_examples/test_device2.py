import os
import asyncio
import json
import time
import random
from PyTango import GreenMode, Database, DbDevInfo, Except, ErrSeverity
from PyTango.server import Device, command, attribute


class TestDevice2(Device):

    def init_device(self):
        super().init_device()
        self._attr_1 = random.randint(0, 150)

    @attribute(
        dtype="int",
        polling_period=500
    )
    def attr_1(self):
        return int(self._attr_1)

    @command(
    )
    def ExecuteWithADelay(self):
        time.sleep(2)


if __name__ == "__main__":
    db = Database()
    test_device = DbDevInfo()
    if "DEVICE_NAME" in os.environ:
        # DEVICE_NAME should be in the format domain/family/member
        test_device.name = os.environ["DEVICE_NAME"]
    else:
        # fall back to default name
        test_device.name = "test/device/2"
    test_device._class = "TestDevice2"
    test_device.server = "TestDevice2/test"
    db.add_server(test_device.server, test_device, with_dserver=True)
    TestDevice2.run_server()
