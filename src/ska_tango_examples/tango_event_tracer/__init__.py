"""Test tools to trace Tango events and make assertions.

This module contains a set of tools to trace events from Tango devices
and create test assertions statements based on those events. The goal
is to write (integration) tests in a more event-based way, where:

1. you subscribe to a device and attribute,
2. you trigger an event,
3. you assert that the event was captured (and check its details).

The primary tool is the `TangoEventTracer` class,
which can be seen as a thread-safe event collector that subscribes
to change events for a specific attribute of a Tango device and then lets
you query those events using a predicate and a timeout.

Starting from that you can build more
complex `assertpy` custom assertions.
"""

from .received_event import ReceivedEvent
from .tango_event_logger import (
    DEFAULT_LOG_ALL_EVENTS,
    DEFAULT_LOG_MESSAGE_BUILDER,
    TangoEventLogger,
)
from .tango_event_tracer import TangoEventTracer

__all__ = [
    "TangoEventTracer",
    "TangoEventLogger",
    "ReceivedEvent",
    "DEFAULT_LOG_ALL_EVENTS",
    "DEFAULT_LOG_MESSAGE_BUILDER",
]
