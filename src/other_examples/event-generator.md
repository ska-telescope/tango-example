## What's in this device?

A test device with attributes which sends change events at a configurable rate. It also has two commands that raise an exception and delays execution, respectively.

## Attributes

There are two kinds of scalar attributes:
- Five attributes which push change events using a poll period (named as `polled_attr_[i]` where i -> 0 - 5). The polled attributes have different attribute config, i.e. distinct polling period, rel change and abs change values
- Another five attributes which push change events manually (named as `non_polled_attr_[i]` where i -> 0 - 5)

Both polled and non_polled attributes are initialised with a random integer between 0,150.

## Commands

One command (`PushScalarChangeEvents`) which pushes changes events for a specified attribute at a configurable rate. It accepts a configuration as a json string in the format: `'{"attribute": "polled_attr_1", "number_of_events": 5, "event_delay":3}'`

The `RaiseException` command throws a `tango.DevFailed` exception when it is invoked. The other command named `ExecuteWithADelay`, responds to a request after a specific time period has elapsed. The command takes in a floating argument (time in seconds) and returns a string with the argument encoded in it.

## Example Usage

### In SKAMPI 
See [exploration test](https://gitlab.com/ska-telescope/skampi/-/tree/master/post-deployment/exploration)

### Another client example

SYNCHRONOUS device proxy client
```
from tango import DeviceProxy, EventType

dp = DeviceProxy("test/device/1")

def cb(event_data): 
    try: 
        attr_value = event_data.attr_value 
        print(f"{attr_value.name}: {attr_value.value}") 
    except Exception as e: 
        print(f"something went wrong: {e}")

def _subscribe_change_event(attr):
    event_id = dp.subscribe_event(attr, EventType.CHANGE_EVENT, cb)
    return event_id

attrs = ["polled_attr_1", "non_polled_attr_1"]
event_ids = [_subscribe_change_event (attr) for attr in attrs]

# event delays shorter than poll period may make some events missed. try with a delay of 1 to reproduce
dp.pushscalarchangeevents('{"attribute": "polled_attr_1", "number_of_events": 5, "event_delay":3}')
# generate event for non polled attribute
dp.pushscalarchangeevents('{"attribute": "non_polled_attr_1", "number_of_events": 5, "event_delay":1}')
```

ASYNCHRONOUS device proxy client
```
import asyncio
from tango import DeviceProxy, EventType, GreenMode

dp = DeviceProxy("test/device/1", green_mode=GreenMode.Asyncio)

def cb(event_data): 
    try: 
        attr_value = event_data.attr_value 
        print(f"{attr_value.name}: {attr_value.value}") 
    except Exception as e: 
        print(f"something went wrong: {e}")

async def _subscribe_change_event(attr):
    event_id = await dp.subscribe_event(attr, EventType.CHANGE_EVENT, cb, green_mode = GreenMode.Asyncio)
    return event_id

attrs = ["polled_attr_1", "non_polled_attr_1"]
event_ids = []
for attr in attrs:
    event_ids.append(await _subscribe_change_event(attr))

# you can do this:
# await dp.pushscalarchangeevents('{"attribute": "polled_attr_1", "number_of_events": 5, "event_delay": 3}')
# await dp.pushscalarchangeevents('{"attribute": "non_polled_attr_1", "number_of_events": 5, "event_delay": 4}')
# or have an event loop like below

async def sub():
    polled_future = dp.pushscalarchangeevents('{"attribute": "polled_attr_1", "number_of_events": 5, "event_delay": 3}')
    non_polled_future =  dp.pushscalarchangeevents('{"attribute": "non_polled_attr_1", "number_of_events": 5, "event_delay": 4}')
    await asyncio.wait([polled_future, non_polled_future])

loop = asyncio.get_event_loop()
loop.run_until_complete(sub())
```

Code snippet of how the command that responds with an exception works:
```
from tango import DeviceProxy, DevFailed

dp = DeviceProxy("test/device/1")
try:
    dp.RaiseException()
except DevFailed as df:
    print(df)

```
Code snippet of how the command that responds at a predefined latency can be used:

```
from tango import DeviceProxy, DevFailed

dp = DeviceProxy("test/device/1")
```

The client waits for 3000 ms by default
```
dp.ExecuteWithADelay(2.0)  # Should work fine
```

If the device command runs for longer than 3000 ms, the client will throw a timeout error
```
try:
    dp.ExecuteWithADelay(10.0)
except DevFailed as df:
    print(df)
```

To work around that timeout error, you can modify the time by using set_timeout_millis
```
dp.set_timeout_millis(10500)  # 500 ms to allow for any additional overhead handling the command and response over the network
dp.ExecuteWithADelay(10.0)
```

## Deployment

See [docs](https://gitlab.com/ska-telescope/tango-example/-/blob/master/docs/src/index.rst) for deploying the `event-generator` device via a helm repo
