# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name
"""
Some simple unit tests of the PowerSupply device, exercising the device from
another host using a DeviceProxy.
"""
import pytest
import tango
from tango.test_context import DeviceTestContext

from ska_tango_examples.basic_example.EventReceiver import EventReceiver


@pytest.fixture
def event_receiver(request):
    """Create DeviceProxy for tests"""
    true_context = request.config.getoption("--true-context")
    if not true_context:
        with DeviceTestContext(EventReceiver, process=True) as proxy:
            yield proxy
    else:
        database = tango.Database()
        instance_list = database.get_device_exported_for_class("EventReceiver")
        for instance in instance_list.value_string:
            yield tango.DeviceProxy(instance)
            break


def test_event_receiver_is_alive(event_receiver):
    """Sanity check: test device on remote host is responsive"""
    try:
        event_receiver.ping()
    except tango.ConnectionFailed:
        pytest.fail("Could not contact event_receiver")
