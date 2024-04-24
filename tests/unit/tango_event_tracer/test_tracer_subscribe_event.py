"""Tests for ::class::`TangoEventTracer` to ensure events are captured.

This second set of tests focuses on ensuring that ::class::`TangoEventTracer`
can subscribe to Tango events and capture them correctly. This is done by
deploying a Tango device, subscribing to its events, triggering
those events, and checking that the events are captured correctly using
the `TangoEventTracer` class.

Those tests are complementary to the ones in
::file::`test_tango_event_tracer.py`, which cover the basic methods of the
`TangoEventTracer` class in isolation.

Those tests rely on demo device ::class::`PollingDemoDevice` and so require
::file::`test_polling_demo_device.py` to run successfully to be meaningful.
"""

import logging
import time

import pytest
from assertpy import assert_that
from tango import DeviceProxy

from ska_tango_examples.DevFactory import DevFactory
from ska_tango_examples.tango_event_tracer.polling_demo_device import (
    PollingDemoDevice,
)
from src.ska_tango_examples.tango_event_tracer.tango_event_tracer import (
    TangoEventTracer,
)


@pytest.fixture()
def devices_to_load():
    return [
        {
            "class": PollingDemoDevice,
            "devices": [
                {"name": "test/pollingdemo/1"},
            ],
        }
    ]


def test_tracer_subscribes_to_demo_device_without_exceptions(tango_context):
    """Given a Tango device, the tracer subscribe to it (without exceptions)."""
    logging.info("%s", tango_context)

    dev_factory = DevFactory()
    proxy = dev_factory.get_device("test/pollingdemo/1")
    assert hasattr(proxy, "pollable_attr")
    sut = TangoEventTracer()

    sut.subscribe_to_device("test/pollingdemo/1", "pollable_attr")

    # NOTE: first event is the initial value => check if it was captured
    assert_that(sut.events).described_as(
        "Expected to have received the initial event, but got none"
    ).is_length(1)
    assert_that(sut.events[0]["device"]).described_as(
        "Expected the event device to be a DeviceProxy instance, "
        f"but instead got {type(sut.events[0]['device'])}"
    ).is_instance_of(DeviceProxy)
    assert_that(sut.events[0]["device"].dev_name()).described_as(
        "Expected the event device name to be 'test/pollingdemo/1', "
        f"but instead got {sut.events[0]['device'].dev_name()}"
    ).is_equal_to("test/pollingdemo/1")
    assert_that(sut.events[0]["attribute"]).described_as(
        "Expected the event attribute name to contain somewhere "
        "'/test/pollingdemo/1/pollable_attr', "
        f"but instead got {sut.events[0]['attribute']}"
    ).contains("/test/pollingdemo/1/pollable_attr")
    assert_that(sut.events[0]["current_value"]).described_as(
        "Expected the event current value to be 0, "
        f"but instead got {sut.events[0]['current_value']}"
    ).is_equal_to(0)


def test_tracer_receives_events_from_demo_device(tango_context):
    """Given a Tango device, the (subscribed) tracer receive its events."""

    logging.info("%s", tango_context)

    dev_factory = DevFactory()
    proxy = dev_factory.get_device("test/pollingdemo/1")
    assert hasattr(proxy, "increment_pollable")
    sut = TangoEventTracer()
    sut.subscribe_to_device("test/pollingdemo/1", "pollable_attr")

    # trigger the event and wait more than the polling period
    proxy.increment_pollable()
    time.sleep(0.3)

    # check if the (second) event was captured
    assert_that(sut.events).described_as(
        "Expected to have received exactly one further event "
        "(other than initial one), but got "
        f"{'more' if len(sut.events) > 2 else 'none'} "
        f"(tot: {len(sut.events)} instead of 2)"
    ).is_length(2)
    assert_that(sut.events[1]["device"]).described_as(
        "Expected the event device to be a DeviceProxy instance, "
        f"but instead got {type(sut.events[1]['device'])}"
    ).is_instance_of(DeviceProxy)
    assert_that(sut.events[1]["device"].dev_name()).described_as(
        "Expected the event device name to be 'test/pollingdemo/1', "
        f"but instead got {sut.events[1]['device'].dev_name()}"
    ).is_equal_to("test/pollingdemo/1")
    assert_that(sut.events[1]["attribute"]).described_as(
        "Expected the event attribute name to contain somewhere "
        "'/test/pollingdemo/1/pollable_attr', "
        f"but instead got {sut.events[1]['attribute']}"
    ).contains("/test/pollingdemo/1/pollable_attr")
    assert_that(sut.events[1]["current_value"]).described_as(
        "Expected the event current value to be 1, "
        f"but instead got {sut.events[1]['current_value']}"
    ).is_equal_to(1)
