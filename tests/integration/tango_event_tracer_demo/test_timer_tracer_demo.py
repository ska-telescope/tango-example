# -*- coding: utf-8 -*-
"""Refactoring of some simple unit tests of the Timer device,
using ::class::`TangoEventTracer` to handle the events.
"""


import logging
import time

import pytest
from assertpy import add_extension, assert_that
from tango import DevState

from ska_tango_examples.counter.Counter import Counter
from ska_tango_examples.DevFactory import DevFactory
from ska_tango_examples.tango_event_tracer import TangoEventTracer
from ska_tango_examples.tango_event_tracer.event_assertions import (
    exists_event_within_timeout,
)
from ska_tango_examples.tango_event_tracer.tango_event_logger import (
    TangoEventLogger,
)
from ska_tango_examples.teams.Timer import Timer

# Add the custom extension to assertpy
add_extension(exists_event_within_timeout)

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


def test_timer_using_tracer(tango_context):
    """The timer device passes through the RUNNING, ALARM, and OFF states.

    This is a refactor of ::method::`test_timer`
    using ::class::`TangoEventTracer` to collect the events.

    NOTE: Since this is a unit test which uses the mock environment,
    if the test doesn't reach the final state, the test may fail
    with a segmentation fault.
    """

    logging.info("%s", tango_context)
    # setup the SUT (timer)
    dev_factory = DevFactory()
    sut = dev_factory.get_device("test/timer/1")
    setup_timer(sut)

    # #########################################################
    # setup the tracer and the logger

    tracer = TangoEventTracer()
    tracer.subscribe_to_device(
        "test/timer/1", "State", dev_factory=dev_factory.get_device
    )

    # #########################################################
    # Run sut

    sut.ResetCounters()
    sut.Start()

    # (avoid segfaults in simulation mode)
    time.sleep(2)

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

    # end of the test


def test_timer_using_tracer_and_customassertions(tango_context):
    """The timer device passes through the RUNNING, ALARM, and OFF states.

    This is a refactored version of ::method::`test_timer`
    using ::class::`TangoEventTracer` to collect the events and custom
    assertions (::mod::`event_assertions`) for simplified event verification.

    This test uses also the ::class::`TangoEventLogger` to log the same events
    that are being captured by the tracer."""
    logging.info("%s", tango_context)
    dev_factory = DevFactory()
    sut = dev_factory.get_device("test/timer/1")
    setup_timer(sut)

    tracer = TangoEventTracer()
    tracer.subscribe_to_device(
        "test/timer/1", "State", dev_factory=dev_factory.get_device
    )
    logger = TangoEventLogger()
    logger.log_events_from_device(
        "test/timer/1", "State", dev_factory=dev_factory.get_device
    )

    sut.ResetCounters()
    sut.Start()
    time.sleep(2)  # Sleep to avoid segfaults in simulation mode

    # Verify that the device passed through the RUNNING state
    assert_that(tracer).described_as(
        "RUNNING state not reached"
    ).exists_event_within_timeout(
        device_name=sut.dev_name(),
        attribute_name="state",
        current_value=DevState.RUNNING,
        previous_value=DevState.OFF,
        timeout=SHORT_TIMEOUT,
    )

    # Verify that the device passed through the ALARM state
    assert_that(tracer).described_as(
        "ALARM state not reached"
    ).exists_event_within_timeout(
        device_name=sut.dev_name(),
        attribute_name="state",
        current_value=DevState.ALARM,
        previous_value=DevState.RUNNING,
        timeout=LONG_TIMEOUT,
    )

    # Verify that the device passed through the OFF state
    assert_that(tracer).described_as(
        "OFF state not reached"
    ).exists_event_within_timeout(
        device_name=sut.dev_name(),
        attribute_name="state",
        current_value=DevState.OFF,
        previous_value=DevState.ALARM,
        timeout=SHORT_TIMEOUT,
    )

    # end of the test


# def test_timer_segfault(tango_context):
#     logging.info("%s", tango_context)
#     dev_factory = DevFactory()
#     proxy = dev_factory.get_device("test/timer/1")
#     setup_timer(proxy)
#     proxy.ResetCounters()
#     proxy.Start()


# def test_timer_segfault_again(tango_context):
#     logging.info("%s", tango_context)
#     dev_factory = DevFactory()
#     proxy = dev_factory.get_device("test/timer/1")
#     setup_timer(proxy)
#     proxy.ResetCounters()
#     proxy.Start()

#     time.sleep(1)


# def test_timer_no_segfault(tango_context):
#     logging.info("%s", tango_context)
#     dev_factory = DevFactory()
#     proxy = dev_factory.get_device("test/timer/1")
#     setup_timer(proxy)
#     proxy.ResetCounters()
#     proxy.Start()

#     time.sleep(2)
