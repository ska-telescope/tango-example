# pylint: disable=redefined-outer-name
# -*- coding: utf-8 -*-
"""
Some simple unit tests of the PowerSupply device, exercising the device from
another host using a DeviceProxy.
"""
import logging

import pytest
import tango

from ska_tango_examples.basic_example.Motor import Motor
from ska_tango_examples.basic_example.powersupply import PowerSupply
from ska_tango_examples.DevFactory import DevFactory


@pytest.fixture()
def devices_to_load():
    return (
        {
            "class": Motor,
            "devices": [
                {
                    "name": "test/motor/1",
                },
            ],
        },
        {
            "class": PowerSupply,
            "devices": [
                {
                    "name": "test/powersupply/1",
                },
            ],
        },
    )


@pytest.fixture
def motor(tango_context):
    """Create DeviceProxy for tests"""
    logging.info("%s", tango_context)
    dev_factory = DevFactory()
    return dev_factory.get_device("test/motor/1")


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
