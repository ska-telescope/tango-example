import pytest
from functools import partial
from pactman import Consumer, Provider, Term
from consumer import get_attribute

from tango import DeviceProxy
#from pact import DeviceProxy

@pytest.fixture
def pact():
    pact = Consumer('Consumer').has_pact_with(Provider('Provider'))
    pact.start_service()
    yield pact
    pact.stop_service()


def test_calendar_date(pact):
    attribute_name = "calendar_date"

    regex = r'^1[0-9]{12}$'
    sample_data = '1596416329618'
    expected = {
        'name': 'calendar_date',
        'value': '03/02/0001',
        'quality': 'ATTR_VALID',
        'timestamp': Term(regex, sample_data)
    }

    (pact
     .given('calendarclockdevice is running')
     .upon_receiving('a read request for calendar_date attribute')
     .with_request('read_attribute', attribute_name)
     .will_respond_with(200, body=expected))

    with pact:
        dp = DeviceProxy("test/calendarclockdevice/1")
        # Think about how to make request to mocked tango device.
        result = dp.read_attribute(attribute_name)
    # generate the timestamp from the Term object
    expected['timestamp'] = expected['timestamp'].generate
    assert result == expected


def test_tick(pact):
    command_name = "tick"
    expected = {}

    (pact
     .given('calendarclockdevice is running')
     .upon_receiving('a tick command')
     .with_request('command_inout', command_name)
     .will_respond_with(200, body=expected))

    with pact:
        dp = DeviceProxy("test/calendarclockdevice/1")
        # Think about how to make request to mocked tango device.
        result = dp.command_inout(command_name)
    assert result == expected
