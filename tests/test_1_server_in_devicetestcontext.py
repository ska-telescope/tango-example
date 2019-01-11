# -*- coding: utf-8 -*-
from tango import DevState
from tango.test_utils import DeviceTestContext

from powersupply.powersupply import PowerSupply


def test_init():
    with DeviceTestContext(PowerSupply, process=True) as proxy:
        proxy.Init()
        assert proxy.state() == DevState.STANDBY


def test_turn_on():
    with DeviceTestContext(PowerSupply, process=True) as proxy:
        proxy.Init()
        assert proxy.state() != DevState.ON
        proxy.current = 5.0
        proxy.TurnOn()
        assert proxy.state() == DevState.ON


def test_turn_off():
    with DeviceTestContext(PowerSupply, process=True) as proxy:
        proxy.Init()
        assert proxy.state() != DevState.OFF
        proxy.TurnOff()
        assert proxy.state() == DevState.OFF


def test_current_is_zero_at_init():
    with DeviceTestContext(PowerSupply, process=True) as proxy:
        proxy.Init()
        proxy.current = 5
        assert proxy.current != 0
        proxy.Init()
        assert proxy.current == 0


def test_set_current():
    with DeviceTestContext(PowerSupply, process=True) as proxy:
        proxy.current = 5.0
        assert proxy.current == 5.0
        proxy.current = 3.0
        assert proxy.current == 3.0
