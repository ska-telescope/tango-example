import threading
import time
from datetime import datetime, timedelta
from typing import Callable, Dict, List, Optional

import tango


class TangoEventTracer:
    """
    MISSION: to represent a tango proxy client that can subscribe to change events of attributes
    of device proxies, store them as they are notified (in a thread-safe way), and support queries
    with timeouts to check if and when and who sent certain events.

    Particularly useful with a set of assertpy custom assertions.
    """

    def __init__(self):
        """
        Initialize the TangoEventTracer.
        """
        self.events: List[Dict[str, any]] = []
        self.lock = threading.Lock()

    def _event_callback(self, event: tango.EventData) -> None:
        """
        Callback function for capturing change events from Tango devices.
        """
        try:
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
        except Exception as e:
            print(f"Exception in event callback: {e}")

    def subscribe_to_device(
        self, device_name: str, attribute_name: str
    ) -> None:
        """
        Subscribe to change events for a specific attribute of a Tango device.
        """
        try:
            device_proxy = tango.DeviceProxy(device_name)
            device_proxy.subscribe_event(
                attribute_name,
                tango.EventType.CHANGE_EVENT,
                self._event_callback,
            )
        except tango.DevFailed as e:
            print(
                f"Failed to subscribe to {device_name}/{attribute_name}: {e}"
            )
        except Exception as e:
            print(f"Unexpected exception during subscription: {e}")

    def query_events(
        self,
        predicate: Callable[[Dict[str, any]], bool],
        timeout: Optional[int] = None,
    ) -> bool:
        """
        Query stored events based on a predicate function. Optionally,
        wait for a matching event until a timeout.



        Args:
            predicate: A function that takes an event as input and returns True if the event matches the desired criteria.
            timeout: The time window in seconds to wait for a matching event (optional). If not specified, the method returns immediately.

        Returns:
            True if a matching event is found within the timeout period, False otherwise.
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

        def _is_event_within_time(event: Dict[str, any]) -> bool:
            return (
                start_time is None
                or start_time <= event["timestamp"] <= end_time
            )

        # wait for future events
        while True:
            try:
                with self.lock:

                    # check if any (in-time) event matches the predicate
                    if any(
                        [
                            predicate(event) and _is_event_within_time(event)
                            for event in self.events
                        ]
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
                # - max_age: the maximum age the event may have to be considered
                #       in a query (default: None, all events are considered)
                # - timeout: the time to wait for a future event
                #       (default: the sleep time,
                #       if > max_age, max_age can be used)
                if timeout is not None and datetime.now() >= end_time:
                    return False

                time.sleep(0.1)  # Sleep to prevent high CPU usage
            except Exception as e:
                # Log or handle the exception as appropriate
                print(f"Error while querying events: {e}")

    def clear_events(self) -> None:
        """
        Clear all stored events.
        """
        with self.lock:
            self.events.clear()
