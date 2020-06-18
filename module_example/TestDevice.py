import asyncio
import random
import json
from tango import DevState, GreenMode, Database, DbDevInfo
from tango.server import Device, command, attribute

class TestDevice(Device):
    green_mode = GreenMode.Asyncio

    async def init_device(self):
        await super().init_device()
        self._test_attribute = 0.0
        self.set_change_event("testAttribute", True, False)

    @attribute(
        dtype="double",
    )
    async def test_attribute(self):
        return self._test_attribute

    @command(
        dtype_in="str",
        doc_in="A json string: "
               "{ 'attribute_name': '<The name of the attribute>',"
               "  'number_of_events':'<Number of events to generate (integer)>'"
               "  'rate_of_events': '<Time to wait before next event> (seconds)'"
               "}"
    )
    async def PushScalarChangeEvents(self, configuration):
        loop = asyncio.get_event_loop()
        future = loop.create_task(self.attribute_event_generator(configuration))

    async def attribute_event_generator(self, configuration):
        config = json.loads(configuration)
        attribute_name = config["attribute_name"]
        number_of_events = int(config["number_of_events"])
        event_rate = config["rate_of_events"]
        for i in range(number_of_events):
            next_value = random.uniform(0, 50)
            setattr(self, "_{}".format(attribute_name), next_value)
            self.push_change_event(attribute_name, next_value)
            await asyncio.sleep(event_rate)

if __name__ == '__main__':
    db = Database()
    humble_device_one = DbDevInfo()
    humble_device_one.name = 'test/device/1'
    humble_device_one._class = 'TestDevice'
    humble_device_one.server = 'TestDevice/test'
    db.add_server(humble_device_one.server, humble_device_one, with_dserver=True)
    TestDevice.run_server()
