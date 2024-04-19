import logging
from datetime import datetime

import tango


class TangoEventLogger:
    """
    MISSION: to log change events of selected devices and attributes. We expect this object
    to be used in test scripts to monitor changes in state and other attributes of relevant devices of the SUT.

    # Create an instance of the TangoEventLogger
    event_logger = TangoEventLogger()

    # Subscribe to attribute change events on multiple devices and attributes
    event_logger.subscribe("device1/name", "Attribute1")
    event_logger.subscribe("device2/name", "Attribute2")

    # Unsubscribe from the events on a specific device and attribute
    event_logger.unsubscribe("device1/name", "Attribute1")
    event_logger.unsubscribe("device2/name", "Attribute2")


    """

    def __init__(self):
        """
        Initializes the TangoEventLogger.
        """
        # Configure logging to write to stdout
        logging.basicConfig(
            level=logging.DEBUG,
            format="%(asctime)s - %(message)s",
            handlers=[logging.StreamHandler()],
        )
        self.logger = logging.getLogger(__name__)
        self.subscriptions = {}

    def _log_info(self, message):
        """
        Logs an info message.

        :param message: The message to log.
        """
        self.logger.info(message)

    def _log_error(self, message):
        """
        Logs an error message.

        :param message: The error message to log.
        """
        self.logger.error(message)

    def log_event(self, device_name, attribute_name, timestamp, value):
        """
        Logs a normal attribute change event.

        :param device_name: The name of the device.
        :param attribute_name: The name of the attribute.
        :param timestamp: The timestamp of the event.
        :param value: The new value of the attribute.
        """
        formatted_time = datetime.fromtimestamp(timestamp).strftime(
            "%Y-%m-%d %H:%M:%S"
        )

        self._log_info(
            f"Device: {device_name}, Attribute: {attribute_name}, Time: {formatted_time}, New value: {value}"
        )

    def log_error_event(self, device_name, attribute_name, timestamp, error):
        """
        Logs an error event.

        :param device_name: The name of the device.
        :param attribute_name: The name of the attribute.
        :param timestamp: The timestamp of the event.
        :param error: The error information.
        """
        formatted_time = datetime.fromtimestamp(timestamp).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        self._log_error(
            f"Error in change event for {device_name}/{attribute_name} at {formatted_time}: {error}"
        )

    def attribute_change_callback(self, event, device_name, attribute_name):
        """
        Callback function that gets called when there's a change in the attribute.

        :param event: The event object containing the change details.
        :param device_name: The name of the device from which the event originated.
        :param attribute_name: The name of the attribute that has changed.
        """
        if event.err:
            self.log_error_event(
                device_name,
                attribute_name,
                event.reception_date.totime(),
                event.errors,
            )
        else:
            self.log_event(
                device_name,
                attribute_name,
                event.reception_date.totime(),
                event.attr_value.value,
            )

    def subscribe(self, device_name, attribute_name="State"):
        """
        Subscribe to change events of the specified attribute of the Tango device.

        :param device_name: Name of the Tango device.
        :param attribute_name: Name of the attribute to subscribe to for change events.
        """
        try:
            device_proxy = tango.DeviceProxy(device_name)
            event_id = device_proxy.subscribe_event(
                attribute_name,
                tango.EventType.CHANGE_EVENT,
                self.attribute_change_callback,
            )
            self.subscriptions[(device_name, attribute_name)] = event_id
            self._log_info(
                f"Subscribed to {attribute_name} changes on {device_name}"
            )
        except tango.DevFailed as e:
            self._log_error(
                f"Failed to subscribe to {attribute_name} changes on {device_name}: {e}"
            )

    def unsubscribe(self, device_name, attribute_name):
        """
        Unsubscribe from the attribute change events.

        :param device_name: Name of the Tango device.
        :param attribute_name: Name of the attribute to unsubscribe from.
        """
        key = (device_name, attribute_name)
        if key in self.subscriptions:
            try:
                device_proxy = tango.DeviceProxy(device_name)
                device_proxy.unsubscribe_event(self.subscriptions[key])
                self._log_info(
                    f"Unsubscribed from {attribute_name} changes on {device_name}"
                )
                del self.subscriptions[key]
            except tango.DevFailed as e:
                self._log_error(
                    f"Failed to unsubscribe from {attribute_name} on {device_name}: {e}"
                )
