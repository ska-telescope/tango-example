import logging

import pytest

from ..lrc_utils import lrcontroller_event_assert

logger = logging.getLogger(__name__)


class TestLRC:
    @pytest.mark.forked
    def test_long_running_device_client_on(
        self, multi_device_tango_context, multi_device_callback_group
    ):
        controller = multi_device_tango_context.get_device(
            "test/lrccontroller/1"
        )
        lrcontroller_event_assert(
            controller, multi_device_callback_group, True
        )

    @pytest.mark.forked
    def test_long_running_device_client_off(
        self, multi_device_tango_context, multi_device_callback_group
    ):
        controller = multi_device_tango_context.get_device(
            "test/lrccontroller/1"
        )
        lrcontroller_event_assert(
            controller, multi_device_callback_group, False
        )
