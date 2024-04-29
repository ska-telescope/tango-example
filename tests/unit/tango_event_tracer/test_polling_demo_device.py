import logging
import threading

import pytest
import tango
from assertpy import assert_that

from ska_tango_examples.DevFactory import DevFactory
from ska_tango_examples.tango_event_tracer.polling_demo_device import (
    PollingDemoDevice,
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


def test_polling_demo_device_initial_state(tango_context):
    logging.info("%s", tango_context)
    dev_factory = DevFactory()
    proxy = dev_factory.get_device("test/pollingdemo/1")

    assert_that(proxy.pollable_attr).described_as(
        f"Expected pollable_attr to be 0, but got {proxy.pollable_attr}"
    ).is_equal_to(0)

    assert_that(proxy.not_pollable_attr).described_as(
        f"Expected not_pollable_attr to be 0, but got {proxy.not_pollable_attr}"
    ).is_equal_to(0)

    assert_that(str(proxy.state())).described_as(
        f"Expected state to be ON, but got {proxy.state()}"
    ).is_equal_to("ON")

    assert_that(str(proxy.status())).described_as(
        f"Expected status to be Device initialized, but got {proxy.status()}"
    ).is_equal_to("Device initialized")


def test_polling_demo_device_increment_pollable(tango_context):
    logging.info("%s", tango_context)
    dev_factory = DevFactory()
    proxy = dev_factory.get_device("test/pollingdemo/1")

    proxy.increment_pollable()

    assert_that(proxy.pollable_attr).described_as(
        "Expected pollable_attr to be 1 (because of increment), "
        f"but got {proxy.pollable_attr}"
    ).is_equal_to(1)


def test_polling_demo_device_increment_not_pollable(tango_context):
    logging.info("%s", tango_context)
    dev_factory = DevFactory()
    proxy = dev_factory.get_device("test/pollingdemo/1")

    proxy.increment_not_pollable()

    assert_that(proxy.not_pollable_attr).described_as(
        "Expected not_pollable_attr to be 1 (because of increment), "
        f"but got {proxy.not_pollable_attr}"
    ).is_equal_to(1)


def test_polling_demo_device_reset(tango_context):
    logging.info("%s", tango_context)
    dev_factory = DevFactory()
    proxy = dev_factory.get_device("test/pollingdemo/1")
    proxy.increment_pollable()
    proxy.increment_not_pollable()

    proxy.reset()

    assert_that(proxy.pollable_attr).described_as(
        "Expected pollable_attr to be 0 (because of reset), "
        f"but got {proxy.pollable_attr}"
    ).is_equal_to(0)

    assert_that(proxy.not_pollable_attr).described_as(
        "Expected not_pollable_attr to be 0 (because of reset), "
        f"but got {proxy.not_pollable_attr}"
    ).is_equal_to(0)


def test_polling_demo_device_pollable_attr_can_be_subscribed_to(tango_context):
    logging.info("%s", tango_context)
    dev_factory = DevFactory()
    proxy = dev_factory.get_device("test/pollingdemo/1")

    # Subscribe to the pollable attribute and check
    # no exception is raised
    try:
        proxy.poll_attribute("pollable_attr", 100)
        proxy.subscribe_event(
            "pollable_attr", tango.EventType.CHANGE_EVENT, lambda _: _
        )
    except tango.DevFailed as dev_failed_exception:
        assert_that(False).described_as(
            "Expected no exception to be raised when subscribing "
            f"to pollable_attr, instead got {dev_failed_exception}"
        ).is_true()


def test_polling_demo_device_not_pollable_attr_cannot_be_subscribed_to(
    tango_context,
):
    logging.info("%s", tango_context)
    dev_factory = DevFactory()
    proxy = dev_factory.get_device("test/pollingdemo/1")

    # Subscribe to the not pollable attribute and check
    # an exception is raised
    with pytest.raises(tango.DevFailed):
        proxy.poll_attribute("not_pollable_attr", 100)
        proxy.subscribe_event(
            "not_pollable_attr", tango.EventType.CHANGE_EVENT, lambda _: _
        )


def test_polling_demo_device_pollable_attr_events_are_received(tango_context):
    logging.info("%s", tango_context)
    dev_factory = DevFactory()
    proxy = dev_factory.get_device("test/pollingdemo/1")

    # Subscribe to the pollable attribute
    event = threading.Event()

    def event_received_cb(event_data):
        event.set()

    proxy.poll_attribute("pollable_attr", 100)
    proxy.subscribe_event(
        "pollable_attr", tango.EventType.CHANGE_EVENT, event_received_cb
    )

    # Increment the pollable attribute
    proxy.increment_pollable()
    event.wait(timeout=1)

    # Check the event was received
    assert_that(event.is_set()).described_as(
        "Expected the event to be received within 1 second"
    ).is_true()
