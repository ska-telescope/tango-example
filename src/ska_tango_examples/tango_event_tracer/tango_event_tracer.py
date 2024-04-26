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
        target_n_events: int = 1,
    ) -> List[dict]:
        """Query stored an future events with a predicate and a timeout.

        :param predicate: A function that takes an event as input and returns.
            True if the event matches the desired criteria.
        :param timeout: The time window in seconds to wait for a matching event
            (optional). If not specified, the method returns immediately.
        :param target_n_events: How many events do you expect to find with this
            query? If in past events you don't reach the target number, the
            method will wait till you reach the target number or you reach
            the timeout. Defaults to 1.

        :return: all matching events within the timeout
            period, an empty list otherwise.
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

        matching_events = []

        def _get_new_events() -> list:
            return [
                event
                for event in self.events
                if predicate(event)
                and _is_event_within_time(event)
                and event not in matching_events
            ]

        # wait for future events
        while True:
            with self.lock:

                # add new (in-time) events which matches the predicate
                matching_events += _get_new_events()

            # if I got the expected nr events I stop
            if len(matching_events) >= target_n_events:
                return matching_events

            # If timeout is reached or there is no timeout, return what I have
            if end_time is None or datetime.now() >= end_time:
                return matching_events

            time.sleep(0.1)  # Sleep to prevent high CPU usage

    def clear_events(self) -> None:
        """Clear all stored events."""
        with self.lock:
            self.events.clear()
