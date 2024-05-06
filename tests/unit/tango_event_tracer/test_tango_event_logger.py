from unittest.mock import ANY, patch

import pytest
from assertpy import assert_that
import tango

from src.ska_tango_examples.tango_event_tracer import (
    DEFAULT_LOG_ALL_EVENTS,
    DEFAULT_LOG_MESSAGE_BUILDER,
    TangoEventLogger,
)
from tests.unit.tango_event_tracer.testing_utils import create_mock_eventdata

LOGGING_PATH = (
    "src.ska_tango_examples.tango_event_tracer.tango_event_logger.logging"
)


class TestTangoEventLogger:
    @pytest.fixture
    def logger(self):
        """Return a TangoEventLogger instance."""
        return TangoEventLogger()

    @patch(LOGGING_PATH)
    def test_log_event_writes_the_right_message_on_logging_info(
        self,
        mock_logging,
        logger: TangoEventLogger,
    ):
        """The log_event method writes a message to the logger when called."""

        mock_event = create_mock_eventdata("test/device/1", "attribute1", 123)

        logger._log_event(
            event_data=mock_event,
            filtering_rule=DEFAULT_LOG_ALL_EVENTS,
            message_builder=DEFAULT_LOG_MESSAGE_BUILDER,
        )

        # Assert that content of the last message
        # printed includes device name, attribute name and current value
        assert_that(mock_logging.info.call_args[0][0]).described_as(
            "The log_event method should write the right message to the logger."
        ).contains("test/device/1")
        assert_that(mock_logging.info.call_args[0][0]).described_as(
            "The log_event method should write the right message to the logger."
        ).contains("attribute1")
        assert_that(mock_logging.info.call_args[0][0]).described_as(
            "The log_event method should write the right message to the logger."
        ).contains(str(123))

    @patch(LOGGING_PATH)
    def test_log_event_does_not_write_message_when_filtering_rule_returns_false(
        self,
        mock_logging,
        logger: TangoEventLogger,
    ):
        """log_event method does not write a message when the filtering fail."""

        mock_event = create_mock_eventdata("test/device/1", "attribute1", 123)

        logger._log_event(
            event_data=mock_event,
            filtering_rule=lambda e: False,
            message_builder=DEFAULT_LOG_MESSAGE_BUILDER,
        )

        # Assert that the logging method was not called
        assert_that(mock_logging.info.call_count).described_as(
            "The log_event method should not write a message to the logger."
        ).is_zero()

    @patch(LOGGING_PATH)
    def test_log_event_writes_custom_message_when_required(
        self,
        mock_logging,
        logger: TangoEventLogger,
    ):
        """log_event method writes a custom message when required."""

        mock_event = create_mock_eventdata("test/device/1", "attribute1", 123)

        logger._log_event(
            event_data=mock_event,
            filtering_rule=DEFAULT_LOG_ALL_EVENTS,
            message_builder=lambda e: "Custom message",
        )

        # Assert that the logging method was called with the expected message
        assert_that(mock_logging.info.call_args[0][0]).described_as(
            "The log_event method should write the custom message to the logger."
        ).is_equal_to("Custom message")

    @patch(LOGGING_PATH)
    def test_log_event_when_event_contains_error_writes_error_message(
        self,
        mock_logging,
        logger: TangoEventLogger,
    ):
        """log_event method writes an error message when the event contains an error."""

        mock_event = create_mock_eventdata(
            "test/device/1",
            "attribute1",
            123,
            error=True,
        )

        logger._log_event(
            event_data=mock_event,
            filtering_rule=DEFAULT_LOG_ALL_EVENTS,
            message_builder=DEFAULT_LOG_MESSAGE_BUILDER,
        )

        # Assert that content of the last message
        # printed includes device name, attribute name and current value
        assert_that(mock_logging.error.call_args[0][0]).described_as(
            "The log_event method should write the right message to the logger."
        ).contains("test/device/1")
        assert_that(mock_logging.error.call_args[0][0]).described_as(
            "The log_event method should write the right message to the logger."
        ).contains("attribute1")
        assert_that(mock_logging.error.call_args[0][0]).described_as(
            "The log_event method should write the right message to the logger."
        ).contains(str(123))

    def test_logger_subscribe_to_device(self, logger: TangoEventLogger):
        """The logger subscribes to a device without exceptions."""
        
        device_name = "test_device"
        attribute_name = "test_attribute"

        with patch("tango.DeviceProxy") as mock_proxy:

            logger.log_events_from_device(device_name, attribute_name)

            try:
                mock_proxy.assert_called_with(device_name)
            except AssertionError:
                raise AssertionError(
                    "DeviceProxy should be called with the correct device name"
                )

            try:
                mock_proxy.return_value.subscribe_event.assert_called_with(
                    attribute_name,
                    tango.EventType.CHANGE_EVENT,
                    ANY
                )
            except AssertionError:
                raise AssertionError(
                    "subscribe_event should be called with "
                    "the correct arguments"
                )

