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
        self.__polled_attr_1 = random.randint(0, 150)
        self.__polled_attr_2 = random.randint(0, 150)
        self.__polled_attr_3 = random.randint(0, 150)
        self.__polled_attr_4 = random.randint(0, 150)
        self.__polled_attr_5 = random.randint(0, 150)

    # -----------------
    # Polled attributes
    # -----------------
    @attribute(
        dtype="int",
        polling_period=200,
        rel_change="0.5",
        abs_change="1",
    )
    def polled_attr_1(self):
        return int(self.__polled_attr_1)

    @attribute(
        dtype="int",
        polling_period=400,
        rel_change="1",
        abs_change="1",
    )
    def polled_attr_2(self):
        return int(self.__polled_attr_2)

    @attribute(
        dtype="int",
        polling_period=600,
        rel_change="1.5",
        abs_change="1",
    )
     def polled_attr_3(self):
        return int(self.__polled_attr_3)

    @attribute(
        dtype="int",
        polling_period=800,
        rel_change="1.7",
        abs_change="1",
    )
    def polled_attr_4(self):
        return int(self.__polled_attr_4)

    @attribute(
        dtype="int",
        polling_period=1000,
        rel_change="1.7",
        abs_change="1",
    )
    def polled_attr_5(self):
        return int(self.__polled_attr_5)

    # -------
    # Command
    # --------

    @command(
        dtype_in=None,
        doc_in="",
        dtype_out="str",
        doc_out="Some dummy message.",
    )
    def ExecuteWithADelay(self):
        time.sleep(2)
        return "ExecuteWithADelay command finished executing after 2 seconds."


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
