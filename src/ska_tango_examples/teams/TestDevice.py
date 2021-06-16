import asyncio
import json
import os
import random

from tango import Database, DbDevInfo, ErrSeverity, Except, GreenMode
from tango.server import Device, attribute, command


class TestDevice(Device):
    green_mode = GreenMode.Asyncio

    def init_device(self):
        super().init_device()
        # double scalars
        self.__non_polled_attr_1 = random.uniform(0, 150)
        self.__non_polled_attr_2 = random.uniform(0, 150)
        self.__non_polled_attr_3 = random.uniform(0, 150)
        self.__non_polled_attr_4 = random.uniform(0, 150)
        self.__non_polled_attr_5 = random.uniform(0, 150)
        # long scalars
        self.__polled_attr_1 = random.randint(0, 150)
        self.__polled_attr_2 = random.randint(0, 150)
        self.__polled_attr_3 = random.randint(0, 150)
        self.__polled_attr_4 = random.randint(0, 150)
        self.__polled_attr_5 = random.randint(0, 150)
        # set manual change event for double scalars
        for idx in range(1, 6):
            self.set_change_event(f"non_polled_attr_{idx}", True, False)

    # ---------------------
    # Non polled attributes
    # ---------------------
    @attribute(
        dtype="double",
    )
    async def non_polled_attr_1(self):
        return self.__non_polled_attr_1

    @attribute(
        dtype="double",
    )
    async def non_polled_attr_2(self):
        return self.__non_polled_attr_2

    @attribute(
        dtype="double",
    )
    async def non_polled_attr_3(self):
        return self.__non_polled_attr_3

    @attribute(
        dtype="double",
    )
    async def non_polled_attr_4(self):
        return self.__non_polled_attr_4

    @attribute(
        dtype="double",
    )
    async def non_polled_attr_5(self):
        return self.__non_polled_attr_5

    # -----------------
    # Polled attributes
    # -----------------
    @attribute(
        dtype="int",
        polling_period=2000,
        rel_change="0.5",
        abs_change="1",
    )
    async def polled_attr_1(self):
        return int(self.__polled_attr_1)

    @attribute(
        dtype="int",
        polling_period=2000,
        rel_change="1",
        abs_change="1",
    )
    async def polled_attr_2(self):
        return int(self.__polled_attr_2)

    @attribute(
        dtype="int",
        polling_period=500,
        rel_change="1.5",
        abs_change="1",
    )
    async def polled_attr_3(self):
        return int(self.__polled_attr_3)

    @attribute(
        dtype="int",
        polling_period=1000,
        rel_change="1.7",
        abs_change="1",
    )
    async def polled_attr_4(self):
        return int(self.__polled_attr_4)

    @attribute(
        dtype="int",
        polling_period=1000,
        rel_change="1.7",
        abs_change="1",
    )
    async def polled_attr_5(self):
        return int(self.__polled_attr_5)

    # -------
    # Command
    # --------
    @command()
    async def RaiseException(self):
        Except.throw_exception(
            "TestDevice command failed",
            "Something wrong occured.",
            "Do something else",
            ErrSeverity.ERR,
        )

    @command(
        dtype_in=float,
        doc_in="A floating number representing the command execution latency",
        dtype_out="str",
        doc_out="Some dummy message.",
    )
    async def ExecuteWithADelay(self, latency):
        await asyncio.sleep(latency)
        return f"ExecuteWithADelay command finished executing after {latency} seconds."  # noqa E501

    @command(
        dtype_in="str",
        doc_in="A json string: "
        "{ 'attribute':'<The name of the attribute'"
        "  'number_of_events':'<Number of events to generate (integer)>'"
        "  'event_delay': '<Time to wait before next event (seconds)>'"
        "}",
    )
    async def PushScalarChangeEvents(self, configuration):
        loop = asyncio.get_event_loop()
        loop.create_task(self.attribute_event_generator(configuration))

    async def attribute_event_generator(self, configuration):
        config = json.loads(configuration)
        attr = config["attribute"]
        number_of_events = int(config["number_of_events"])
        event_delay = config["event_delay"]
        polled = self.is_attribute_polled(attr)
        while number_of_events > 0:
            await asyncio.sleep(event_delay)
            # using _classname in calls to setattr and getattr due to name mangling # noqa E501
            next_value = getattr(self, f"_TestDevice__{attr}") + 1
            setattr(self, f"_TestDevice__{attr}", next_value)
            if not polled:
                self.push_change_event(attr, next_value)
            number_of_events -= 1


if __name__ == "__main__":
    db = Database()
    test_device = DbDevInfo()
    if "DEVICE_NAME" in os.environ:
        # DEVICE_NAME should be in the format domain/family/member
        test_device.name = os.environ["DEVICE_NAME"]
    else:
        # fall back to default name
        test_device.name = "test/device/1"
    test_device._class = "TestDevice"
    test_device.server = "TestDevice/test"
    db.add_server(test_device.server, test_device, with_dserver=True)
    TestDevice.run_server()
