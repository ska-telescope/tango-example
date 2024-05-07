"""Test the custom predicates for the ::class::`TangoEventTracer`.

Ensure that the custom predicates for the ::class::`TangoEventTracer` work
as expected, by testing them in isolation against mocked imput.
"""


from datetime import timedelta, datetime
from typing import Callable
from assertpy import assert_that

from unittest.mock import MagicMock

from pytest import fixture
from ska_tango_examples.tango_event_tracer import ReceivedEvent

from ska_tango_examples.tango_event_tracer.event_assertions import (
    build_event_predicate, build_previous_value_predicate, compose_predicates
)
from ska_tango_examples.tango_event_tracer.tango_event_tracer import TangoEventTracer


class TestCustomPredicates:

    @staticmethod
    def create_dummy_event(
        device_name: str, 
        attribute_name: str, 
        attribute_value: str, 
        seconds_ago: float = 0
    ) -> MagicMock:
        
        event = MagicMock(spec=ReceivedEvent)
        event.device_name = device_name
        event.attribute_name = attribute_name
        event.current_value = attribute_value
        event.reception_time = datetime.now() - timedelta(seconds=seconds_ago)
        return event
    
    @fixture
    def tracer(self):
        tracer = MagicMock(spec=TangoEventTracer)
        tracer.events = []
        return tracer
    
    ## #######################################################
    ## Tests for the build_previous_value_predicate function
    
    def test_build_event_returns_a_predicate(self):
        """The build_event_predicate function should return a function."""

        predicate = build_event_predicate()
        assert_that(callable(predicate)).described_as(
            "The build_event_predicate function should return a function which "
            "takes a ReceivedEvent as input and returns a boolean."
        ).is_true()

        event = self.create_dummy_event("test/device/1", "attr1", 10)

        assert_that(predicate(event)).described_as(
            "The predicate should return a boolean."
        ).is_instance_of(bool)
    
    def test_build_event_predicate_mock_matches(self):
        """An event should match the predicate if all fields match."""

        event = self.create_dummy_event("test/device/1", "attr1", 10)

        predicate = build_event_predicate(
            device_name="test/device/1",
            attribute_name="attr1",
            current_value=10
        )
        
        assert_that(predicate(event)).described_as(
            "The event should match the predicate if all fields match."
        ).is_true()


    def test_build_event_predicate_soft_match(self):
        """An event should the predicate if just some specified fields match."""

        event = self.create_dummy_event("test/device/1", "attr1", 10)

        predicate = build_event_predicate(
            current_value=10
        )
        
        assert_that(predicate(event)).described_as(
            "The event should match the predicate if the specified fields match."
        ).is_true()

    def test_build_event_predicate_does_not_match(self):
        """An event should not match the predicate if any field does not match."""

        event = self.create_dummy_event("test/device/1", "attr1", 10)

        predicate = build_event_predicate(
            device_name="test/device/1",
            attribute_name="attr1",
            current_value=11
        )
        
        assert_that(predicate(event)).described_as(
            "The event should not match the predicate if a specified "
            "field does not match."
        ).is_false()

    ## #######################################################
    ## Tests for the build_previous_value_predicate function

    def test_build_previous_value_predicate_returns_a_predicate(self, tracer):
        """The build_previous_value_predicate function should return a function."""

        event = self.create_dummy_event("test/device/1", "attr1", 10)
        prev_event = self.create_dummy_event("test/device/1", "attr1", 5, 
                                             seconds_ago=2)
        tracer.events = [prev_event, event]

        predicate = build_previous_value_predicate(
            tracer, 
            prev_event.current_value)

        assert_that(callable(predicate)).described_as(
            "The build_previous_value_predicate function should return a "
            "function which takes a ReceivedEvent as input and returns a "
            "boolean."
        ).is_true()


        assert_that(predicate(prev_event)).described_as(
            "The predicate should return a boolean."
        ).is_instance_of(bool)

    def test_build_previous_value_predicate_matches(self, tracer):
        """An event should match the predicate if the previous value matches."""

        event = self.create_dummy_event("test/device/1", "attr1", 10)
        prev_event = self.create_dummy_event("test/device/1", "attr1", 5, 
                                             seconds_ago=2)
        tracer.events = [prev_event, event]

        predicate = build_previous_value_predicate(
            tracer, 
            prev_event.current_value)

        assert_that(predicate(event)).described_as(
            "The event should match the predicate if the previous value matches."
        ).is_true()

    def test_build_previous_value_predicate_does_not_match(self, tracer):
        """An event should not match the predicate if the previous value does not match."""

        event = self.create_dummy_event("test/device/1", "attr1", 10)
        prev_event = self.create_dummy_event("test/device/1", "attr1", 5, 
                                             seconds_ago=2)
        tracer.events = [prev_event, event]

        predicate = build_previous_value_predicate(
            tracer, 
            prev_event.current_value + 1)

        assert_that(predicate(event)).described_as(
            "The event should not match the predicate if the previous value "
            "does not match."
        ).is_false()

    def test_build_previous_value_predicate_no_previous_event(self, tracer):
        """An event should not match the predicate if there is no previous event."""

        event = self.create_dummy_event("test/device/1", "attr1", 10)
    
        tracer.events = [ 
            event
        ]

        predicate = build_previous_value_predicate(
            tracer, 
            10)

        assert_that(predicate(event)).described_as(
            "The event should not match the predicate because there is no "
            "previous event. It may be predicate matched with the event "
            "itself."
        ).is_false()

    def test_build_previous_uses_most_recent(self, tracer):
        """An event previous value should be the most recent of the past events."""

        event = self.create_dummy_event("test/device/1", "attr1", 10)
        
    
        tracer.events = [
            self.create_dummy_event("test/device/1", "attr1", 5, seconds_ago=10),
            self.create_dummy_event("test/device/1", "attr1", 7, seconds_ago=8),
            event
        ]

        predicate = build_previous_value_predicate(
            tracer, 
            5)

        assert_that(predicate(event)).described_as(
            "The predicate should check the most recent previous event, not "
            "just one of the previous events or just one which mathces"
        ).is_false()

    def test_build_previous_doesnt_use_future_events(self, tracer):
        """An event previous value should not be from future events."""

        event = self.create_dummy_event("test/device/1", "attr1", 10)
        
        tracer.events = [
            event,
            self.create_dummy_event("test/device/1", "attr1", 5, seconds_ago=-1),
        ]

        predicate = build_previous_value_predicate(
            tracer, 
            5)

        assert_that(predicate(event)).described_as(
            "The predicate should not consider future events."
        ).is_false()

    def test_build_previous_doesnt_use_other_devices(self, tracer):
        """An event previous value should not be from other devices."""

        event = self.create_dummy_event("test/device/1", "attr1", 10)
        
        tracer.events = [
            event,
            self.create_dummy_event("test/device/2", "attr1", 5, seconds_ago=1),
        ]

        predicate = build_previous_value_predicate(
            tracer, 
            5)

        assert_that(predicate(event)).described_as(
            "The predicate should not consider events from other devices."
        ).is_false()

    def test_build_previous_doesnt_use_other_attributes(self, tracer):
        """An event previous value should not be from other attributes."""

        event = self.create_dummy_event("test/device/1", "attr1", 10)
        
        tracer.events = [
            event,
            self.create_dummy_event("test/device/1", "attr2", 5, seconds_ago=1),
        ]

        predicate = build_previous_value_predicate(
            tracer, 
            5)

        assert_that(predicate(event)).described_as(
            "The predicate should not consider events from other attributes."
        ).is_false()

    ## #######################################################
    ## Tests for the compose_predicates function

    def test_compose_predicate_returns_a_predicate(self):
        """The compose_predicates function should return a function."""

        predicate = compose_predicates(
            lambda e: e.device_name == "test/device/1",
            lambda e: e.attribute_name == "attr1",
        )
        assert_that(callable(predicate)).described_as(
            "The compose_predicates function should return a function which "
            "takes a ReceivedEvent as input and returns a boolean."
        ).is_true()

        event = self.create_dummy_event("test/device/1", "attr1", 10)

        assert_that(predicate(event)).described_as(
            "The predicate should return a boolean."
        ).is_instance_of(bool)

    def test_compose_predicate_applies_and_operation(self):
        """The compose_predicates function should apply an AND operation."""

        event = self.create_dummy_event("test/device/1", "attr1", 10)
        
        assert_that(
            compose_predicates(
                lambda _: True, 
                lambda _: True,
            )(event)
        ).described_as(
            "The event should match the predicate if all predicates match."
        ).is_true()

        assert_that(
            compose_predicates(
                lambda _: True, 
                lambda _: False,
            )(event)
        ).described_as(
            "The event should not match the predicate if any predicate does not match."
        ).is_false()

        assert_that(
            compose_predicates(
                lambda _: False, 
                lambda _: True,
            )(event)
        ).described_as(
            "The event should not match the predicate if any predicate does not match."
        ).is_false()

        assert_that(
            compose_predicates(
                lambda _: False, 
                lambda _: False,
            )(event)
        ).described_as(
            "The event should not match the predicate if any predicate does not match."
        ).is_false()

    def test_compose_predicate_applies_custom_connector(self):
        """The compose_predicates function should apply a custom connector."""

        event = self.create_dummy_event("test/device/1", "attr1", 10)

        assert_that(
            compose_predicates(
                lambda _: True, 
                lambda _: False,
                connector=lambda a, b: a or b
            )(event)
        ).described_as(
            "The event should match the predicate if any predicate matches."
        ).is_true()

        

    





