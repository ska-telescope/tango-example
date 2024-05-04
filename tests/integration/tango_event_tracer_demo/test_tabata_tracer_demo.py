# -*- coding: utf-8 -*-
"""Refactoring of some simple unit tests of the Tabata device,
using ::class::`TangoEventTracer` to handle the events.
"""

import logging
import time

import pytest
import tango
from tango import DevState
from assertpy import assert_that

from ska_tango_examples.counter.Counter import Counter
from ska_tango_examples.DevFactory import DevFactory
from ska_tango_examples.tabata.RunningState import RunningState
from ska_tango_examples.tabata.Tabata import Tabata
from ska_tango_examples.tango_event_tracer.tango_event_tracer import TangoEventTracer

TIMEOUT = 60


@pytest.fixture()
def devices_to_load():
    return (
        {
            "class": Counter,
            "devices": [
                {"name": "test/counter/prepare"},
                {"name": "test/counter/work"},
                {"name": "test/counter/rest"},
                {"name": "test/counter/cycles"},
                {"name": "test/counter/tabatas"},
            ],
        },
        {
            "class": Tabata,
            "devices": [
                {
                    "name": "test/tabata/1",
                    "properties": {"sleep_time": 0.01},
                },
            ],
        },
    )


def setup_tabata(proxy):
    proxy.prepare = 5
    proxy.work = 5
    proxy.rest = 5
    proxy.cycles = 1
    proxy.tabatas = 1


def wait_for_events(proxy):
    dev_factory = DevFactory()
    tabatasCounter = dev_factory.get_device("test/counter/tabatas")
    dev_states = []
    run_states = []
    start_time = time.time()
    while not tabatasCounter.value <= 0 or proxy.State() == DevState.ON:
        dev_state = proxy.state()
        run_state = proxy.running_state
        if dev_state not in dev_states:
            logging.info("Device: %s %s", dev_state, run_state)
            dev_states.append(dev_state)
        if run_state not in run_states:
            logging.info("Device: %s %s", dev_state, run_state)
            run_states.append(run_state)
        elapsed_time = time.time() - start_time
        if elapsed_time > TIMEOUT:
            pytest.fail("Timeout occurred while executing the test")
        # to avoid the segmentation fault in simulation mode,
        # tests must run in less than 10ss
        # https://gitlab.com/tango-controls/cppTango/-/issues/843
        time.sleep(0.01)
    assert proxy.state() == DevState.OFF
    assert DevState.ON in dev_states
    assert RunningState.PREPARE in run_states
    assert RunningState.WORK in run_states
    assert RunningState.REST in run_states


def assert_event_after(tracer, device_name, attribute_name, value, after):
    """Assert an event with the given params is received after the given event."""
    query = tracer.query_events(
        lambda e: e.device_name == device_name
        and e.attribute_name == attribute_name
        and e.current_value == value
        and e.reception_time > after.reception_time,
        timeout=TIMEOUT,
    )
    assert_that(query).described_as(
        f"{attribute_name} {value} not reached"
    ).is_length(1)
    return query[0]


@pytest.mark.post_deployment
def test_sync_tabata_using_tracer(tango_context):
    logging.info("%s", tango_context)
    dev_factory = DevFactory()

    proxy = dev_factory.get_device("test/tabata/1")
    setup_tabata(proxy)


    tracer = TangoEventTracer()
    tracer.subscribe_to_device(
        "test/tabata/1", "state", 
        dev_factory=dev_factory.get_device
    )
    tracer.subscribe_to_device(
        "test/tabata/1", "running_state", 
        dev_factory=dev_factory.get_device
    )


    proxy.ResetCounters()
    proxy.Start()
    with pytest.raises(Exception):
        proxy.Start()

    # ##################################################
    # Verify that the device passed through the ON state

    query_on = tracer.query_events(
        lambda e: e.device_name == proxy.dev_name()
        and e.attribute_name == "state"
        and e.current_value is DevState.ON,
        timeout=TIMEOUT,
    )
    assert_that(query_on).described_as(
        "ON state not reached"
    ).is_not_empty()


    # ##################################################
    # Verify that the device passed through the PREPARE, 
    # WORK, and REST states in that order

    prepare_event = assert_event_after(
        tracer, proxy.dev_name(), 
        "running_state", 
        RunningState.PREPARE, 
        query_on[0]
    )

    work_event = assert_event_after(
        tracer, proxy.dev_name(), 
        "running_state", 
        RunningState.WORK, 
        prepare_event
    )

    rest_event = assert_event_after(
        tracer, proxy.dev_name(), 
        "running_state", 
        RunningState.REST, 
        work_event
    )

    # ##################################################
    # Verify that the device passed through the OFF state

    query_off = tracer.query_events(
        lambda e: e.device_name == proxy.dev_name()
        and e.attribute_name == "state"
        and e.current_value is DevState.OFF
        and e.reception_time > rest_event.reception_time,
        timeout=TIMEOUT,
    )

    assert_that(query_off).described_as(
        "OFF state not reached"
    ).is_not_empty()



