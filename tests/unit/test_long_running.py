import logging
from queue import Empty

import pytest
from tango import EventType

from ska_tango_examples.teams.long_running.Controller import LRController
from ska_tango_examples.teams.long_running.Station import Station
from ska_tango_examples.teams.long_running.Tile import Tile

from .utils import LRCAttributesStore

logger = logging.getLogger(__name__)

devices_to_test = [
    {
        "class": LRController,
        "devices": [
            {
                "name": "test/lrccontroller/1",
                "properties": {
                    "stations": ["test/lrcstation/1", "test/lrcstation/2"]
                },
            }
        ],
    },
    {
        "class": Station,
        "devices": [
            {
                "name": "test/lrcstation/1",
                "properties": {"tiles": ["test/lrctile/1", "test/lrctile/2"]},
            },
            {
                "name": "test/lrcstation/2",
                "properties": {"tiles": ["test/lrctile/3", "test/lrctile/4"]},
            },
        ],
    },
    {
        "class": Tile,
        "devices": [
            {"name": "test/lrctile/1"},
            {"name": "test/lrctile/2"},
            {"name": "test/lrctile/3"},
            {"name": "test/lrctile/4"},
        ],
    },
]


class TestLRC:
    @pytest.mark.forked
    def test_long_running_device_client(
        self, multi_device_tango_context, caplog
    ):
        caplog.set_level(logging.INFO)
        store = LRCAttributesStore()
        controller = multi_device_tango_context.get_device(
            "test/lrccontroller/1"
        )
        controller.subscribe_event(
            "longRunningCommandResult",
            EventType.CHANGE_EVENT,
            store,
            wait=True,
        )

        controller.On()

        for timing in [2, 2, 2, 2]:
            try:
                val = store.get_attribute_value(
                    "longRunningCommandResult", fetch_timeout=timing
                )
                if val[2] == "Controller On completed":
                    break
            except Empty:
                continue
        else:
            assert 0, "Command not completed"
