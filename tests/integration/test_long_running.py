import logging

import pytest
from tango import DeviceProxy

from ..lrc_utils import lrcontroller_event_assert

logger = logging.getLogger(__name__)


class TestLRC:
    @pytest.mark.post_deployment
    @pytest.mark.forked
    def test_long_running_device_client_on(self, multi_device_callback_group):
        controller = DeviceProxy("test/lrccontroller/1")
        lrcontroller_event_assert(
            controller, multi_device_callback_group, True
        )

    @pytest.mark.post_deployment
    @pytest.mark.forked
    def test_long_running_device_client_off(self, multi_device_callback_group):
        controller = DeviceProxy("test/lrccontroller/1")
        lrcontroller_event_assert(
            controller, multi_device_callback_group, False
        )
