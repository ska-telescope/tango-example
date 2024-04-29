"""A Tango event which has been received by the ::class::`TangoEventTracer`.
"""

from datetime import datetime


class ReceivedEvent:
    """A Tango event which has been received by the ::class::`TangoEventTracer`."""

    def __init__(self, event_data):
        """Initialise the ReceivedEvent.

        :param event_data (EventData): The event data.
        """

        # Store the whole event data to allow further inspection
        self.event_data = event_data

        # Build retro-compatible attributes
        self.timestamp = datetime.now()
        # self.device = event_data.device
        # self.attribute = event_data.attr_name
        # self.current_value = event_data.attr_value.value

    def __str__(self):
        return f"ReceivedEvent({self._event_data})"

    @property
    def device(self):
        return self.event_data.device

    @property
    def device_name(self):
        return self.event_data.device.dev_name()

    @property
    def attribute(self):
        return self.event_data.attr_name

    @property
    def current_value(self):
        return self.event_data.attr_value.value
