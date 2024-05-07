# -*- coding: utf-8 -*-
"""Refactoring of some simple unit tests of the Tabata device,
using ::class::`TangoEventTracer` to handle the events.
"""

import logging

import pytest
from assertpy import add_extension, assert_that
from tango import DevState

from ska_tango_examples.counter.Counter import Counter
from ska_tango_examples.DevFactory import DevFactory
from ska_tango_examples.tabata.RunningState import RunningState
from ska_tango_examples.tabata.Tabata import Tabata
from ska_tango_examples.tango_event_tracer.predicates_and_assertions.event_assertions import (
    exists_event_within_timeout,
)
from ska_tango_examples.tango_event_tracer.tango_event_logger import (
    TangoEventLogger,
)
from ska_tango_examples.tango_event_tracer.tango_event_tracer import (
    TangoEventTracer,
)

# Add the custom extension to assertpy
add_extension(exists_event_within_timeout)

TIMEOUT = 10


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


def assert_event_after(tracer, device_name, attribute_name, value, after):
    """Assert an event with the given params is received after the given event."""
    query = tracer.query_events(
        lambda e: e.device_name == device_name
        and e.attribute_name == attribute_name
        and e.attribute_value == value
        and e.reception_time > after.reception_time,
        timeout=TIMEOUT,
    )
    assert_that(query).described_as(
        f"{attribute_name} {value} not reached"
    ).is_length(1)
    return query[0]


@pytest.mark.post_deployment
def test_sync_tabata_using_tracer(tango_context):
    """The tabata device pass through the correct state sequence when started.

    This is a refactored version of the ::function::`test_sync_tabata`
    test, which uses the ::class::`TangoEventTracer` to capture the sequence
    of events instead of polling the device state with a while loop.

    This test uses also the ::class::`TangoEventLogger` to log the same events
    that are being captured by the tracer.
    """
    logging.info("%s", tango_context)
    dev_factory = DevFactory()

    proxy = dev_factory.get_device("test/tabata/1")
    setup_tabata(proxy)

    # ##################################################
    # setup the tracer and the logger

    tracer = TangoEventTracer()
    tracer.subscribe_to_device(
        "test/tabata/1", "state", dev_factory=dev_factory.get_device
    )
    tracer.subscribe_to_device(
        "test/tabata/1", "running_state", dev_factory=dev_factory.get_device
    )
    logger = TangoEventLogger()
    logger.log_events_from_device(
        "test/tabata/1", "state", dev_factory=dev_factory.get_device
    )
    logger.log_events_from_device(
        "test/tabata/1", "running_state", dev_factory=dev_factory.get_device
    )

    # ##################################################
    # Start the device
    # (tracer is already capturing events)

    proxy.ResetCounters()
    proxy.Start()
    with pytest.raises(Exception):
        proxy.Start()

    # ##################################################
    # Verify that the device passed through the ON state

    query_on = tracer.query_events(
        lambda e: e.device_name == proxy.dev_name()
        and e.attribute_name == "state"
        and e.attribute_value is DevState.ON,
        timeout=TIMEOUT,
    )
    assert_that(query_on).described_as("ON state not reached").is_not_empty()

    # ##################################################
    # Verify that the device passed through the PREPARE,
    # WORK, and REST states in that order

    prepare_event = assert_event_after(
        tracer,
        proxy.dev_name(),
        "running_state",
        RunningState.PREPARE,
        query_on[0],
    )

    work_event = assert_event_after(
        tracer,
        proxy.dev_name(),
        "running_state",
        RunningState.WORK,
        prepare_event,
    )

    rest_event = assert_event_after(
        tracer,
        proxy.dev_name(),
        "running_state",
        RunningState.REST,
        work_event,
    )

    # ##################################################
    # Verify that the device passed through the OFF state

    query_off = tracer.query_events(
        lambda e: e.device_name == proxy.dev_name()
        and e.attribute_name == "state"
        and e.attribute_value is DevState.OFF
        and e.reception_time > rest_event.reception_time,
        timeout=TIMEOUT,
    )

    assert_that(query_off).described_as("OFF state not reached").is_not_empty()


@pytest.mark.post_deployment
def test_sync_tabata_using_tracer_and_customassetions(tango_context):
    """The tabata device pass through the correct state sequence when started.

    This is a refactored version of the ::function::`test_sync_tabata`
    using ::class::`TangoEventTracer` to collect the events and custom
    assertions (::mod::`event_assertions`) for simplified event verification.

    This test uses also the ::class::`TangoEventLogger` to log the same events
    that are being captured by the tracer.
    """
    logging.info("%s", tango_context)
    dev_factory = DevFactory()

    proxy = dev_factory.get_device("test/tabata/1")
    setup_tabata(proxy)

    # ##################################################
    # setup the tracer and the logger

    tracer = TangoEventTracer()
    tracer.subscribe_to_device(
        "test/tabata/1", "state", dev_factory=dev_factory.get_device
    )
    tracer.subscribe_to_device(
        "test/tabata/1", "running_state", dev_factory=dev_factory.get_device
    )
    logger = TangoEventLogger()
    logger.log_events_from_device(
        "test/tabata/1", "state", dev_factory=dev_factory.get_device
    )
    logger.log_events_from_device(
        "test/tabata/1", "running_state", dev_factory=dev_factory.get_device
    )

    # ##################################################
    # Start the device
    # (tracer is already capturing events)

    proxy.ResetCounters()
    proxy.Start()
    with pytest.raises(Exception):
        proxy.Start()

    # ##################################################
    # Verify that the device passed through the ON state

    assert_that(tracer).described_as(
        "ON state not reached"
    ).exists_event_within_timeout(
        device_name=proxy.dev_name(),
        attribute_name="state",
        attribute_value=DevState.ON,
        timeout=TIMEOUT,
    )

    # ##################################################
    # Verify that the device passed through the PREPARE,
    # WORK, and REST states in that order

    assert_that(tracer).described_as(
        "PREPARE state not reached"
    ).exists_event_within_timeout(
        device_name=proxy.dev_name(),
        attribute_name="running_state",
        attribute_value=RunningState.PREPARE,
        timeout=TIMEOUT,
    )

    assert_that(tracer).described_as(
        "WORK state not reached"
    ).exists_event_within_timeout(
        device_name=proxy.dev_name(),
        attribute_name="running_state",
        attribute_value=RunningState.WORK,
        previous_value=RunningState.PREPARE,
        timeout=TIMEOUT,
    )

    assert_that(tracer).described_as(
        "REST state not reached"
    ).exists_event_within_timeout(
        device_name=proxy.dev_name(),
        attribute_name="running_state",
        attribute_value=RunningState.REST,
        previous_value=RunningState.WORK,
        timeout=TIMEOUT,
    )

    # ##################################################
    # Verify that the device passed through the OFF state

    assert_that(tracer).described_as(
        "OFF state not reached"
    ).exists_event_within_timeout(
        device_name=proxy.dev_name(),
        attribute_name="state",
        attribute_value=DevState.OFF,
        previous_value=DevState.ON,
        timeout=TIMEOUT,
    )
