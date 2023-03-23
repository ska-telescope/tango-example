# -*- coding: utf-8 -*-
# pylint: disable=redefined-outer-name
"""
Some simple unit tests of the Counter device, exercising the device from
the same host as the tests by using a DeviceTestContext.
"""
import logging
import time

import pytest
import tango
from tango.test_utils import DeviceTestContext

from ska_tango_examples.counter.AsyncCounter import AsyncCounter


@pytest.fixture
def counter(request):
    """Create DeviceProxy for tests"""
    true_context = request.config.getoption("--true-context")
    if not true_context:
        with DeviceTestContext(AsyncCounter) as proxy:
            yield proxy
    else:
        database = tango.Database()
        instance_list = database.get_device_exported_for_class("AsyncCounter")
        for instance in instance_list.value_string:
            yield tango.DeviceProxy(instance)
            break


def test_init(counter):
    counter.Init()
    print(counter.value)
    assert counter.value == 0


def test_increment(counter):
    counter.Init()
    value_before_inc = counter.value
    counter.increment()
    assert value_before_inc == counter.value - 1


def test_decrement(counter):
    counter.Init()
    value_before_inc = counter.value
    counter.decrement()
    assert value_before_inc == counter.value + 1


def test_reset(counter):
    counter.Init()
    counter.CounterReset(1)
    assert counter.value == 1


@pytest.mark.post_deployment
def test_polled_value():
    pytest.count = 0
    counter = tango.DeviceProxy("test/counter/prepare")

    def count_events(evt):
        logging.info("%s", evt)
        pytest.count += 1

    event_id = counter.subscribe_event(
        "polled_value",
        tango.EventType.CHANGE_EVENT,
        count_events,
    )
    counter.increment()
    time.sleep(1)
    counter.increment()
    time.sleep(1)
    counter.increment()
    time.sleep(1)
    assert pytest.count >= 4  # 3 changes, 1 subscription

    counter.unsubscribe_event(event_id)
