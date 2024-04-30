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

TIMEOUT = 11
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

    logging.info("%s", tango_context)
    # setup the SUT (timer)
    dev_factory = DevFactory()
    sut = dev_factory.get_device("test/timer/1")
    setup_timer(sut)
    tracer = TangoEventTracer()
    tracer.subscribe_to_device(
        "test/timer/1", "State", dev_factory=dev_factory
    )

    sut.ResetCounters()

    start_time = time.time()
    sut.Start()

    # assert that the sut passed through the RUNNING state
    query_running = tracer.query_events(
        lambda e: e.device_name == sut.dev_name()
        and e.attribute_name == "state"
        and e.current_value is DevState.RUNNING,
        timeout=5,
    )

    logging.info(
        "Running query done! Tracer status %s",
        tracer.query_events(
            lambda _: True,
        ),
    )

    # logging.info("Expected devicename %s (type %s)",
    #              sut, type(sut))
    # logging.info("Expected state %s (type %s)",
    #              DevState.RUNNING,
    #              type(DevState.RUNNING))
    # logging.info("Actual devicename %s (type %s)",
    #              tracer.events[0].device_name,
    #              type(tracer.events[0].device_name)
    # logging.info("Actual state %s (type %s)",
    #              tracer.events[0].current_value,
    #              type(tracer.events[0].current_value))
    # logging.info("Actual attribute %s (type %s)",
    #              tracer.events[0].attribute,
    #              type(tracer.events[0].attribute))

    assert_that(query_running).described_as(
        "The SUT should have reached the RUNNING state"
    ).is_length(1)

    # assert that the sut passed through the ALARM state
    query_alarm = tracer.query_events(
        lambda e: e.device_name == sut.dev_name()
        and e.attribute_name == "state"
        and e.current_value is DevState.ALARM,
        timeout=TIMEOUT,
    )
    logging.info(
        "Alarm query done! Tracer status %s",
        tracer.query_events(
            lambda _: True,
        ),
    )
    assert_that(query_alarm).described_as(
        f"The SUT should have reached the ALARM state before {TIMEOUT} seconds"
    ).is_length(1)

    logging.info("Elapsed time: %s", time.time() - start_time)

    # assert that the sut passed through the OFF state
    query_off = tracer.query_events(
        lambda e: e.device_name == sut.dev_name()
        and e.attribute_name == "state"
        and e.current_value is DevState.OFF,
        timeout=None,
    )
    assert_that(query_off).described_as(
        f"The SUT should have reached the OFF state before {TIMEOUT} seconds"
    ).is_length(1)

    logging.info(
        "Off query done! Tracer status %s",
        tracer.query_events(
            lambda _: True,
        ),
    )

    elapsed_time = time.time() - start_time
    sleeping_time = MIN_EXECUTION_TIME - elapsed_time
    logging.info("Elapsed time: %s (sleeping %s)", elapsed_time, sleeping_time)

    # NOTE: empirically, this test must run in more than 2 seconds
    # to avoid the segmentation fault in simulation mode (TODO: why?)
    if sleeping_time > 0:
        time.sleep(sleeping_time)

    # TODO: integrate the logger too to log automatically
    # the minutes and seconds counter values (i.e. fixing a callback
    # when a predicate is met)

    # TODO: verify order of events
