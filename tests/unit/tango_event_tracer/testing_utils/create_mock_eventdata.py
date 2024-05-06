"""Tools to create mock data"""

from unittest.mock import MagicMock

import tango


def create_mock_eventdata(dev_name, attribute, value, error=False):
    """Create a mock Tango event data object.

    :param device: The device name.
    :param attribute: The attribute name.
    :param value: The current value.
    :param error: Whether the event is an error event, default is False.
    :return: A mock Tango event data object.
    """

    # Create a mock device
    mock_device = MagicMock(spec=tango.DeviceProxy)
    mock_device.dev_name.return_value = dev_name

    # Create a mock attribute value
    mock_attr_value = MagicMock()
    mock_attr_value.value = value
    mock_attr_value.name = attribute

    # Create a mock event
    mock_event = MagicMock(spec=tango.EventData)
    mock_event.device = mock_device
    mock_event.attr_name = (
        f"tango://127.0.0.1:8080/{dev_name}/{attribute}#dbase=no"
    )
    mock_event.attr_value = mock_attr_value
    mock_event.err = error

    return mock_event
