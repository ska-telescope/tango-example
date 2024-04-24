"""Tango proxy client which can trace events from Tango devices.

MISSION: to represent a tango proxy client that can subscribe
to change events of attributes of device proxies, store them as
they are notified (in a thread-safe way), and support queries
with timeouts to check if and when and who sent certain events.
"""

import threading
import time
from datetime import datetime, timedelta
from typing import Any, Callable, Dict, List, Optional

import tango


class TangoEventTracer:
    """Tango proxy client which can trace events from Tango devices.

    MISSION: to represent a tango proxy client that can subscribe to
    change events of attributes of device proxies, store them as
    they are notified (in a thread-safe way), and support queries
    with timeouts to check if and when and who sent certain events.

    This class allows you to:

    - subscribe to change events for a specific attribute of a Tango device,
    - store the events in a thread-safe way,
    - query the stored events based on a predicate function and a timeout,
    - clear all stored events.

    Usage example 1: test where you subscribe to a device
    and query an attribute change event.

    .. code-block:: python

        def test_attribute_change():

            tracer = TangoEventTracer()
            tracer.subscribe_to_device("sys/tg_test/1", "attribute1")

            # do something that triggers the event
            # ...

            assert tracer.query_events(
                lambda e: e["device"] == "sys/tg_test/1",
                10)

    """

    def __init__(self) -> None:
        """Initialize the event collection and the lock."""
        self.events: List[Dict[str, Any]] = []
        self.lock = threading.Lock()

    def _event_callback(self, event: tango.EventData) -> None:
        """Store a Tango event in a thread-safe way.

        :param event: The event data object.
        """
        if event.err:
            print(f"Error in event callback: {event.errors}")
            return

        # TODO: why not storing the event as a Tango EventData object?
        # Maybe in a key-value structure where the key is the datetime
        # Why? No duplicate data types, programmers may formulate queries
        # based on the standard Tango EventData object
        # (they know it well and it's already documented)
        with self.lock:
            self.events.append(
                {
                    "timestamp": datetime.now(),
                    "device": event.device,
                    "attribute": event.attr_name,
                    "current_value": event.attr_value.value,
                    # NOTE: I guess we don't have it this way
                    # "previous_value": event.attr_value.prev_value,
                }
            )

    def subscribe_to_device(
        self, device_name: str, attribute_name: str
    ) -> None:
        """Subscribe to change events for a Tango device attribute.

        :param device_name: The name of the Tango target device.
        :param attribute_name: The name of the attribute to subscribe to.

        :raises tango.DevFailed: If the subscription fails. A common reason
            for this is that the attribute is not pollable and therefore not
            subscribable. An alternative reason is that the device cannot be
            reached or it has no such attribute.
        """
        device_proxy = tango.DeviceProxy(device_name)
        device_proxy.subscribe_event(
            attribute_name,
            tango.EventType.CHANGE_EVENT,
            self._event_callback,
        )

    def query_events(
        self,
        predicate: Callable[[Dict[str, Any]], bool],
        timeout: Optional[int] = None,
    ) -> bool:
        """Query stored an future events with a predicate and a timeout.

        :param predicate: A function that takes an event as input and returns.
            True if the event matches the desired criteria.
        :param timeout: The time window in seconds to wait for a matching event
            (optional). If not specified, the method returns immediately.

        :return: True if a matching event is found within the timeout
            period, False otherwise.
        """
        end_time = (
            datetime.now() + timedelta(seconds=timeout)
            if timeout is not None
            else None
        )

        start_time = (
            datetime.now() - timedelta(seconds=timeout)
            if timeout is not None
            else None
        )

        def _is_event_within_time(event: Dict[str, Any]) -> bool:
            return (
                start_time is None
                or start_time <= event["timestamp"] <= end_time
            )

        # wait for future events
        while True:
            with self.lock:

                # check if any (in-time) event matches the predicate
                if any(
                    predicate(event) and _is_event_within_time(event)
                    for event in self.events
                ):
                    return True

            # If timeout is reached, no event was found
            # TODO: a logic choice would be to return
            # False if no event is found and it's not
            # given any timeout (i.e. if not given, all past
            # events should be considered but any of the future ones)
            # Why? Because if no timeout is given and no event is found
            # if may began an infinite wait
            # Maybe timeout may be broken in two different parameters:
            # - max_age: the maximum age the event may have to be
            # considered
            #       in a query (default: None, all events are considered)
            # - timeout: the time to wait for a future event
            #       (default: the sleep time,
            #       if > max_age, max_age can be used)
            if end_time is not None and datetime.now() >= end_time:
                return False

            time.sleep(0.1)  # Sleep to prevent high CPU usage

    def clear_events(self) -> None:
        """Clear all stored events."""
        with self.lock:
            self.events.clear()
