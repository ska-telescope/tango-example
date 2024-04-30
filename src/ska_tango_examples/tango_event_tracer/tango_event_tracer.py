"""Tango proxy client which can trace events from Tango devices.

MISSION: to represent a tango proxy client that can subscribe
to change events of attributes of device proxies, store them as
they are notified (in a thread-safe way), and support queries
with timeouts to check if and when and who sent certain events.
"""

import logging
import threading
import time
from datetime import datetime, timedelta
from typing import Callable, Dict, List, Optional, Tuple

import tango

from ska_tango_examples.tango_event_tracer.received_event import ReceivedEvent


class TangoEventTracer:
    """Tango proxy client which can trace events from Tango devices.

    MISSION: to represent a tango proxy client that can subscribe to
    change events of attributes of device proxies, store them as
    they are notified (in a thread-safe way), and support queries
    with timeouts to check if and when and who sent certain events.

    This class allows you to:

    - subscribe to change events for a specific attribute of a Tango device,
    - store and access the events (in a thread-safe way),
    - query the stored events based on a predicate function and a timeout,
    - clear all stored events (in a thread-safe way), .

    Usage example 1: test where you subscribe to a device
    and query an attribute change event.

    .. code-block:: python

        def test_attribute_change():

            tracer = TangoEventTracer()
            tracer.subscribe_to_device("sys/tg_test/1", "attribute1")

            # do something that triggers the event
            # ...

            assert len(tracer.query_events(
                lambda e: e.device_name == "sys/tg_test/1",
                timeout=10)) == 1

    """

    # Sleep time for the query loops
    QUERY_SLEEP_TIME = 0.1

    def __init__(self) -> None:
        """Initialize the event collection and the lock."""

        # set of received events
        self._events: List[ReceivedEvent] = []

        # dictionary of subscription ids (foreach device proxy
        # are stored the subscription ids of the subscribed attributes)
        self._subscription_ids: Dict[tango.DeviceProxy, List[int]] = {}

        # lock for thread safety
        self.lock = threading.Lock()

    def __del__(self) -> None:
        """Teardown the object and unsubscribe from all subscriptions.

        (else they will be kept alive and they may cause segfaults)
        """
        self.unsubscribe_all()
        self.clear_events()

    # #############################
    # Access to stored events

    @property
    def events(self) -> List[ReceivedEvent]:
        """Return a copy of the currently stored events (thread-safe)."""

        # check if this process is currently holding the lock
        if self.lock.locked():
            return self._events.copy()

        # if not, acquire the lock and release it after copying the events
        with self.lock:
            return self._events.copy()

    def clear_events(self) -> None:
        """Clear all stored events."""
        with self.lock:
            self._events.clear()

    # #############################
    # Subscription and
    # event handling

    def subscribe_to_device(
        self,
        device_name: str,
        attribute_name: str,
        dev_factory: Optional[Callable[[str], tango.DeviceProxy]] = None,
        set_polling_period_ms: Optional[int] = 50,
    ) -> None:
        """Subscribe to change events for a Tango device attribute.

        :param device_name: The name of the Tango target device.
        :param attribute_name: The name of the attribute to subscribe to.
        :param dev_factory: A device factory method to get the device proxy.
            If not specified, the device proxy is created using the
            default constructor ::class::`tango.DeviceProxy`.
        :param set_polling_period_ms: The polling period in milliseconds to
            set for the attribute (optional). If not specified, the attribute
            is not polled and it is used the eventually already set
            polling_period.

        :raises tango.DevFailed: If the subscription fails. A common reason
            for this is that the attribute is not pollable and therefore not
            subscribable. An alternative reason is that the device cannot be
            reached or it has no such attribute.
        """

        # TODO: is it really necessary?
        # alternative: use device proxy directly as input parameter
        if dev_factory is None:
            dev_factory = tango.DeviceProxy

        device_proxy = dev_factory(device_name)

        # set polling period if specified
        if set_polling_period_ms is not None:
            device_proxy.poll_attribute(attribute_name, set_polling_period_ms)

        # subscribe to the change event
        device_proxy.subscribe_event(
            attribute_name,
            tango.EventType.CHANGE_EVENT,
            self._event_callback,
        )

    def _event_callback(self, event: tango.EventData) -> None:
        """Store a Tango event in a thread-safe way.

        :param event: The event data object.
        """
        if event.err:
            logging.error("Error in event callback: %s", event.errors)
            return

        # TODO: why not storing the event as a Tango EventData object?
        # Maybe in a key-value structure where the key is the datetime
        # Why? No duplicate data types, programmers may formulate queries
        # based on the standard Tango EventData object
        # (they know it well and it's already documented)
        with self.lock:
            self._events.append(ReceivedEvent(event))

    def unsubscribe_all(self) -> None:
        """Unsubscribe from all subscriptions."""
        with self.lock:
            for device_proxy, device_sub_ids in self._subscription_ids.items():
                for subscription_id in device_sub_ids:
                    try:
                        device_proxy.unsubscribe_event(subscription_id)
                    except tango.DevFailed as df:
                        logging.warning(
                            "Error while unsubscribing from event: %s", df
                        )
            self._subscription_ids.clear()

    # #############################
    # Querying stored events

    def query_events(
        self,
        predicate: Callable[[ReceivedEvent], bool],
        timeout: Optional[int] = None,
        target_n_events: int = 1,
    ) -> List[ReceivedEvent]:
        """Query stored an future events with a predicate and a timeout.

        :param predicate: A function that takes an event as input and returns.
            True if the event matches the desired criteria.
        :param timeout: The time window in seconds to wait for a matching event
            (optional). If not specified, the method returns immediately.
        :param target_n_events: How many events do you expect to find with this
            query? If in past events you don't reach the target number, the
            method will wait till you reach the target number or you reach
            the timeout. Defaults to 1 so in case of a waiting loop, the method
            will return the first event.

        :return: all matching events within the timeout
            period, an empty list otherwise.
        """
        end_time = (
            datetime.now() + timedelta(seconds=timeout)
            if timeout is not None
            else None
        )

        matching_events = []

        def _get_new_events() -> list:
            events_snapshot = self.events
            return [
                event
                for event in events_snapshot
                if predicate(event)
                and self._is_event_within_time(event, timeout)
                and event not in matching_events
            ]

        # wait for future events
        while True:
            matching_events += _get_new_events()

            # if I got the expected nr events I stop
            if len(matching_events) >= target_n_events:
                return matching_events

            # If timeout is reached or there is no timeout, return what I have
            if end_time is None or datetime.now() >= end_time:
                return matching_events

            time.sleep(
                self.QUERY_SLEEP_TIME
            )  # Sleep to prevent high CPU usage

    def query_event_pairs(
        self,
        predicate: Callable[[ReceivedEvent, ReceivedEvent], bool],
        timeout: Optional[int] = None,
        target_n_pairs: int = 1,
        is_pair_sorted: bool = False,
    ) -> List[Tuple[ReceivedEvent, ReceivedEvent]]:
        """Query for pairs of events that satisfy a given predicate.

        :param predicate: A function that takes a pair of events and returns
                True if they match the condition.
        :param timeout: The time window in seconds to wait for a matching
                pair of events (optional). If not specified, the method
                returns immediately.
        :param target_n_pairs: How many pairs of events do you expect to find
            with this query? If in past events you don't reach the target
            number, the method will wait till you reach the target number
            or you reach the timeout. Defaults to 1, so in case of a
            waiting loop, the method will return the first pair of events.
        :param is_pair_sorted: If True, the pairs are sorted before being
            returned. This is useful when the order of the events in the
            pair matters. Defaults to False.

        :return: A list of tuples, where each tuple contains a pair of
            matching events (event1, event2). If specified, the pair
            elements are sorted by reception time.
        """
        end_time = (
            datetime.now() + timedelta(seconds=timeout)
            if timeout is not None
            else None
        )

        matching_pairs = []

        def _get_new_pairs() -> Tuple[ReceivedEvent, ReceivedEvent]:
            events_snapshot = self.events
            return [
                # we want to return pairs of events that satisfy a predicate
                (event1, event2)
                for event1 in events_snapshot
                for event2 in events_snapshot
                if predicate(event1, event2)
                # avoid self-pairs
                and event1 != event2
                # check if the events are within the timeout
                and self._is_event_within_time(event1, timeout)
                and self._is_event_within_time(event2, timeout)
                # avoid duplicates
                and (event1, event2) not in matching_pairs
                and (event2, event1) not in matching_pairs
                # if required, ensure the order of the pair
                and (
                    not is_pair_sorted
                    or event1.reception_time < event2.reception_time
                )
            ]

        # wait for future event pairs
        while True:
            matching_pairs += _get_new_pairs()

            # if I got the expected nr of pairs I stop
            if len(matching_pairs) >= target_n_pairs:
                return matching_pairs

            # If timeout is reached or there is no timeout, return what I have
            if end_time is None or datetime.now() >= end_time:
                return matching_pairs

            time.sleep(
                self.QUERY_SLEEP_TIME
            )  # Sleep to prevent high CPU usage

    # TODO: two important questions:
    # - should we separate this from the timeout?
    #   * Now I can query just past events within a maximum time window
    #     (timeout=None + e.reception_age() < MAX_TIME_WINDOW)
    #   * I can also query just future events within a maximum time window
    #     (timeout=TIMEOUT + e.reception_age() < VERY_SMALL_TIME_WINDOW)
    #   * ... but is this understandable for the user?
    # - in EventData I have a server timestamp, should we use that because
    #   it's more reliable than the reception time? Or should we use both?
    @staticmethod
    def _is_event_within_time(event: ReceivedEvent, timeout) -> bool:
        """Check if the event is within the timeout window."""
        return timeout is None or event.reception_age() < timeout
