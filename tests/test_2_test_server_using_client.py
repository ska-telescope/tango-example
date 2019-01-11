# -*- coding: utf-8 -*-
import pytest
import tango


@pytest.fixture
def power_supply():
    db = tango.Database()
    instance_list = db.get_device_exported_for_class('PowerSupply')
    for instance in instance_list.value_string:
        try:
            return tango.DeviceProxy(instance)
        except Exception:
            continue


def test_power_supply_is_alive(power_supply):
    try:
        power_supply.ping()
    except tango.ConnectionFailed:
        pytest.fail('Could not contact power_supply')


def test_init(power_supply):
    power_supply.Init()
    assert power_supply.state() == tango.DevState.STANDBY


def test_turn_on(power_supply):
    power_supply.Init()
    assert power_supply.state() != tango.DevState.ON
    power_supply.current = 5.0
    power_supply.TurnOn()
    assert power_supply.state() == tango.DevState.ON


def test_turn_off(power_supply):
    power_supply.Init()
    assert power_supply.state() != tango.DevState.OFF
    power_supply.TurnOff()
    assert power_supply.state() == tango.DevState.OFF


def test_current_is_zero_at_init(power_supply):
    power_supply.current = 5
    assert power_supply.current != 0
    power_supply.Init()
    assert power_supply.current == 0


def set_current(power_supply):
    power_supply.current = 5.0
    assert power_supply.current == 5.0
    power_supply.current = 3.0
    assert power_supply.current == 3.0
