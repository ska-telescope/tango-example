# -*- coding: utf-8 -*-
"""
Some simple unit tests of the PowerSupply device, exercising the device from
another host using a DeviceProxy.
"""
import pytest
import tango
import time


@pytest.fixture
def training_receiver():
    """Create DeviceProxy for tests"""
    database = tango.Database()
    instance_list = database.get_device_exported_for_class('TrainingReceiver')
    for instance in instance_list.value_string:
        try:
            return tango.DeviceProxy(instance)
        except tango.DevFailed:
            continue


def test_event_received(training_receiver):
    try:
        time.sleep(3)
        res = training_receiver.read_attribute("EventReceived")
        assert res.value == True
    except tango.ConnectionFailed:
        pytest.fail('Could not contact training_receiver')

