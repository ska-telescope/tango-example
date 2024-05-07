"""Predicates to filter ::class::`TangoEventTracer` events in queries.

A collection of predicates to filter ::class::`ReceivedEvent` instances
when calling the ::method::`TangoEventTracer.query_events` method. The main
purpose of these predicates is to allow the user to compose complex queries
to filter events based on their attributes but also on their position in the
event sequence.
"""


from typing import Callable, Optional, Union

from ska_tango_examples.tango_event_tracer.received_event import ReceivedEvent
from ska_tango_examples.tango_event_tracer.tango_event_tracer import (
    TangoEventTracer,
)

ANY = None


def event_matches_parameters(
    target_event: ReceivedEvent,
    device_name: Optional[str] = ANY,
    attribute_name: Optional[str] = ANY,
    current_value: Optional[any] = ANY,
    max_age: Optional[Union[int, float]] = None,
) -> bool:
    """Soft match events just on passed criteria.

    :param device_name: The device name to match. If not provided, it will
        match any device name.
    :param attribute_name: The attribute name to match. If not provided, it will
        match any attribute name.
    :param current_value: The current value to match. If not provided, it will
        match any current value.
    :param max_age: The maximum age of the event in seconds. If not provided,
        it will match any age.

    :return: True if the event matches the provided criteria, False otherwise.
    """

    if device_name is not ANY and target_event.device_name != device_name:
        return False
    if (
        attribute_name is not ANY
        and target_event.attribute_name != attribute_name
    ):
        return False
    if (
        current_value is not ANY
        and not target_event.current_value == current_value
    ):
        return False
    if max_age is not None and target_event.reception_age() > max_age:
        return False
    return True


def event_has_previous_value(
    target_event: ReceivedEvent, tracer: TangoEventTracer, previous_value: any
) -> Callable[[ReceivedEvent], bool]:
    """Build a predicate to look for an event with a specific previous value."""
    previous_event = None

    # If any, get the previous event for the same device and attribute
    # than the current event

    for e in tracer.events:
        if (
            e.device_name == target_event.device_name
            and e.attribute_name == target_event.attribute_name
            and e.reception_time < target_event.reception_time
        ):

            if (
                previous_event is None
                or e.reception_time > previous_event.reception_time
            ):
                previous_event = e

    # If no previous event was found, return False (there is no event
    # before the target one, so none with the expected previous value)
    if previous_event is None:
        return False

    # If the previous event was found, check if previous value matches
    return previous_event.current_value == previous_value
