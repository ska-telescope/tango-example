# ===============================================
# and some of its unit tests
import threading
import time
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch

import pytest
import tango
from assertpy import assert_that
from tango.test_context import DeviceTestContext

from ska_tango_examples.basic_example.powersupply import PowerSupply
from src.ska_tango_examples.test_utils.tango_event_tracer import (
    TangoEventTracer,
)


@pytest.fixture
def power_supply(request):
    """Create DeviceProxy for tests"""
    true_context = request.config.getoption("--true-context")
    if not true_context:
        with DeviceTestContext(PowerSupply) as proxy:
            yield proxy
    else:
        database = tango.Database()
        instance_list = database.get_device_exported_for_class("PowerSupply")
        for instance in instance_list.value_string:
            yield tango.DeviceProxy(instance)
            break


class TestTangoEventTracer:
    @pytest.fixture
    def tracer(self):
        return TangoEventTracer()

    def add_event(self, tracer, device, value, prev_value, seconds_ago):
        event = {
            "timestamp": datetime.now() - timedelta(seconds=seconds_ago),
            "device": device,
            "attribute": "test_attribute",
            "current_value": value,
            "previous_value": prev_value,
        }
        tracer.events.append(event)

    def test_query_events_no_timeout_with_matching_event(self, tracer):
        self.add_event(
            tracer, "device1", 100, 90, 5
        )  # Adds an event 5 seconds ago
        result = tracer.query_events(lambda e: e["device"] == "device1", None)
        assert_that(result).described_as(
            "Expected to find a matching event for 'device1', but none was found."
        ).is_true()

    # def test_query_events_no_timeout_without_matching_event(self, tracer: TangoEventTracer):
    #     self.add_event(tracer, "device1", 100, 90, 5)
    #     result = tracer.query_events(lambda e: e["device"] == "device2", None)
    #     assert_that(result).described_as(
    #         "Found an unexpected event for 'device2' when none should exist."
    #     ).is_false()

    def test_query_events_with_timeout_event_occurs(self, tracer):
        self.add_event(tracer, "device1", 100, 90, 2)  # Event 2 seconds ago
        result = tracer.query_events(lambda e: e["device"] == "device1", 5)
        assert_that(result).described_as(
            "Expected to find a matching event for 'device1' within 5 seconds, but none was found."
        ).is_true()

    def test_query_events_with_timeout_event_does_not_occur(
        self, tracer: TangoEventTracer
    ):
        self.add_event(tracer, "device1", 100, 90, 10)  # Event 10 seconds ago
        result = tracer.query_events(lambda e: e["device"] == "device1", 5)
        assert_that(result).described_as(
            "An event for 'device1' was found, but it should have been outside the 5-second timeout."
        ).is_false()

    def delayed_add_event(self, tracer, delay, device, value, prev_value):
        """
        Helper method to add an event after a specified delay.
        """

        def _add_event():
            time.sleep(delay)
            self.add_event(tracer, device, value, prev_value, 0)

        threading.Thread(target=_add_event).start()

    def test_query_events_with_delayed_event(self, tracer: TangoEventTracer):
        # At this point, no event for 'device1' exists
        self.delayed_add_event(
            tracer, 5, "device1", 100, 90
        )  # Add an event after 5 seconds

        # query_events with a timeout of 10 seconds
        result = tracer.query_events(lambda e: e["device"] == "device1", 10)

        # Assert that the event is found within the timeout
        assert_that(result).described_as(
            "Expected to find a matching event for 'device1' within 10 seconds, but none was found."
        ).is_true()

    def _check_tracer_one_event(self, tracer, device, attribute, value):
        assert_that(tracer.events).described_as(
            "Event callback should add an event"
        ).is_not_empty()
        assert_that(tracer.events).described_as(
            "Event callback should add exactly one event"
        ).is_length(1)
        assert_that(tracer.events[0]).described_as(
            "The added event should contain the expected fields"
            # ).contains("device", "attribute", "current_value", "previous_value")
        ).contains("device", "attribute", "current_value")
        assert_that(tracer.events[0]["device"]).described_as(
            "The device name in the event should match"
        ).is_equal_to(device)
        assert_that(tracer.events[0]["attribute"]).described_as(
            "The attribute name in the event should match"
        ).is_equal_to(attribute)
        assert_that(tracer.events[0]["current_value"]).described_as(
            "The current value in the event should be correct"
        ).is_equal_to(value)
        # assert_that(tracer.events[0]["previous_value"]).described_as(
        #     "The previous value in the event should be correct"
        # ).is_equal_to(100)

    def test_event_callback_adds_event(self, tracer: TangoEventTracer):
        test_event = MagicMock()
        test_event.device = "test_device"
        test_event.attr_name = "test_attribute"
        test_event.attr_value.value = 123
        # test_event.attr_value.prev_value = 100
        test_event.err = False

        tracer._event_callback(test_event)

        self._check_tracer_one_event(
            tracer, "test_device", "test_attribute", 123  # , 100
        )

    def test_subscribe_to_device(self, tracer: TangoEventTracer):

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
                    "subscribe_event should be called with the correct arguments"
                )

    # def test_event_is_captured(
    #     self, tracer: TangoEventTracer, power_supply: PowerSupply
    # ):
    #     """
    #     Test that an event is captured using the tracer
    #     when the current attribute of the power supply changes.
    #     """

    #     power_supply.Init()
    #     assert power_supply.state() == tango.DevState.STANDBY
    #     tracer.subscribe_to_device(power_supply.dev_name, "current")

    #     power_supply.current = 5.0

    #     query = tracer.query_events(
    #         lambda e: e["device"] == power_supply.dev_name
    #         and e["attribute"] == "current"
    #         and e["current_value"] == 5.0,
    #         5,
    #     )
    #     assert_that(query).described_as(
    #         "Expected to find an event for the current attribute change within 5 seconds, but none was found."
    #     ).is_true()
