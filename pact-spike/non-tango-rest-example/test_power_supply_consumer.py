import pytest

from pactman import Consumer, Provider, Term
from tango import DeviceAttribute, AttrQuality
from tango_pact import TangoPact

from consumer import PowerSupplyConsumer


TANGO_DEVICE_NAME = "test/power_supply/1"

@pytest.fixture
def pact():
    pact = Consumer('Consumer', TangoPact).has_pact_with(Provider('PowerSupply'))
    pact.start_mocking()
    yield pact
    pact.stop_mocking()

@pytest.fixture
def consumer():
    return PowerSupplyConsumer(TANGO_DEVICE_NAME)

def test_get_voltage_attr(pact, consumer):
    expected = DeviceAttribute()
    expected.value = 0.0
    expected.quality = AttrQuality.ATTR_VALID
    # (there are many other fields, but this test is not interested in those)

    (pact
     .given('powersupply is running')
     .upon_receiving('a read request for the voltage attribute')
     .with_request('method', 'read_attribute', 'voltage')
     .will_respond_with(expected))

    with pact:
        result = consumer.get_voltage_attr()
        assert result.value == 0.0
        assert result.quality == AttrQuality.ATTR_VALID

def test_get_current(pact, consumer):
    expected = 11.2
 
    (pact
     .given('powersupply is running')
     .upon_receiving('a short-form read request for the current attribute')
     .with_request('attribute', 'current')
     .will_respond_with(expected))

    with pact:
        result = consumer.get_current()
        assert result == 11.2

def test_ramp_command(pact, consumer):
    expected = True

    (pact
     .given('powersupply is running')
     .upon_receiving('a command to ramp the current')
     .with_request('command', 'ramp', 44.3)
     .will_respond_with(expected))

    with pact:
        result = consumer.ramp_command(44.3)
        assert result == True
