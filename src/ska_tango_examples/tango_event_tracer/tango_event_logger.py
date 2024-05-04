

import logging
import threading
import time
from typing import Any, Callable, Dict, List, Optional

import tango

from ska_tango_examples.tango_event_tracer.received_event import ReceivedEvent


DEFAULT_LOG_ALL_EVENTS = lambda _: True
DEFAULT_LOG_MESSAGE_BUILDER = lambda e: \
    f"At {e.reception_time}, {e.device_name} {e.attribute_name} " + \
    f"changed to {e.current_value}."

class TangoEventLogger:
    """A Tango event logger that logs change events from Tango devices.

    The logger subscribes to change events from a Tango device attribute and
    logs them using a filtering rule and a message builder. By default, all
    events are logged in a human-readable format.

    The logger can be used to log events from multiple devices and attributes.

    Usage example 1: Given a device A, with two attributes X and Y, log all
    change events from X and only the events from Y which have a value greater
    than 10.

    .. code-block:: python

        logger = TangoEventLogger()
        logger.log_events_from_Device("A", "X")
        logger.log_events_from_Device(
            "A", "Y",
            filtering_rule=lambda e: e.current_value > 10
        )

    Usage example 2: Given the device A of the previous example, log all change
    events from Y, but costumize the message to say if the value > 10 or
    not.

    .. code-block:: python

        logger = TangoEventLogger()
        logger.log_events_from_Device(
            "A", "Y",
            message_builder=lambda e: 
                DEFAULT_LOG_MESSAGE_BUILDER(e) + \
                f"(Value > 10: {e.current_value > 10})"
        )

    """


    def __init__(self):
        """Initialise the Tango event logger."""
        self._subscription_ids: Dict[tango.DeviceProxy, List[int]] = {}
        self.lock = threading.Lock()

    def __del__(self):
        """Unsubscribe from all events when the logger is deleted."""
        self.unsubscribe_all()


    def log_events_from_device(
        self,
        device_name: str,
        attribute_name: str,
        filtering_rule: Callable[[ReceivedEvent], bool] = \
            DEFAULT_LOG_ALL_EVENTS,
        message_builder: Callable[[ReceivedEvent], str] = \
            DEFAULT_LOG_MESSAGE_BUILDER,
        dev_factory: Optional[Callable[[str], tango.DeviceProxy]] = None,
        set_polling_period_ms: Optional[int] = 50,
    ) -> None:
        """Log change events from a Tango device attribute.

        :param device_name: The name of the Tango target device.
        :param attribute_name: The name of the attribute to subscribe to.
        :param filtering_rule: A function that takes a received event and
            returns whether it should be logged or not. By default, all events
            are logged.
        :param message_builder: A function that takes a received event and
            returns the (str) message to log. By default, it logs the event in a
            human-readable format.
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

        
        def _callback(event_data: tango.EventData):
            """Callback to log the received event."""
            received_event = ReceivedEvent(event_data)

            # if event passes the filter, log it using the message builder
            if filtering_rule(received_event):
                logging.info(message_builder(received_event))

        # subscribe to the change event
        subid = device_proxy.subscribe_event(
            attribute_name,
            tango.EventType.CHANGE_EVENT,
            _callback
        )

        # store the subscription id
        with self.lock:
            if device_proxy not in self._subscription_ids:
                self._subscription_ids[device_proxy] = []
            self._subscription_ids[device_proxy].append(subid)

    def unsubscribe_all(self):
        """Unsubscribe from all events."""
        with self.lock:
            for device_proxy, subids in self._subscription_ids.items():
                for subid in subids:
                    device_proxy.unsubscribe_event(subid)
            self._subscription_ids.clear()

    