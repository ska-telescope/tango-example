# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name
"""
Some simple unit tests of the PowerSupply device, exercising the device from
another host using a DeviceProxy.
"""
import time
from time import sleep

import pytest
import tango
import logging


@pytest.fixture
def event_receiver():
    """Create DeviceProxy for tests"""
    database = tango.Database()
    instance_list = database.get_device_exported_for_class("EventReceiver")
    for instance in instance_list.value_string:
        timeSleep = 30
        for _ in range(10):
            try:
                return tango.DeviceProxy(instance)
            except Exception as ex:
                logging.info(
                    "Could not connect to the "
                    "event_receiver DeviceProxy. %s %s %s",
                    "Retry after ",
                    str(timeSleep),
                    " seconds.",
                )
                logging.info(str(ex))
                sleep(timeSleep)

    pytest.fail("Could not contact the event_receiver device")


def test_event_receiver_is_alive(event_receiver):
    """Sanity check: test device on remote host is responsive"""
    try:
        event_receiver.ping()
    except tango.ConnectionFailed:
        pytest.fail("Could not contact event_receiver")


def test_event_received(event_receiver):
    """Test device sets current on request"""
    time.sleep(3)
    assert event_receiver.read_attribute("EventReceived").value is True


def test_type_spectrum(event_receiver):
    """Test device turns on when requested"""
    assert not isinstance(
        event_receiver.read_attribute("TestSpectrumType").value, tuple
    )
