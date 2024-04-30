# -*- coding: utf-8 -*-
"""Refactoring of some simple unit tests of the Tabata device,
using ::class::`TangoEventTracer` to handle the events.
"""
import logging
import time

import pytest
from assertpy import assert_that
from tango import DevState

from ska_tango_examples.counter.Counter import Counter
from ska_tango_examples.DevFactory import DevFactory
from ska_tango_examples.tango_event_tracer import TangoEventTracer
from ska_tango_examples.teams.Timer import Timer

LONG_TIMEOUT = 11
SHORT_TIMEOUT = 5

MIN_EXECUTION_TIME = 2


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


def test_tracer_on_timer(tango_context):
    """Refactor ::method::`test_timer` to use the ::class::`TangoEventTracer`."""

    logging.info("%s", tango_context)
    # setup the SUT (timer)
    dev_factory = DevFactory()
    sut = dev_factory.get_device("test/timer/1")
    setup_timer(sut)
    tracer = TangoEventTracer()
    tracer.subscribe_to_device(
        "test/timer/1", "State", dev_factory=dev_factory.get_device
    )

    sut.ResetCounters()
    start_time = time.time()
    sut.Start()

    # #########################################################
    # assert that the sut passed through the RUNNING state

    query_running = tracer.query_events(
        lambda e: e.device_name == sut.dev_name()
        and e.attribute_name == "state"
        and e.current_value is DevState.RUNNING,
        timeout=SHORT_TIMEOUT,
    )
    logging.info("Running query done! Tracer status %s", tracer.events)
    assert_that(query_running).described_as(
        "The SUT should have reached the RUNNING state before "
        f"{SHORT_TIMEOUT} seconds"
    ).is_length(1)

    # #########################################################
    # assert that the sut passed through the ALARM state

    query_alarm = tracer.query_events(
        lambda e: e.device_name == sut.dev_name()
        and e.attribute_name == "state"
        and e.current_value is DevState.ALARM,
        timeout=LONG_TIMEOUT,
    )
    logging.info("Alarm query done! Tracer status %s", tracer.events)
    assert_that(query_alarm).described_as(
        "The SUT should have reached the ALARM state before "
        f"{LONG_TIMEOUT} seconds"
    ).is_length(1)
    assert_that(query_alarm[0].reception_time).described_as(
        "The ALARM event should have been received after the RUNNING event"
    ).is_greater_than(query_running[0].reception_time)

    # #########################################################
    # assert that the sut passed through the OFF state

    query_off = tracer.query_events(
        lambda e: e.device_name == sut.dev_name()
        and e.attribute_name == "state"
        and e.current_value is DevState.OFF
        # I want to check that the OFF state is reached after the ALARM state
        # (to distinguish this from the initial OFF state of the device)
        and e.reception_time > query_alarm[0].reception_time,
        timeout=SHORT_TIMEOUT,
    )
    logging.info("Off query done! Tracer status %s", tracer.events)
    assert_that(query_off).described_as(
        "The SUT should have reached the OFF state before "
        f"{SHORT_TIMEOUT} seconds"
    ).is_length(1)

    # #########################################################
    # end of the test

    elapsed_time = time.time() - start_time
    sleeping_time = MIN_EXECUTION_TIME - elapsed_time
    logging.info("Elapsed time: %s (sleeping %s)", elapsed_time, sleeping_time)

    # NOTE: empirically, this test must run in more than 2 seconds
    # to avoid the segmentation fault in simulation mode (TODO: why?)
    if sleeping_time > 0:
        time.sleep(sleeping_time)
