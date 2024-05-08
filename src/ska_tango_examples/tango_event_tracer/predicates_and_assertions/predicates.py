"""Predicates to filter ::class::`TangoEventTracer` events in queries.

A collection of predicates to filter ::class::`ReceivedEvent` instances
when calling the ::method::`TangoEventTracer.query_events` method. The main
purpose of these predicates is to allow the user to compose complex queries
to filter events based on their attributes but also on their position in the
event sequence.
"""


from typing import Callable, Optional

from ska_tango_examples.tango_event_tracer.received_event import ReceivedEvent
from ska_tango_examples.tango_event_tracer.tango_event_tracer import (
    TangoEventTracer,
)

ANY = None


def event_matches_parameters(
    target_event: ReceivedEvent,
    device_name: Optional[str] = ANY,
    attribute_name: Optional[str] = ANY,
    attribute_value: Optional[any] = ANY,
) -> bool:
    """Check if an event matches the provided criteria. If a criteria is not
    provided, it will match any value.

    :param device_name: The device name to match. If not provided, it will
        match any device name.
    :param attribute_name: The attribute name to match. If not provided,
        it will match any attribute name.
    :param attribute_value: The current value to match. If not provided,
        it will match any current value.

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
        attribute_value is not ANY
        and not target_event.attribute_value == attribute_value
    ):
        return False
    return True


def event_has_previous_value(
    target_event: ReceivedEvent, tracer: TangoEventTracer, previous_value: any
) -> Callable[[ReceivedEvent], bool]:
    """Check if an event has a specific previous value.

    This predicate can be used to match events based on the value they had
    before the current one. It is useful to check if an event was triggered
    by a specific value change. If the event has no previous value, it will
    return False.

    :param target_event: The event to check.
    :param tracer: The event tracer containing the events.
    :param previous_value: The value to match.

    :return: True if the event has the provided previous value, False
        if the event has no previous value or if the previous value does
        not match.
    """
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
    return previous_event.attribute_value == previous_value
