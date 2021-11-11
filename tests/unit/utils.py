from queue import Queue
from typing import Any

import tango


class LRCAttributesStore:
    """Utility class to keep track of LRC attribute changes."""

    def __init__(self) -> None:
        """Create the queues."""
        self.queues = {}
        self.event_name_map = {}
        for attribute in [
            "longRunningCommandsInQueue",
            "longRunningCommandStatus",
            "longRunningCommandProgress",
            "longRunningCommandIDsInQueue",
            "longRunningCommandResult",
        ]:
            self.queues[attribute] = Queue()
            self.event_name_map[attribute.lower()] = attribute

    def store_push_event(self, attribute_name: str, value: Any):
        """Store attribute changes as they change.

        :param attribute_name: a valid LCR attribute
        :type attribute_name: str
        :param value: The value of the attribute
        :type value: Any
        """
        assert attribute_name in self.queues
        self.queues[attribute_name].put_nowait(value)

    def push_event(self, ev: tango.EventData):
        """Store attribute events

        :param ev: Tango event
        :type ev: tango.EventData
        """
        attribute_name = ev.attr_name.split("/")[-1].replace("#dbase=no", "")
        if attribute_name in self.event_name_map:
            if ev.attr_value:
                self.queues[self.event_name_map[attribute_name]].put_nowait(
                    ev.attr_value.value
                )

    def get_attribute_value(
        self, attribute_name: str, fetch_timeout: float = 2.0
    ):
        """Read a value from the queue.

        :param attribute_name: a valid LCR attribute
        :type attribute_name: str
        :param fetch_timeout: How long to wait for a event, defaults to 2.0
        :type fetch_timeout: float, optional
        :return: An attribute value fromthe queue
        :rtype: Any
        """
        return self.queues[attribute_name].get(timeout=fetch_timeout)
