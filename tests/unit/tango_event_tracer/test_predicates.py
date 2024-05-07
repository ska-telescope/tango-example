"""Test the custom predicates for the ::class::`TangoEventTracer`.

Ensure that the custom predicates for the ::class::`TangoEventTracer` work
as expected, matching the correct events and values.
"""


from datetime import datetime, timedelta
from unittest.mock import MagicMock

import tango
from assertpy import assert_that
from pytest import fixture

from ska_tango_examples.tango_event_tracer import ReceivedEvent
from ska_tango_examples.tango_event_tracer.predicates_and_assertions.predicates import (
    event_has_previous_value,
    event_matches_parameters,
)
from ska_tango_examples.tango_event_tracer.tango_event_tracer import (
    TangoEventTracer,
)


class TestCustomPredicates:
    @staticmethod
    def create_dummy_event(
        device_name: str,
        attribute_name: str,
        attribute_value: str,
        seconds_ago: float = 0,
    ) -> MagicMock:

        event = MagicMock(spec=ReceivedEvent)
        event.device_name = device_name
        event.attribute_name = attribute_name
        event.attribute_value = attribute_value
        event.reception_time = datetime.now() - timedelta(seconds=seconds_ago)
        return event

    @fixture
    def tracer(self):
        tracer = MagicMock(spec=TangoEventTracer)
        tracer.events = []
        return tracer

    # #######################################################
    # Tests for the build_previous_value_predicate function

    def test_predicate_event_predicate_mock_matches(self):
        """An event should match the predicate if all fields match."""

        event = self.create_dummy_event("test/device/1", "attr1", 10)

        assert_that(
            event_matches_parameters(
                target_event=event,
                device_name="test/device/1",
                attribute_name="attr1",
                attribute_value=10,
            )
        ).described_as(
            "The event should match the predicate if all fields match."
        ).is_true()

    def test_predicate_event_predicate_soft_match(self):
        """An event should the predicate if just some specified fields match."""

        event = self.create_dummy_event("test/device/1", "attr1", 10)

        assert_that(
            event_matches_parameters(target_event=event, attribute_value=10)
        ).described_as(
            "The event should match the predicate if the specified fields match."
        ).is_true()

    def test_predicate_tango_state_matches(self):
        """An event match when attribute is a ::class::`tango.DevState`."""

        event = self.create_dummy_event(
            "test/device/1", "state", tango.DevState.ON
        )

        assert_that(
            event_matches_parameters(
                target_event=event,
                device_name="test/device/1",
                attribute_name="state",
                attribute_value=tango.DevState.ON,
            )
        ).described_as(
            "The event should match the predicate if the specified fields match."
        ).is_true()

    def test_predicate_event_predicate_does_not_match(self):
        """An event should not match the predicate if any field does not match."""

        event = self.create_dummy_event("test/device/1", "attr1", 10)

        assert_that(
            event_matches_parameters(
                target_event=event,
                device_name="test/device/1",
                attribute_name="attr1",
                attribute_value=11,
            )
        ).described_as(
            "The event should not match the predicate if a specified "
            "field does not match."
        ).is_false()

    # #######################################################
    # Tests for the build_previous_value_predicate function

    def test_predicate_previous_value_predicate_matches(self, tracer):
        """An event should match the predicate if the previous value matches."""

        event = self.create_dummy_event("test/device/1", "attr1", 10)
        prev_event = self.create_dummy_event(
            "test/device/1", "attr1", 5, seconds_ago=2
        )
        tracer.events = [prev_event, event]

        assert_that(
            event_has_previous_value(
                target_event=event, tracer=tracer, previous_value=5
            )
        ).described_as(
            "The event should match the predicate if the previous value matches."
        ).is_true()

    def test_predicate_previous_value_predicate_does_not_match(self, tracer):
        """An event should not match the predicate if the previous value does not match."""

        event = self.create_dummy_event("test/device/1", "attr1", 10)
        prev_event = self.create_dummy_event(
            "test/device/1", "attr1", 5, seconds_ago=2
        )
        tracer.events = [prev_event, event]

        assert_that(
            event_has_previous_value(
                target_event=event, tracer=tracer, previous_value=6
            )
        ).described_as(
            "The event should not match the predicate if the previous value "
            "does not match."
        ).is_false()

    def test_predicate_previous_value_predicate_no_previous_event(
        self, tracer
    ):
        """An event should not match the predicate if there is no previous event."""

        event = self.create_dummy_event("test/device/1", "attr1", 10)

        tracer.events = [event]

        assert_that(
            event_has_previous_value(
                target_event=event, tracer=tracer, previous_value=10
            )
        ).described_as(
            "The event should not match the predicate because there is no "
            "previous event. It may be predicate matched with the event "
            "itself."
        ).is_false()

    def test_predicate_previous_uses_most_recent(self, tracer):
        """An event previous value should be the most recent of the past events."""

        event = self.create_dummy_event("test/device/1", "attr1", 10)

        tracer.events = [
            self.create_dummy_event(
                "test/device/1", "attr1", 5, seconds_ago=10
            ),
            self.create_dummy_event(
                "test/device/1", "attr1", 7, seconds_ago=8
            ),
            event,
        ]

        assert_that(
            event_has_previous_value(
                target_event=event, tracer=tracer, previous_value=5
            )
        ).described_as(
            "The predicate should check the most recent previous event, not "
            "just one of the previous events or just one which mathces"
        ).is_false()

    def test_predicate_previous_doesnt_use_future_events(self, tracer):
        """An event previous value should not be from future events."""

        event = self.create_dummy_event("test/device/1", "attr1", 10)

        tracer.events = [
            event,
            self.create_dummy_event(
                "test/device/1", "attr1", 5, seconds_ago=-1
            ),
        ]

        assert_that(
            event_has_previous_value(
                target_event=event, tracer=tracer, previous_value=5
            )
        ).described_as(
            "The predicate should not consider future events."
        ).is_false()

    def test_predicate_previous_doesnt_use_other_devices(self, tracer):
        """An event previous value should not be from other devices."""

        event = self.create_dummy_event("test/device/1", "attr1", 10)

        tracer.events = [
            event,
            self.create_dummy_event(
                "test/device/2", "attr1", 5, seconds_ago=1
            ),
        ]

        assert_that(
            event_has_previous_value(
                target_event=event, tracer=tracer, previous_value=5
            )
        ).described_as(
            "The predicate should not consider events from other devices."
        ).is_false()

    def test_predicate_previous_doesnt_use_other_attributes(self, tracer):
        """An event previous value should not be from other attributes."""

        event = self.create_dummy_event("test/device/1", "attr1", 10)

        tracer.events = [
            event,
            self.create_dummy_event(
                "test/device/1", "attr2", 5, seconds_ago=1
            ),
        ]

        assert_that(
            event_has_previous_value(
                target_event=event, tracer=tracer, previous_value=5
            )
        ).described_as(
            "The predicate should not consider events from other attributes."
        ).is_false()
