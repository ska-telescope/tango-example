import logging

import pytest
from ska_tango_base.commands import ResultCode
from ska_tango_testing.mock.placeholders import Anything
from tango import EventType, DevState

logger = logging.getLogger(__name__)


class TestLRC:
    @pytest.mark.forked
    def test_long_running_device_client_on(
        self, multi_device_tango_context, multi_device_callback_group
    ):
        controller = multi_device_tango_context.get_device(
            "test/lrccontroller/1"
        )
        controller.subscribe_event(
            "longRunningCommandResult",
            EventType.CHANGE_EVENT,
            multi_device_callback_group["longRunningCommandResult"],
        )
        # A Tango subscription always produces a change event when first subscribing
        multi_device_callback_group.assert_change_event(
            "longRunningCommandResult", Anything
        )

        return_code, command_id = controller.On()
        assert return_code[0] == ResultCode.QUEUED
        multi_device_callback_group[
            "longRunningCommandResult"
        ].assert_change_event(
            (
                f"{command_id[0]}",
                f'[{int(ResultCode.OK)}, "Controller On completed"]',
            )
        )

        state = controller.state()
        assert state == DevState.ON

    @pytest.mark.forked
    def test_long_running_device_client_off(
        self, multi_device_tango_context, multi_device_callback_group
    ):
        controller = multi_device_tango_context.get_device(
            "test/lrccontroller/1"
        )
        controller.subscribe_event(
            "longRunningCommandResult",
            EventType.CHANGE_EVENT,
            multi_device_callback_group["longRunningCommandResult"],
        )
        # A Tango subscription always produces a change event when first subscribing
        multi_device_callback_group.assert_change_event(
            "longRunningCommandResult", Anything
        )

        return_code, command_id = controller.Off()
        assert return_code[0] == ResultCode.QUEUED
        multi_device_callback_group[
            "longRunningCommandResult"
        ].assert_change_event(
            (
                f"{command_id[0]}",
                f'[{int(ResultCode.OK)}, "Controller Off completed"]',
            )
        )

        state = controller.state()
        assert state == DevState.OFF
