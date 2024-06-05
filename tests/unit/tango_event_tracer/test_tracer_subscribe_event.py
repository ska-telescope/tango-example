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
from tango import DevFailed, DeviceProxy, EventData

from ska_tango_examples.DevFactory import DevFactory
from ska_tango_examples.tango_event_tracer.polling_demo_device import (
    PollingDemoDevice,
)
from ska_tango_examples.tango_event_tracer.received_event import ReceivedEvent
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
    assert hasattr(proxy, "subscrib_attr")
    sut = TangoEventTracer()

    sut.subscribe_to_device("test/pollingdemo/1", "subscrib_attr")

    # NOTE: first event is the initial value => check if it was captured
    assert_that(sut.events).described_as(
        "Expected to have received the initial event, but got none"
    ).is_length(1)
    assert_that(sut.events[0]).described_as(
        "Expected the event to be an instance of tango.EventData,"
        f"but instead got {type(sut.events[0])}"
    ).is_instance_of(ReceivedEvent)
    assert_that(sut.events[0].event_data).described_as(
        "Expected the event to be an instance of ReceivedEvent,"
        f"but instead got {type(sut.events[0].event_data)}"
    ).is_instance_of(EventData)
    assert_that(sut.events[0].device).described_as(
        "Expected the event device to be a DeviceProxy instance, "
        f"but instead got {type(sut.events[0].device)}"
    ).is_instance_of(DeviceProxy)
    assert_that(sut.events[0].device_name).described_as(
        "Expected the event device name to be 'test/pollingdemo/1', "
        f"but instead got {sut.events[0].device_name}"
    ).is_equal_to("test/pollingdemo/1")
    assert_that(sut.events[0].attribute_name).described_as(
        "Expected the event current value to be 'subscrib_attr' "
        f"but instead got {sut.events[0].attribute_name}"
    ).is_equal_to("subscrib_attr")

    assert_that(sut.events[0].attribute_value).described_as(
        "Expected the event current value to be 0, "
        f"but instead got {sut.events[0].attribute_value}"
    ).is_equal_to(0)


def test_tracer_receives_events_from_demo_device(tango_context):
    """Given a Tango device, the (subscribed) tracer receive its events."""

    logging.info("%s", tango_context)

    dev_factory = DevFactory()
    proxy = dev_factory.get_device("test/pollingdemo/1")
    sut = TangoEventTracer()
    sut.subscribe_to_device("test/pollingdemo/1", "subscrib_attr")

    # trigger the event and wait more than the polling period
    proxy.increment_subscrib()
    time.sleep(0.3)

    # check if the (second) event was captured
    assert_that(sut.events).described_as(
        "Expected to have received exactly one further event "
        "(other than initial one), but got "
        f"{'more' if len(sut.events) > 2 else 'none'} "
        f"(tot: {len(sut.events)} instead of 2)"
    ).is_length(2)
    assert_that(sut.events[1].event_data).described_as(
        "Expected the event to be an instance of ReceivedEvent,"
        f"but instead got {type(sut.events[1].event_data)}"
    ).is_instance_of(EventData)
    assert_that(sut.events[1].device).described_as(
        "Expected the event device to be a DeviceProxy instance, "
        f"but instead got {type(sut.events[1].device)}"
    ).is_instance_of(DeviceProxy)
    assert_that(sut.events[1].device_name).described_as(
        "Expected the event device name to be 'test/pollingdemo/1', "
        f"but instead got {sut.events[1].device_name}"
    ).is_equal_to("test/pollingdemo/1")
    assert_that(sut.events[1].attribute_name).described_as(
        "Expected the event current value to be 'subscrib_attr' "
        f"but instead got {sut.events[1].attribute_name}"
    ).is_equal_to("subscrib_attr")
    assert_that(sut.events[1].attribute_value).described_as(
        "Expected the event current value to be 1, "
        f"but instead got {sut.events[1].attribute_value}"
    ).is_equal_to(1)


