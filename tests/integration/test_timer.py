# -*- coding: utf-8 -*-
"""
Some simple unit tests of the Tabata device, exercising the device from
the same host as the tests by using a DeviceTestContext.
"""
import logging
import time

import pytest
from tango import DevState

from ska_tango_examples.counter.Counter import Counter
from ska_tango_examples.DevFactory import DevFactory
from ska_tango_examples.teams.Timer import Timer

TIMEOUT = 70


@pytest.fixture()
def devices_to_load():
    return (
        {
            "class": Counter,
            "devices": [
                {"name": "test/counter/minutes"},
                {"name": "test/counter/seconds"},
            ],
        },
        {
            "class": Timer,
            "devices": [
                {
                    "name": "test/timer/1",
                    "properties": {"sleep_time": 0.05},
                },
            ],
        },
    )


def setup_timer(proxy):
    proxy.start_seconds = 5
    proxy.start_minutes = 1


def wait_for_events(proxy):
    dev_states = []
    start_time = time.time()
    dev_factory = DevFactory()
    minCounter = dev_factory.get_device("test/counter/minutes")
    ssCounter = dev_factory.get_device("test/counter/seconds")
    lastValuemin, lastValuesec = minCounter.value, ssCounter.value
    logging.info("%s:%s", lastValuemin, lastValuesec)
    while proxy.State() == DevState.RUNNING or proxy.State() == DevState.ALARM:
        dev_state = proxy.state()
        if dev_state not in dev_states:
            logging.info("State %s", dev_state)
            dev_states.append(dev_state)
        elapsed_time = time.time() - start_time
        if elapsed_time > TIMEOUT:
            pytest.fail("Timeout occurred while executing the test")
        # to avoid the segmentation fault in simulation mode,
        # tests must run in less than 10ss
        # https://gitlab.com/tango-controls/cppTango/-/issues/843
        tmpValuemin, tmpValuesec = minCounter.value, ssCounter.value
        if not (
            (tmpValuemin == lastValuemin) and (tmpValuesec == lastValuesec)
        ):
            logging.info("%s:%s", tmpValuemin, tmpValuesec)
            lastValuemin, lastValuesec = tmpValuemin, tmpValuesec

        time.sleep(0.001)
    assert proxy.state() == DevState.OFF
    assert DevState.ALARM in dev_states


def test_timer(tango_context):
    logging.info("%s", tango_context)
    dev_factory = DevFactory()
    proxy = dev_factory.get_device("test/timer/1")
    setup_timer(proxy)
    proxy.ResetCounters()
    proxy.Start()
    with pytest.raises(Exception):
        proxy.Start()
    assert proxy.State() == DevState.RUNNING
    wait_for_events(proxy)
    assert proxy.State() == DevState.OFF
