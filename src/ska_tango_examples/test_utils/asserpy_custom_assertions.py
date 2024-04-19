# what follows are examples of assertpy custom assertions that take advantage of
# the tracer class

import time

from assertpy import add_extension  # , assert_that

from ska_tango_examples.test_utils.tango_event_tracer import TangoEventTracer


def assert_event_occurs_within_timeout(
    tracer: TangoEventTracer, predicate, timeout
):
    """
    Custom assertpy assertion to verify that an event matching a given predicate occurs within a specified timeout.

    Args:
        tracer (TangoEventTracer): The TangoEventTracer instance to query for events.
        predicate (Callable[[Dict[str, any]], bool]): A function that takes an event as input and returns True if the event matches the desired criteria.
        timeout (int): The time window in seconds to wait for a matching event.

    This assertion checks if an event that satisfies the provided predicate occurs within the given timeout period.
    If no such event is found within the timeout, it lists the existing events and raises an assertion error.

    Example Usage:
        assert_that(tracer).assert_event_occurs_within_timeout(lambda e: e['device'] == 'device1' and e['current_value'] > 50, 10)

    The above example asserts that an event from 'device1' with a current value greater than 50 should occur within 10 seconds.
    """

    def _assertion(self):
        result = tracer.query_events(predicate, timeout)
        if not result:
            event_list = "\n".join([str(event) for event in tracer.events])
            self.error(
                f"Expected to find an event matching the predicate within {timeout} seconds, but none was found. Existing events:\n{event_list}"
            )

    return _assertion


# Add the custom extension to assertpy
add_extension(assert_event_occurs_within_timeout)


def assert_two_events_in_order_with_timeout(
    tracer: TangoEventTracer,
    first_event_predicate,
    second_event_predicate,
    timeout,
):
    """
    Custom assertpy assertion to verify that two specific events occur in the given order within a specified timeout.

    Args:
        tracer (TangoEventTracer): The TangoEventTracer instance to query for events.
        first_event_predicate (Callable[[Dict[str, any]], bool]): A predicate function for the first event.
        second_event_predicate (Callable[[Dict[str, any]], bool]): A predicate function for the second event.
        timeout (int): The time window in seconds to wait for the events.

    This assertion checks if two events that satisfy the provided predicates occur in order within the given timeout period.
    If the events do not occur in the expected order within the timeout, it lists the existing events and raises an assertion error.

    Example Usage:
        assert_that(tracer).assert_two_events_in_order_with_timeout(
            lambda e: e['device'] == 'device1',
            lambda e: e['device'] == 'device2',
            10
        )

    This checks that an event from 'device1' occurs before an event from 'device2' within 10 seconds.
    """

    def _assertion(self):
        start_time = time.time()
        first_event_occurred = False

        while time.time() - start_time < timeout:
            with tracer.lock:
                if not first_event_occurred and any(
                    first_event_predicate(event) for event in tracer.events
                ):
                    first_event_occurred = True

                if first_event_occurred and any(
                    second_event_predicate(event) for event in tracer.events
                ):
                    return

            time.sleep(0.1)  # Sleep to prevent high CPU usage

        event_list = "\n".join([str(event) for event in tracer.events])
        self.error(
            f"Expected to find two events in order within {timeout} seconds, but they were not found. Existing events:\n{event_list}"
        )

    return _assertion


# Add the custom extension to assertpy
add_extension(assert_two_events_in_order_with_timeout)
