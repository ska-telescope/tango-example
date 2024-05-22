import tango
from ska_tango_base.commands import ResultCode
from ska_tango_testing.mock.placeholders import Anything
from ska_tango_testing.mock.tango import MockTangoEventCallbackGroup


def lrcontroller_event_assert(
    controller: tango.DeviceProxy,
    multi_device_callback_group: MockTangoEventCallbackGroup,
    switch: bool,
):
    controller.subscribe_event(
        "longRunningCommandResult",
        tango.EventType.CHANGE_EVENT,
        multi_device_callback_group["longRunningCommandResult"],
    )
    # A Tango subscription always produces a change event when first subscribing
    multi_device_callback_group.assert_change_event(
        "longRunningCommandResult", Anything
    )

    if switch:
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
        assert state == tango.DevState.ON
    else:
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
        assert state == tango.DevState.OFF
