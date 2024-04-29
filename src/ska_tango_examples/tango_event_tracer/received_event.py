"""A Tango event which has been received by the ::class::`TangoEventTracer`.
"""

from datetime import datetime

import tango


class ReceivedEvent:
    """A Tango event which has been received by the ::class::`TangoEventTracer`.

    This class is a wrapper around the Tango event data, which allows to
    access the most relevant information in a more user-friendly way. The main
    attributes are:

    - ::property::`device`: the device proxy that sent the event,
    - ::property::`device_name`: the name of the device that sent the event,
    - ::property::`attribute`: the full name of the attribute that sent the
        event,
    - ::property::`current_value`: the new value of the attribute when
        the event was sent.

    Other than that, the event data contains also the reception timestamp.

    If you need to access the full event data, you can use the `event_data`
    attribute to access the original Tango event data.

    You can use this class interface to build predicates for the
    ::method::`TangoEventTracer.query_events` method, i.e.:

    .. code-block:: python

        query_result = tracer.query_events(
            lambda e: e.device_name == "sys/tg_test/1",
                    and "attribute1" in e.attribute,
                    and e.current_value == 10,
            timeout=10)

    """

    def __init__(self, event_data: tango.EventData):
        """Initialise the ReceivedEvent with the event data.

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
        return (
            f"ReceivedEvent("
            f"device_name='{self.device_name}', "
            f"attribute='{self.attribute}', "
            f"current_value={self.current_value}), "
            f"timestamp={self.timestamp})"
        )

    @property
    def device(self) -> tango.DeviceProxy:
        """The device proxy that sent the event."""
        return self.event_data.device

    @property
    def device_name(self) -> str:
        """The name of the device that sent the event."""
        return self.event_data.device.dev_name()

    @property
    def attribute(self) -> str:
        """The full name of the attribute that sent the event.

        NOTE: This full name conainst the whole path to device, e.g.:
        'http://sys/tg_test/1/attribute1'

        TODO: Find a reliable way to have just the short name, e.g. 'attribute1'
        """
        return self.event_data.attr_name

    @property
    def current_value(self):
        """The new value of the attribute when the event was sent."""
        return self.event_data.attr_value.value
