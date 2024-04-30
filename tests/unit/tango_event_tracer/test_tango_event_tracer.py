"""Basic unit tests for ::class::`TangoEventTracer`.

This set of tests covers the basic individual methods of the
::class::`TangoEventTracer` class. The tests are designed to trigger
each single method in isolation and check that it behaves as expected.

Those tests are not exhaustive, because they do not cover the actual
capability of subscribing to events from a Tango device and capturing
those events correctly. For that, see ::file::`test_tracer_subscribe_event.py`.
"""

# import logging
import threading
import time
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest
import tango
from assertpy import assert_that

from ska_tango_examples.tango_event_tracer.received_event import ReceivedEvent
from src.ska_tango_examples.tango_event_tracer import TangoEventTracer


class TestTangoEventTracer:
    """Unit tests for the `TangoEventTracer` class."""

    # ############################
    # Fixtures and helper methods

    @pytest.fixture
    def tracer(self) -> TangoEventTracer:
        """Create a `TangoEventTracer` instance for testing.

        :return: a `TangoEventTracer` instance.
        """
        return TangoEventTracer()

    def create_mock_eventdata(self, dev_name, attribute, value, error=False):
        """Create a mock Tango event data object.

        :param device: The device name.
        :param attribute: The attribute name.
        :param value: The current value.
        :param error: Whether the event is an error event, default is False.
        :return: A mock Tango event data object.
        """

        # Create a mock device
        mock_device = MagicMock(spec=tango.DeviceProxy)
        mock_device.dev_name.return_value = dev_name

        # Create a mock attribute value
        mock_attr_value = MagicMock()
        mock_attr_value.value = value
        mock_attr_value.name = attribute

        # Create a mock event
        mock_event = MagicMock(spec=tango.EventData)
        mock_event.device = mock_device
        mock_event.attr_name = (
            f"tango://127.0.0.1:8080/{dev_name}/{attribute}#dbase=no"
        )
        mock_event.attr_value = mock_attr_value
        mock_event.err = error

        return mock_event

    def add_event(self, tracer, device, value, seconds_ago=0) -> None:
        """Add an event to the tracer.

        :param tracer: The `TangoEventTracer` instance.
        :param device: The device name.
        :param value: The current value.
        :param seconds_ago: How many seconds ago the event occurred,
            default is 0.
        """
        test_event = ReceivedEvent(
            self.create_mock_eventdata(device, "test_attribute", value)
        )

        # Set the timestamp to the past (if needed)
        if seconds_ago > 0:
            test_event.reception_time = datetime.now() - timedelta(
                seconds=seconds_ago
            )

        tracer._events.append(test_event)

    def delayed_add_event(self, tracer, delay, device, value) -> None:
        """Add an event to the tracer after a delay.

        :param tracer: The `TangoEventTracer` instance.
        :param delay: The delay in seconds.
        :param device: The device name.
        :param value: The current value.
        """

        def _add_event():
            time.sleep(delay)
            self.add_event(tracer, device, value)

        threading.Thread(target=_add_event).start()

    def _check_tracer_one_event(
        self, tracer: TangoEventTracer, device: str, attribute: str, value
    ) -> None:
        """Check that tracer contains exactly one event with expected fields.

        :param tracer: The `TangoEventTracer` instance.
        :param device: The device name.
        :param attribute: The attribute name.
        :param value: The current value.
        """
        assert_that(tracer.events).described_as(
            "Event callback should add an event"
        ).is_not_empty()
        assert_that(tracer.events).described_as(
            "Event callback should add exactly one event"
        ).is_length(1)
        assert_that(tracer.events[0]).described_as(
            "The added event should be a ReceivedEvent instance"
        ).is_instance_of(ReceivedEvent)
        assert_that(tracer.events[0].device_name).described_as(
            "The device name in the event should match"
        ).is_equal_to(device)
        assert_that(tracer.events[0].attribute_name).described_as(
            "The attribute name in the event should match"
        ).is_equal_to(attribute)
        assert_that(tracer.events[0].current_value).described_as(
            "The current value in the event should be correct"
        ).is_equal_to(value)

    # ########################################
    # Test cases: query_events method
    # (timeout mechanism)

    def test_query_events_no_timeout_with_matching_event(
        self, tracer: TangoEventTracer
    ) -> None:
        """Test that an event is found when no timeout is specified.

        :param tracer: The `TangoEventTracer` instance.
        """
        self.add_event(
            tracer, "device1", 100, 5
        )  # Adds an event 5 seconds ago
        result = tracer.query_events(
            lambda e: e.device_name == "device1", timeout=None
        )
        assert_that(result).described_as(
            "Expected to find a matching event for 'device1', "
            "but none was found."
        ).is_length(1)

    # NOTE: this test cannot happen! Infinite wait...
    # def test_query_events_no_timeout_without_matching_event(
    #    self, tracer: TangoEventTracer):
    #     self.add_event(tracer, "device1", 100, 5)
    #     result = tracer.query_events(
    #           lambda e: e.device_name == "device2", None)
    #     assert_that(result).described_as(
    #         "Found an unexpected event for 'device2' when none should exist."
    #     ).is_false()

    def test_query_events_with_timeout_event_occurs(
        self, tracer: TangoEventTracer
    ) -> None:
        """Test that an event is found when the timeout is long enough.

        :param tracer: The `TangoEventTracer` instance.
        """
        self.add_event(tracer, "device1", 100, 2)  # Event 2 seconds ago
        result = tracer.query_events(
            lambda e: e.device_name == "device1", timeout=5
        )
        assert_that(result).described_as(
            "Expected to find a matching event for 'device1' within "
            "5 seconds, but none was found."
        ).is_length(1)

    def test_query_events_with_timeout_event_does_not_occur(
        self, tracer: TangoEventTracer
    ) -> None:
        """Test that an event is not found when the timeout is too short.

        :param tracer: The `TangoEventTracer` instance.
        """
        self.add_event(tracer, "device1", 100, 10)  # Event 10 seconds ago

        # query_events with a timeout of 5 seconds
        result = tracer.query_events(
            lambda e: e.device_name == "device1", timeout=5
        )

        assert_that(result).described_as(
            "An event for 'device1' was found, but it should have been "
            "outside the 5-second timeout."
        ).is_length(0)

    def test_query_events_with_delayed_event(
        self, tracer: TangoEventTracer
    ) -> None:
        """Test a delayed event is captured by the tracer.

        :param tracer: The `TangoEventTracer` instance.
        """
        # At this point, no event for 'device1' exists
        self.delayed_add_event(
            tracer, 5, "device1", 100
        )  # Add an event after 5 seconds

        # query_events with a timeout of 10 seconds
        result = tracer.query_events(
            lambda e: e.device_name == "device1", timeout=10
        )

        # Assert that the event is found within the timeout
        assert_that(result).described_as(
            "Expected to find a matching event for 'device1' "
            "within 10 seconds, but none was found."
        ).is_length(1)

    # ########################################
    # Test cases: event_callback method

    def test_event_callback_adds_event(self, tracer: TangoEventTracer) -> None:
        """Test that the event callback adds an event to the tracer.

        :param tracer: The `TangoEventTracer` instance.
        """
        test_event = self.create_mock_eventdata(
            "test_device", "test_attribute", 123
        )

        tracer._event_callback(test_event)

        self._check_tracer_one_event(
            tracer, "test_device", "test_attribute", 123  # , 100
        )

    def test_event_callback_when_error_ignore_event(
        self, tracer: TangoEventTracer
    ) -> None:
        """Test that the event callback ignores events with errors.

        :param tracer: The `TangoEventTracer` instance.
        """
        test_event = self.create_mock_eventdata(
            "test_device", "test_attribute", 123, error=True
        )

        tracer._event_callback(test_event)

        assert_that(tracer.events).described_as(
            "Event callback should ignore events with errors"
        ).is_empty()

    # ########################################
    # Test cases: subscribe method

    def test_subscribe_to_device(self, tracer: TangoEventTracer) -> None:
        """Test subscribing to a device and attribute.

        :param tracer: The `TangoEventTracer` instance.

        :raises AssertionError: when an assertion fails.
        """
        device_name = "test_device"
        attribute_name = "test_attribute"

        with patch("tango.DeviceProxy") as mock_proxy:

            tracer.subscribe_to_device(device_name, attribute_name)

            try:
                mock_proxy.assert_called_with(device_name)
            except AssertionError:
                raise AssertionError(
                    "DeviceProxy should be called with the correct device name"
                )

            try:
                mock_proxy.return_value.subscribe_event.assert_called_with(
                    attribute_name,
                    tango.EventType.CHANGE_EVENT,
                    tracer._event_callback,
                )
            except AssertionError:
                raise AssertionError(
                    "subscribe_event should be called with "
                    "the correct arguments"
                )

    def test_subscribe_to_device_passing_dev_factory(
        self, tracer: TangoEventTracer
    ) -> None:
        """Test subscribing to a device and attribute passing a device factory.

        :param tracer: The `TangoEventTracer` instance.

        :raises AssertionError: when an assertion fails.
        """
        device_name = "test_device"
        attribute_name = "test_attribute"

        def device_factory(device_name):
            return tango.DeviceProxy(device_name)

        with patch("tango.DeviceProxy") as mock_proxy:

            tracer.subscribe_to_device(
                device_name, attribute_name, dev_factory=device_factory
            )

            try:
                mock_proxy.assert_called_with(device_name)
            except AssertionError:
                raise AssertionError(
                    "DeviceProxy should be called with the correct device name"
                )

            try:
                mock_proxy.return_value.subscribe_event.assert_called_with(
                    attribute_name,
                    tango.EventType.CHANGE_EVENT,
                    tracer._event_callback,
                )
            except AssertionError:
                raise AssertionError(
                    "subscribe_event should be called with "
                    "the correct arguments"
                )

    def test_clear_events(self, tracer: TangoEventTracer) -> None:
        """Test clearing the events from the tracer.

        :param tracer: The `TangoEventTracer` instance.
        """
        self.add_event(tracer, "device1", 100, 5)
        self.add_event(tracer, "device2", 100, 5)
        assert len(tracer.events) == 2

        tracer.clear_events()

        assert_that(tracer.events).described_as(
            "Expected the events list to be empty after clearing"
        ).is_empty()

    # ########################################
    # Test cases: query_events method
    # (correct predicate evaluation)

    def test_query_events_within_multiple_devices_returns_just_the_right_ones(
        self, tracer: TangoEventTracer
    ) -> None:
        """Test that the query select exactly the required events."""
        self.add_event(tracer, "device1", 100, 10)  # Event 10 seconds ago
        self.add_event(tracer, "device1", 100, 25)  # Event 25 seconds ago
        self.add_event(tracer, "device2", 100, 20)  # Event 20 seconds ago
        self.add_event(tracer, "device2", 100, 15)  # Event 15 seconds ago
        self.add_event(tracer, "device2", 100, 30)  # Event 30 seconds ago
        self.add_event(tracer, "device3", 100, 30)  # Event 30 seconds ago

        result = tracer.query_events(lambda e: e.device_name == "device2")

        assert_that(result).described_as(
            "Expected to find 3 events for 'device2'"
        ).is_length(3)

        assert_that(result[0].device_name).described_as(
            "Expected the device name to be 'device2'"
        ).is_equal_to("device2")
        assert_that(result[1].device_name).described_as(
            "Expected the device name to be 'device2'"
        ).is_equal_to("device2")
        assert_that(result[2].device_name).described_as(
            "Expected the device name to be 'device2'"
        ).is_equal_to("device2")

    def test_query_events_within_multiple_devices_all_wrong_returns_none(
        self, tracer: TangoEventTracer
    ) -> None:
        """Test that the query select exactly the required events."""
        self.add_event(tracer, "device1", 100, 10)  # Event 10 seconds ago
        self.add_event(tracer, "device1", 100, 25)  # Event 25 seconds ago
        self.add_event(tracer, "device2", 100, 20)  # Event 20 seconds ago
        self.add_event(tracer, "device2", 100, 15)  # Event 15 seconds ago
        self.add_event(tracer, "device2", 100, 30)  # Event 30 seconds ago
        self.add_event(tracer, "device3", 100, 30)  # Event 30 seconds ago

        result = tracer.query_events(lambda e: e.device_name == "device4")

        assert_that(result).described_as(
            "Expected to find 0 events for 'device4'"
        ).is_length(0)

    def test_query_event_pairs_returns_just_the_right_ones(
        self, tracer: TangoEventTracer
    ) -> None:
        """Test that the query select exactly the required events."""

        self.add_event(tracer, "device1", 100, 10)  # A) Event 10 seconds ago
        self.add_event(tracer, "device2", 100, 8)  # B)
        self.add_event(tracer, "device2", 150, 5)  # C)
        self.add_event(tracer, "device1", 180, 4)  # D)
        self.add_event(tracer, "device1", 90, 2)  # E)
        self.add_event(tracer, "device1", 200, 1)  # F)
        self.add_event(tracer, "device1", 210, 1)  # G)

        # detect sudden increases of 50+ within 3 seconds
        result = tracer.query_event_pairs(
            lambda e1, e2: e1.device_name == e2.device_name
            and e1.current_value < e2.current_value
            and e2.reception_time - e1.reception_time <= timedelta(seconds=3.1)
            and e2.current_value - e1.current_value >= 50
            # between e1 and e2 there is no other event
            # from the same device
            and all(
                e.device_name != e1.device_name
                for e in tracer.events
                if e.reception_time > e1.reception_time
                and e.reception_time < e2.reception_time
            ),
            is_pair_sorted=True,
        )

        # expect to find: (B, C) and (E, F)
        # nothing else satisfies the predicate
        assert_that(result).described_as(
            "Expected to find 2 event pairs"
        ).is_length(2)

        assert_that(result[0][0].device_name).described_as(
            "Expected the device name to be 'device2'"
        ).is_equal_to("device2")
        assert_that(result[0][1].device_name).described_as(
            "Expected the device name to be 'device2'"
        ).is_equal_to("device2")

        assert_that(result[1][0].device_name).described_as(
            "Expected the device name to be 'device1'"
        ).is_equal_to("device1")
        assert_that(result[1][1].device_name).described_as(
            "Expected the device name to be 'device1'"
        ).is_equal_to("device1")
