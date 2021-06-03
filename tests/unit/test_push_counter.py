# -*- coding: utf-8 -*-
"""
Some simple unit tests of the Counter device, exercising the device from
the same host as the tests by using a DeviceTestContext.
"""
from unittest.mock import patch

from tango.test_utils import DeviceTestContext

from ska_tango_examples.counter.PushCounter import PushCounter


def test_init():
    with DeviceTestContext(PushCounter) as proxy:
        assert proxy.value == 0


@patch("tango.server.Device.push_change_event")
def test_increment(push_change_event):
    with DeviceTestContext(PushCounter) as proxy:
        proxy.Init()
        value_before_inc = proxy.value
        proxy.increment()
        push_change_event.assert_called()
        assert value_before_inc == proxy.value - 1


@patch("tango.server.Device.push_change_event")
def test_decrement(push_change_event):
    with DeviceTestContext(PushCounter) as proxy:
        value_before_inc = proxy.value
        proxy.decrement()
        push_change_event.assert_called()
        assert value_before_inc == proxy.value + 1


@patch("tango.server.Device.push_change_event")
def test_reset(push_change_event):
    with DeviceTestContext(PushCounter) as proxy:
        proxy.Init()
        proxy.CounterReset(1)
        push_change_event.assert_called()
        assert proxy.value == 1
