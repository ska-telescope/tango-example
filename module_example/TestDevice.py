import asyncio
import json
import random
from tango import DevState, GreenMode, Database, DbDevInfo
from tango.server import Device, command, attribute

class TestDevice(Device):
    green_mode = GreenMode.Asyncio

    async def init_device(self):
        await super().init_device()
        self.__double_scalar = 0.0
        self.__long_scalar = 0
        self.set_change_event("double_scalar", True, False)

    @attribute(
        dtype="double",
    )
    async def double_scalar(self):
        return self.__double_scalar

    @attribute(
        dtype="int",
        polling_period=2000,
        rel_change="1.7",
        abs_change="1",
    )
    async def long_scalar(self):
        return int(self.__long_scalar)

    @command(
        dtype_in="str",
        doc_in="A json string: "
               "{ 'number_of_events':'<Number of events to generate (integer)>'"
               "  'event_delay': '<Time to wait before next event> (seconds)'"
               "}"
    )
    async def PushChangeEventsNonPolledAttributes(self, configuration):
        loop = asyncio.get_event_loop()
        future = loop.create_task(self.non_polled_attributes_event_generator(configuration))

    async def non_polled_attributes_event_generator(self, configuration):
        config = json.loads(configuration)
        number_of_events = int(config["number_of_events"])
        event_rate = config["event_delay"]
        for next_value in range(number_of_events):
            self.__double_scalar = next_value
            self.push_change_event("double_scalar", next_value)
            await asyncio.sleep(event_rate)

    @command(
        dtype_in="str",
        doc_in="A json string: "
               "{ 'number_of_events':'<Number of events to generate (integer)>'"
               "  'event_delay': '<Time to wait before next event> (seconds)'"
               "}"
    )
    async def PushChangeEventsPolledAttributes(self, configuration):
        loop = asyncio.get_event_loop()
        future = loop.create_task(self.polled_attributes_event_generator(configuration))

    async def polled_attributes_event_generator(self, configuration):
        config = json.loads(configuration)
        number_of_events = int(config["number_of_events"])
        event_rate = config["event_delay"]
        for next_value in range(number_of_events):
            await asyncio.sleep(event_rate)
            self.__long_scalar = random.uniform(0, 150)


if __name__ == '__main__':
    db = Database()
    humble_device_one = DbDevInfo()
    humble_device_one.name = 'test/device/1'
    humble_device_one._class = 'TestDevice'
    humble_device_one.server = 'TestDevice/test'
    db.add_server(humble_device_one.server, humble_device_one, with_dserver=True)
    TestDevice.run_server()
