"""Tests for ::class::`TangoEventLogger` to ensure events are captured.

This second set of tests focuses on ensuring that ::class::`TangoEventLogger`
can subscribe to Tango events and capture them correctly. This is done by
deploying a Tango device, subscribing to its events with the logger and checking
that foreach event is generated a log message.

Those tests are complementary to the ones in
::file::`test_tango_event_logger.py`, which cover the basic methods of the
`TangoEventLogger` class in isolation.

Those tests rely on demo device ::class::`PollingDemoDevice` and so require
::file::`test_polling_demo_device.py` to run successfully to be meaningful.
"""

import logging
from unittest.mock import patch
import pytest

from assertpy import assert_that

from ska_tango_examples.DevFactory import DevFactory
from ska_tango_examples.tango_event_tracer.polling_demo_device import (
    PollingDemoDevice,
)
from ska_tango_examples.tango_event_tracer import TangoEventLogger


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

LOGGING_PATH = (
    "src.ska_tango_examples.tango_event_tracer.tango_event_logger.logging"
)

@patch("logging.info")
def test_logger_subscribes_to_demo_device_and_receive_message(
    logging_info_patch, tango_context):
    """Given a Tango device, the logger subscribe to it (without exceptions)."""
    logging.info("%s", tango_context)

    dev_factory = DevFactory()
    proxy = dev_factory.get_device("test/pollingdemo/1")
    assert hasattr(proxy, "pollable_attr")
    sut = TangoEventLogger()

    sut.log_events_from_device("test/pollingdemo/1", "pollable_attr", 
                            dev_factory=dev_factory.get_device)

    # Assert that content of last call to info includes 
    # device name, attribute name and current value
    assert_that(logging_info_patch.call_args[0][0]).described_as(
        "The log_event method should write the right message to the logger."
    ).contains("test/pollingdemo/1")
    assert_that(logging_info_patch.call_args[0][0]).described_as(
        "The log_event method should write the right message to the logger."
    ).contains("pollable_attr")
    assert_that(logging_info_patch.call_args[0][0]).described_as(
        "The log_event method should write the right message to the logger."
    ).contains(str(proxy.pollable_attr)) 


