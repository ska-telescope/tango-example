# -*- coding: utf-8 -*-
"""
Some simple unit tests of the Counter device, exercising the device from
the same host as the tests by using a DeviceTestContext.
"""
from tango.test_utils import DeviceTestContext

from ska_tango_examples.counter.PollingCounter import PollingCounter


def test_init():
    with DeviceTestContext(PollingCounter) as proxy:
        assert proxy.value == 0


def test_increment():
    with DeviceTestContext(PollingCounter) as proxy:
        value_before_inc = proxy.value
        proxy.increment()
        assert value_before_inc == proxy.value - 1


def test_decrement():
    with DeviceTestContext(PollingCounter) as proxy:
        value_before_inc = proxy.value
        proxy.decrement()
        assert value_before_inc == proxy.value + 1


def test_reset():
    with DeviceTestContext(PollingCounter) as proxy:
        proxy.CounterReset(0)
        assert proxy.value == 0
