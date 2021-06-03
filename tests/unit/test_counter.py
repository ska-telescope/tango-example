# -*- coding: utf-8 -*-
"""
Some simple unit tests of the Counter device, exercising the device from
the same host as the tests by using a DeviceTestContext.
"""
from tango.test_utils import DeviceTestContext

from ska_tango_examples.counter.Counter import Counter


def test_init():
    with DeviceTestContext(Counter) as proxy:
        proxy.Init()
        print(proxy.value)
        assert proxy.value == 0


def test_increment():
    with DeviceTestContext(Counter) as proxy:
        proxy.Init()
        value_before_inc = proxy.value
        proxy.increment()
        assert value_before_inc == proxy.value - 1


def test_decrement():
    with DeviceTestContext(Counter) as proxy:
        proxy.Init()
        value_before_inc = proxy.value
        proxy.decrement()
        assert value_before_inc == proxy.value + 1


def test_reset():
    with DeviceTestContext(Counter) as proxy:
        proxy.Init()
        proxy.CounterReset(1)
        assert proxy.value == 1
