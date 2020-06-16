import asyncio
import random
from tango import DevState, GreenMode, Database, DbDevInfo
from tango.server import Device, command, attribute

class TestDevice(Device):
    green_mode = GreenMode.Asyncio

    async def init_device(self):
        await super().init_device()
        self._test_attribute = 0.0

    @attribute(
        dtype="double",
        polling_period=1000,
        abs_change="1",
        rel_change="0.5",
    )
    def testAttribute(self):
        return self._test_attribute

    @command(
        dtype_in=("int16",),
        doc_in="An array of short values",
    )
    async def PushScalarChangeEvents(self, values):
        loop = asyncio.get_event_loop()
        future = loop.create_task(self.event_generator(values))

    async def event_generator(self, values):
        number_of_events = int(values[0])
        rate = values[1]
        for i in range(number_of_events):
            self._test_attribute = random.uniform(0, 50)
            self.push_change_event("testAttribute", self._test_attribute)
            await asyncio.sleep(rate)

if __name__ == '__main__':
    db = Database()
    humble_device_one = DbDevInfo()
    humble_device_one.name = 'test/device/1'
    humble_device_one._class = 'TestDevice'
    humble_device_one.server = 'TestDevice/test'
    db.add_server(humble_device_one.server, humble_device_one, with_dserver=True)
    TestDevice.run_server()
