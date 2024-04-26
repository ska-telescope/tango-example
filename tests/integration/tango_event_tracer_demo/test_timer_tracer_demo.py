# -*- coding: utf-8 -*-
"""Refactoring of some simple unit tests of the Tabata device, 
using ::class::`TangoEventTracer` to handle the events.
"""
import logging
import time

import pytest
from tango import DevState
from assertpy import assert_that

from ska_tango_examples.counter.Counter import Counter
from ska_tango_examples.DevFactory import DevFactory
from ska_tango_examples.teams.Timer import Timer

from ska_tango_examples.tango_event_tracer import TangoEventTracer

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


def test_tracer_on_timer(tango_context):

    logging.info("%s", tango_context)
    # setup the SUT (timer)
    dev_factory = DevFactory()
    sut = dev_factory.get_device("test/timer/1")
    setup_timer(sut)
    
    tracer = TangoEventTracer()
    sut.poll_attribute("State", 50)
    tracer.subscribe_to_device("test/timer/1", "State")

    sut.ResetCounters()
    sut.Start()

    # assert that the sut passed through the RUNNING state
    query_running = tracer.query_events(lambda e: 
                        e["device"].dev_name() == sut
                        and "test/timer/1/state" in e["attribute"] 
                        and e["current_value"] == DevState.RUNNING, 
                        timeout=5)
    logging.info("Tracer status %s", tracer.events)
    assert_that(
        query_running
    ).described_as(
        f"The SUT should have reached the RUNNING state"
    ).is_true()

    # assert that the sut passed through the ALARM state
    query_alarm = tracer.query_events(lambda e: 
                        e["device"].dev_name() == sut
                        and "test/timer/1/state" in e["attribute"].name 
                        and e["current_value"] == DevState.ALARM, 
                        timeout=TIMEOUT)
    logging.info("Tracer status %s", tracer.events)
    assert_that(
        query_alarm
    ).described_as(
        f"The SUT should have reached the ALARM state before {TIMEOUT} seconds"
    ).is_true()

    # assert that the sut passed through the OFF state
    query_off = tracer.query_events(lambda e:
                        e["device"].dev_name() == sut
                        and "test/timer/1/state" in e["attribute"]
                        and e["current_value"] == DevState.OFF, 
                        timeout=5)
    assert_that(
        query_off
    ).described_as(
        f"The SUT should have reached the OFF state before {TIMEOUT} seconds"
    ).is_true()
    logging.info("Tracer status %s", tracer.events)
    

    #TODO: integrate the logger too to log automatically
    # the minutes and seconds counter values (i.e. fixing a callback 
    # when a predicate is met)

    # TODO: verify order of events
