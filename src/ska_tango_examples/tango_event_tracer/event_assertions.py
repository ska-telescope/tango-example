"""Basic custom event-based assertions for ::class::`TangoEventTracer`.

This module provides some example of basic custom ::mod::`assertpy` assertions
to be used with ::class::`TangoEventTracer` instances. These assertions can be
used to verify properties about the events captured by the tracer.

Essentially they are query calls to the tracer, within
a timeout, to check if the are events which match an expected more or less
complex predicate. 

You can and you are encouraged to take those assertions as a starting point
to create more complex ones, as needed by your test cases.
"""

from typing import Callable, Optional, Union
from assertpy import add_extension

from ska_tango_examples.tango_event_tracer import ReceivedEvent
from ska_tango_examples.tango_event_tracer.tango_event_tracer import (
    TangoEventTracer
)

ANY = None


def build_event_predicate(
        device_name: Optional[str] = ANY, 
        attribute_name: Optional[str] = ANY, 
        current_value: Optional[any] = ANY, 
        max_age: Optional[Union[int, float]] = None
        ) -> Callable[[ReceivedEvent], bool]:
    """Build a predicate to match events based on the provided params.

    :param device_name: The device name to match. If not provided, it will
        match any device name.
    :param attribute_name: The attribute name to match. If not provided, it will
        match any attribute name.
    :param current_value: The current value to match. If not provided, it will
        match any current value.
    :param max_age: The maximum age of the event in seconds. If not provided,
        it will match any age.
    
    :return: A predicate function that returns True if the event matches the
        provided criteria, False otherwise.

    Usage example:
    >>> build_event_predicate(
    ...     device_name="device1",
    ...     attribute_name="attribute1",
    ...     current_value=42,
    ... )
    ... # is equivalent to:
    ... lambda event: (
    ...     event.device_name == "device1"
    ...     and event.attribute_name == "attribute1"
    ...     and event.current_value == 42
    ... )

    """
    
    def predicate(event: ReceivedEvent) -> bool:
        if device_name is not ANY and event.device_name != device_name:
            return False
        if attribute_name is not ANY and event.attribute_name != attribute_name:
            return False
        if current_value is not ANY and event.current_value != current_value:
            return False
        if max_age is not None and event.reception_age() > max_age:
            return False
        return True

    return predicate

def previous_value_predicate(
        tracer: TangoEventTracer,
        previous_value: any
        ) -> Callable[[ReceivedEvent], bool]:
    """Build a predicate to look for an event with a specific previous value."""

    def predicate(event: ReceivedEvent) -> bool:

        previous_event = None

        # If any, get the previous event for the same device and attribute
        # than the current event

        for e in tracer.events:
            if (e.device_name == event.device_name and
                e.attribute_name == event.attribute_name and
                e.timestamp < event.timestamp):

                if (previous_event is None or
                    e.timestamp > previous_event.timestamp):
                    previous_event = e

        # If no previous event was found, return False (there is no event
        # before the target one, so none with the expected previous value)
        if previous_event is None:
            return False
        
        # If the previous event was found, check if previous value matches
        return previous_event.current_value == previous_value
    
    return predicate

def exists_event_within_timeout(
        tracer: TangoEventTracer, 
        device_name: Optional[str] = ANY,
        attribute_name: Optional[str] = ANY,
        current_value: Optional[any] = ANY,
        previous_value: Optional[any] = ANY,
        max_age: Optional[Union[int, float]] = None,
        timeout: Optional[int] = None
        ) -> Callable:
    """Custom assertpy assertion to verify that an event matching a given
    predicate occurs within a specified timeout.
    """

    # build a predicate to match the event
    event_match_predicate = build_event_predicate(
        device_name=device_name,
        attribute_name=attribute_name,
        current_value=current_value,
        max_age=max_age
    ) 

    # if previous_value is not ANY, add a predicate to ensure the event has
    # a previous value and that it matches the expected one
    if previous_value is not ANY:
        event_match_predicate = lambda e: (
            event_match_predicate(e) and 
            previous_value_predicate(tracer, previous_value)(e)
        )

    def _assertion(self):
        result = tracer.query_events(
            event_match_predicate, 
            timeout)
        
        if len(result) == 0:
            event_list = "\n".join([str(event) for event in tracer.events])
            self.error(
                f"Expected to find an event matching the predicate within "
                f"{timeout} seconds, but none was found. "
                f"Existing events:\n{event_list}")

    return _assertion




# def assert_two_events_in_order_with_timeout(tracer: TangoEventTracer, first_event_predicate, second_event_predicate, timeout):
#     """
#     Custom assertpy assertion to verify that two specific events occur in the given order within a specified timeout.

#     Args:
#         tracer (TangoEventTracer): The TangoEventTracer instance to query for events.
#         first_event_predicate (Callable[[Dict[str, any]], bool]): A predicate function for the first event.
#         second_event_predicate (Callable[[Dict[str, any]], bool]): A predicate function for the second event.
#         timeout (int): The time window in seconds to wait for the events.

#     This assertion checks if two events that satisfy the provided predicates occur in order within the given timeout period.
#     If the events do not occur in the expected order within the timeout, it lists the existing events and raises an assertion error.

#     Example Usage:
#         assert_that(tracer).assert_two_events_in_order_with_timeout(
#             lambda e: e['device'] == 'device1',
#             lambda e: e['device'] == 'device2',
#             10
#         )

#     This checks that an event from 'device1' occurs before an event from 'device2' within 10 seconds.
#     """

#     def _assertion(self):
#         start_time = time.time()
#         first_event_occurred = False

#         while time.time() - start_time < timeout:
#             with tracer.lock:
#                 if not first_event_occurred and any(first_event_predicate(event) for event in tracer.events):
#                     first_event_occurred = True

#                 if first_event_occurred and any(second_event_predicate(event) for event in tracer.events):
#                     return

#             time.sleep(0.1)  # Sleep to prevent high CPU usage

#         event_list = "\n".join([str(event) for event in tracer.events])
#         self.error(f"Expected to find two events in order within {timeout} seconds, but they were not found. Existing events:\n{event_list}")

#     return _assertion

# # Add the custom extension to assertpy
# add_extension(assert_two_events_in_order_with_timeout)
