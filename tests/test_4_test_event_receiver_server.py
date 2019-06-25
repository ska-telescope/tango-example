# -*- coding: utf-8 -*-
"""
Some simple unit tests of the PowerSupply device, exercising the device from
another host using a DeviceProxy.
"""
import pytest
import tango
import time

@pytest.fixture
def event_receiver():
    """Create DeviceProxy for tests"""
    database = tango.Database()
    instance_list = database.get_device_exported_for_class('EventReceiver')
    for instance in instance_list.value_string:
        try:
            return tango.DeviceProxy(instance)
        except tango.DevFailed:
            continue


def test_event_receiver_is_alive(event_receiver):
    """Sanity check: test device on remote host is responsive"""
    try:
        event_receiver.ping()
    except tango.ConnectionFailed:
        pytest.fail('Could not contact event_receiver')

def test_event_received(event_receiver):
    """Test device sets current on request"""
    time.sleep(30)
    assert event_receiver.read_attribute("EventReceived").value == True
