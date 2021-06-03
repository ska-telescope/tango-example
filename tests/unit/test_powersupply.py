# -*- coding: utf-8 -*-
"""
Some simple unit tests of the PowerSupply device, exercising the device from
the same host as the tests by using a DeviceTestContext.
"""
from tango import DevState
from tango.test_utils import DeviceTestContext

from ska_tango_examples.basic_example.powersupply import PowerSupply


def test_init():
    """Test device goes into STANDBY when initialised"""
    with DeviceTestContext(PowerSupply) as proxy:
        proxy.Init()
        assert proxy.state() == DevState.STANDBY


def test_turn_on():
    """Test device turns on when requested"""
    with DeviceTestContext(PowerSupply) as proxy:
        proxy.Init()
        assert proxy.state() != DevState.ON
        proxy.current = 5.0
        proxy.turn_on()
        assert proxy.state() == DevState.ON


def test_turn_off():
    """Test device turns off when requested"""
    with DeviceTestContext(PowerSupply) as proxy:
        proxy.Init()
        assert proxy.state() != DevState.OFF
        proxy.turn_off()
        assert proxy.state() == DevState.OFF


def test_current_is_zero_at_init():
    """Test device sets current to 0 when initialised"""
    with DeviceTestContext(PowerSupply) as proxy:
        proxy.Init()
        proxy.current = 5
        assert proxy.current != 0
        proxy.Init()
        assert proxy.current == 0


def test_set_current():
    """Test device sets current on request"""
    with DeviceTestContext(PowerSupply) as proxy:
        proxy.current = 5.0
        assert proxy.current == 5.0
        proxy.current = 3.0
        assert proxy.current == 3.0
