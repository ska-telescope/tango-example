"""Basic custom event-based assertions for ::class::`TangoEventTracer`.

This module provides some example of basic custom ::mod::`assertpy` assertions
to be used with ::class::`TangoEventTracer` instances. These assertions can be
used to verify properties about the events captured by the tracer.

Essentially they are query calls to the tracer, within
a timeout, to check if the are events which match an expected more or less
complex predicate.

You can and you are encouraged to take those assertions as a starting point
to create more complex ones, as needed by your test cases. If you want to do
that it is suggested to check ::mod::`assertpy` documentation to understand how
to create custom assertions (https://assertpy.github.io/docs.html).

Usage example:

.. code-block:: python

    from assertpy import assert_that, add_extension
    from ska_tango_examples.tango_event_tracer.tango_event_tracer import (
        TangoEventTracer
    )
    from ska_tango_examples.tango_event_tracer.predicates_and_assertions.event_assertions import (
        exists_event_within_timeout
    )

    # IMPORTANT: Add the custom extension to assertpy
    add_extension(exists_event_within_timeout)

    # ...

    def test_event_occurs_within_timeout(sut, tracer: TangoEventTracer):

        tracer.subscribe_to_device("devname", "attrname")

        # ... do something that triggers the event

        # Check that an attr change event happens within 10 seconds
        assert_that(tracer).exists_event_within_timeout(
            device_name="devname",
            attribute_name="attrname",
            current_value="new_value",
            previous_value="old_value",
            timeout=10
        )
"""


from typing import Optional, Union

from ska_tango_examples.tango_event_tracer.predicates_and_assertions.predicates import (
    ANY,
    event_has_previous_value,
    event_matches_parameters,
)
from ska_tango_examples.tango_event_tracer.tango_event_tracer import (
    TangoEventTracer,
)


def exists_event_within_timeout(
    self,
    device_name: Optional[str] = ANY,
    attribute_name: Optional[str] = ANY,
    current_value: Optional[any] = ANY,
    previous_value: Optional[any] = ANY,
    max_age: Optional[Union[int, float]] = None,
    timeout: Optional[int] = None,
):
    """Custom assertpy assertion to verify that an event matching a given
    predicate occurs within a specified timeout.
    """

    # check self has a tracer object
    if not hasattr(self, "val") or not isinstance(self.val, TangoEventTracer):
        raise ValueError(
            "The TangoEventTracer instance must be stored in the 'val' attribute"
            " of the assertpy context. Try using the 'assert_that' method with"
            " the TangoEventTracer instance as argument.\n"
            "Example: assert_that(tracer).exists_event_within_timeout(...)"
        )

    tracer = self.val

    # query and check if any event matches the predicate
    result = tracer.query_events(
        lambda e:
        # the event match passed values
        event_matches_parameters(
            target_event=e,
            device_name=device_name,
            attribute_name=attribute_name,
            current_value=current_value,
            max_age=max_age,
        )
        and (
            # if given a previous value, the event must have a previous
            # event and tue previous value must match
            event_has_previous_value(
                target_event=e, tracer=tracer, previous_value=previous_value
            )
            if previous_value is not ANY
            else True
        ),
        timeout=timeout,
    )

    if len(result) == 0:
        event_list = "\n".join([str(event) for event in tracer.events])
        self.error(
            f"Expected to find an event matching the predicate within "
            f"{timeout} seconds, but none was found. "
            f"Existing events:\n{event_list}"
        )


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
