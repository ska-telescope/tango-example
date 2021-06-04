# pylint: disable=redefined-outer-name
# -*- coding: utf-8 -*-
"""
Some simple unit tests of the PowerSupply device, exercising the device from
another host using a DeviceProxy.
"""
import logging
from time import sleep
from tango.test_context import DeviceTestContext
import pytest
import tango
from ska_tango_examples.basic_example.Motor import Motor


@pytest.fixture
def motor(request):
    """Create DeviceProxy for tests"""
    true_context = request.config.getoption("--true-context")
    if not true_context:
        with DeviceTestContext(Motor) as proxy:
            yield proxy
    else:
        database = tango.Database()
        instance_list = database.get_device_exported_for_class("Motor")
        for instance in instance_list.value_string:
            yield tango.DeviceProxy(instance)
            break

def test_motor_is_alive(motor):
    """Sanity check: test device on remote host is responsive"""
    try:
        motor.ping()
    except tango.ConnectionFailed:
        pytest.fail("Could not contact motor")


def test_turn_on(motor):
    """Test device sets current on request"""
    motor.turnOn()
    assert motor.state() == tango.DevState.ON


def test_turn_off(motor):
    """Test device sets current on request"""
    motor.turnOff()
    assert motor.state() == tango.DevState.OFF


def test_start(motor):
    """Test device sets current on request"""
    motor.Start()
    assert motor.state() == tango.DevState.RUNNING
