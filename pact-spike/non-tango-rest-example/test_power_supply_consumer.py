import pytest
from pactman import Consumer, Provider, Term
from consumer import get_current
from mock_device_proxy import TangoPact

@pytest.fixture
def pact():
    pact = Consumer('Consumer', TangoPact).has_pact_with(Provider('PowerSupply'))
    pact.start_mocking()
    yield pact
    pact.stop_mocking()

def test_voltage(pact):
    expected = 0.0
    # a read_attribute request returns a DeviceAttribute object with values for
    # of its attributes. At the moment we're retrieving only the name, value, quality
    # and timestamp values from the object just like what the tango rest api server returns

    (pact
     .given('powersupply is running')
     .upon_receiving('a read request for the current attribute')
     .with_request('read_attribute')
     .will_respond_with(expected)) # reply can be tango obj, exception obj, none, int, ...

    with pact:
        result = get_current("test/power_supply/1")
        assert result == 0.0

# def test_tick(pact):
#     command_name = "tick"
#     expected = {}

#     (pact
#      .given('calendarclockdevice is running')
#      .upon_receiving('a tick command')
#      .with_request('command_inout', command_name)
#      .will_respond_with(200, body=expected))

#     with pact:
#         result = command_inout(command_name)
#     assert result == expected