def test_tracer_query_real_events(tango_context):

    logging.info("%s", tango_context)

    # dev_factory = DevFactory()
    # proxy = dev_factory.get_device("test/pollingdemo/1")

    proxy = tango_context.get_device("test/pollingdemo/1")

    sut = TangoEventTracer()
    sut.subscribe_to_device("test/pollingdemo/1", "subscrib_attr")

    # trigger the event and wait more than the polling period
    proxy.increment_subscrib()

    query_result = sut.query_events(
        lambda e: e.device_name == "test/pollingdemo/1"
        and e.attribute_name == "subscrib_attr"
        and e.attribute_value == 1,
        timeout=5,
    )

    assert_that(query_result).described_as(
        "Expected exactly one event to be captured, but got "
        f"{'more' if len(query_result) > 1 else 'none'} "
        f"(tot: {len(query_result)} instead of 1)"
    ).is_length(1)


def test_tracer_when_attr_not_pollable_raises_exception(tango_context):
    """Given a Tango device, if the attribute is not pollable, the tracer raises an exception."""
    logging.info("%s", tango_context)

    sut = TangoEventTracer()

    with pytest.raises(DevFailed):
        sut.subscribe_to_device("test/pollingdemo/1", "not_subscrib_attr")


def test_tracer_when_attr_not_found_raises_exception(tango_context):
    """Given a Tango device, if the attribute is not found, the tracer raises an exception."""
    logging.info("%s", tango_context)

    sut = TangoEventTracer()

    with pytest.raises(DevFailed):
        sut.subscribe_to_device("test/pollingdemo/1", "not_existent_attr")


def test_tracer_when_device_not_found_raises_exception(tango_context):
    """Given a Tango device, if the device is not found, the tracer raises an exception."""
    logging.info("%s", tango_context)

    sut = TangoEventTracer()

    with pytest.raises(DevFailed):
        sut.subscribe_to_device("test/pollingdemo/100", "subscrib_attr")


def test_tracer_late_subscription_catches_last_event(tango_context):
    """A late subscription catches just the last event.

    When you subscribe to a device attribute, after a sequence of events
    have already been triggered, the subscription should only catch the
    last event.
    """
    proxy = tango_context.get_device("test/pollingdemo/1")

    proxy.increment_subscrib()
    proxy.increment_subscrib()
    proxy.increment_subscrib()

    time.sleep(1)

    sut = TangoEventTracer()
    sut.subscribe_to_device("test/pollingdemo/1", "subscrib_attr")

    query_result = sut.query_events(
        lambda e: e.device_name == "test/pollingdemo/1"
        and e.attribute_name == "subscrib_attr"
    )

    assert_that(query_result).described_as(
        "Expected exactly four events to be captured, but got "
        f"{'more' if len(query_result) > 1 else 'none'} "
        f"(tot: {len(query_result)} instead of 1)"
    ).is_length(1)

    assert_that(query_result[0].attribute_value).is_equal_to(3)

    # those assertions would fail!
    # assert_that(query_result[0].attribute_value).is_equal_to(0)
    # assert_that(query_result[1].attribute_value).is_equal_to(1)
    # assert_that(query_result[2].attribute_value).is_equal_to(2)
    # assert_that(query_result[3].attribute_value).is_equal_to(3)


@pytest.mark.xfail(
    reason="Right now, multiple subscriptions duplicate the events"
    "TODO: discuss if this is the desired behavior or not and"
    "eventually fix the code to avoid this."
)
def test_tracer_multiple_subscription_doesnt_duplicate_events(tango_context):
    """Multiple subscriptions don't duplicate events.

    When you subscribe to a device attribute multiple times, the events
    should not be duplicated.
    """
    proxy = tango_context.get_device("test/pollingdemo/1")

    sut = TangoEventTracer()
    sut.subscribe_to_device("test/pollingdemo/1", "subscrib_attr")
    sut.subscribe_to_device("test/pollingdemo/1", "subscrib_attr")

    proxy.increment_subscrib()
    proxy.increment_subscrib()
    proxy.increment_subscrib()

    time.sleep(1)

    query_result = sut.query_events(
        lambda e: e.device_name == "test/pollingdemo/1"
        and e.attribute_name == "subscrib_attr"
    )

    assert_that(query_result).described_as(
        "Expected exactly four event to be captured, but got "
        f"{'more' if len(query_result) > 4 else 'none'} "
        f"(tot: {len(query_result)} instead of 4)"
    ).is_length(4)

    assert_that(query_result[0].attribute_value).is_equal_to(0)
    assert_that(query_result[1].attribute_value).is_equal_to(1)
    assert_that(query_result[2].attribute_value).is_equal_to(2)
    assert_that(query_result[3].attribute_value).is_equal_to(3)
