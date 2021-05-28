# pylint: disable=redefined-outer-name
# -*- coding: utf-8 -*-
"""
Some simple unit tests of the PowerSupply device, exercising the device from
another host using a DeviceProxy.
"""
import logging
from time import sleep

import pytest
import tango


@pytest.fixture
def motor():
    """Create DeviceProxy for tests"""
    database = tango.Database()
    instance_list = database.get_device_exported_for_class("Motor")
    for instance in instance_list.value_string:
        timeSleep = 30
        for _ in range(10):
            try:
                return tango.DeviceProxy(instance)
            except Exception as ex:
                logging.info(
                    "Could not connect to the motor DeviceProxy."
                    "Retry after %s ss. Exception %s",
                    str(timeSleep),
                    str(ex),
                )
                sleep(timeSleep)

    pytest.fail("Could not contact the motor device")


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
