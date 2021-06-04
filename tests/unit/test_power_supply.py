# pylint: disable=redefined-outer-name
# -*- coding: utf-8 -*-
"""
Some simple unit tests of the PowerSupply device, exercising the device from
another host using a DeviceProxy.
"""
import pytest
import tango
from tango.test_context import DeviceTestContext

from ska_tango_examples.basic_example.powersupply import PowerSupply


@pytest.fixture
def power_supply(request):
    """Create DeviceProxy for tests"""
    true_context = request.config.getoption("--true-context")
    if not true_context:
        with DeviceTestContext(PowerSupply) as proxy:
            yield proxy
    else:
        database = tango.Database()
        instance_list = database.get_device_exported_for_class("PowerSupply")
        for instance in instance_list.value_string:
            yield tango.DeviceProxy(instance)


def test_power_supply_is_alive(power_supply):
    """Sanity check: test device on remote host is responsive"""
    try:
        power_supply.ping()
    except tango.ConnectionFailed:
        pytest.fail("Could not contact power_supply")


def test_init(power_supply):
    """Test device goes into STANDBY when initialised"""
    power_supply.Init()
    assert power_supply.state() == tango.DevState.STANDBY


def test_turn_on(power_supply):
    """Test device turns on when requested"""
    power_supply.Init()
    assert power_supply.state() != tango.DevState.ON
    power_supply.current = 5.0
    power_supply.turn_on()
    assert power_supply.state() == tango.DevState.ON


def test_turn_off(power_supply):
    """Test device turns off when requested"""
    power_supply.Init()
    assert power_supply.state() != tango.DevState.OFF
    power_supply.turn_off()
    assert power_supply.state() == tango.DevState.OFF


def test_current_is_zero_at_init(power_supply):
    """Test device sets current to 0 when initialised"""
    power_supply.current = 5
    assert power_supply.current != 0
    power_supply.Init()
    assert power_supply.current == 0


def set_current(power_supply):
    """Test device sets current on request"""
    power_supply.current = 5.0
    assert power_supply.current == 5.0
    power_supply.current = 3.0
    assert power_supply.current == 3.0
