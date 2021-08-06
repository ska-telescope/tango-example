import time
from io import StringIO

import pytest
from tango import EventType
from tango.utils import EventCallback

from ska_tango_examples.teams.SampleLongRunningDevice import (
    SampleLongRunningDevice,
)
from ska_tango_examples.teams.SampleLongRunningDeviceClient import (
    SampleLongRunningDeviceClient,
)

TEST_TIMEOUT = 8

devices_to_test = [
    {
        "class": SampleLongRunningDevice,
        "devices": [
            {"name": "test/longrunning/1"},
            {"name": "test/longrunning/2"},
        ],
    },
    {
        "class": SampleLongRunningDeviceClient,
        "devices": [
            {
                "name": "test/longrunningclient/1",
                "properties": {
                    "client_devices": [
                        "test/longrunning/1",
                    ],
                },
            },
            {
                "name": "test/longrunningclient/2",
                "properties": {
                    "client_devices": [
                        "test/longrunning/1",
                        "test/longrunning/2",
                    ],
                },
            },
        ],
    },
]


class TestMasterWorkerIntegration:
    @pytest.mark.timeout(TEST_TIMEOUT)
    def test_long_running_device_client(self, multi_device_tango_context):
        client = multi_device_tango_context.get_device(
            "test/longrunningclient/1"
        )

        result_id_events = EventCallback(fd=StringIO())
        client.subscribe_event(
            "lastResultCommandIDs",
            EventType.CHANGE_EVENT,
            result_id_events,
            wait=True,
        )

        result_command_name_events = EventCallback(fd=StringIO())
        client.subscribe_event(
            "lastResultCommandName",
            EventType.CHANGE_EVENT,
            result_command_name_events,
            wait=True,
        )

        # ExecuteTestA does not use the interface
        client.ExecuteTestA()
        client.ExecuteTestB()
        time.sleep(3)

        event_id_results = [
            i.attr_value.value
            for i in result_id_events.get_events()
            if i.attr_value.value
        ]
        event_name_results = [
            i.attr_value.value
            for i in result_command_name_events.get_events()
            if i.attr_value.value
        ]
        assert len(event_id_results) == 1
        assert len(event_id_results[0]) == 1
        assert event_name_results == ["TestB"]

    @pytest.mark.timeout(TEST_TIMEOUT)
    def test_long_running_device_client_group(
        self, multi_device_tango_context
    ):
        client = multi_device_tango_context.get_device(
            "test/longrunningclient/2"
        )

        result_id_events = EventCallback(fd=StringIO())
        client.subscribe_event(
            "lastResultCommandIDs",
            EventType.CHANGE_EVENT,
            result_id_events,
            wait=True,
        )

        result_command_name_events = EventCallback(fd=StringIO())
        client.subscribe_event(
            "lastResultCommandName",
            EventType.CHANGE_EVENT,
            result_command_name_events,
            wait=True,
        )

        # ExecuteTestA does not use the interface
        client.ExecuteTestA()
        client.ExecuteTestB()
        time.sleep(3)

        event_id_results = [
            i.attr_value.value
            for i in result_id_events.get_events()
            if i.attr_value.value
        ]
        event_name_results = [
            i.attr_value.value
            for i in result_command_name_events.get_events()
            if i.attr_value.value
        ]
        # Callback should only fire once when the command executed on both
        # devices. Thus one update
        assert len(event_id_results) == 1
        # We executed against 2 devices therefore there should be 2 IDs
        assert len(event_id_results[0]) == 2
        # We ran one command against 2 devices therefore there should be
        # only one TestB
        assert event_name_results == ["TestB"]

    @pytest.mark.timeout(TEST_TIMEOUT)
    def test_long_running_device_client_duplicate_command(
        self, multi_device_tango_context
    ):
        client = multi_device_tango_context.get_device(
            "test/longrunningclient/2"
        )

        result_id_events = EventCallback(fd=StringIO())
        client.subscribe_event(
            "lastResultCommandIDs",
            EventType.CHANGE_EVENT,
            result_id_events,
            wait=True,
        )

        result_command_name_events = EventCallback(fd=StringIO())
        client.subscribe_event(
            "lastResultCommandName",
            EventType.CHANGE_EVENT,
            result_command_name_events,
            wait=True,
        )

        # ExecuteTestA does not use the interface
        client.ExecuteTestA()
        client.ExecuteTestB()
        client.ExecuteTestB()
        client.ExecuteTestB()
        time.sleep(5)

        event_id_results = [
            i.attr_value.value
            for i in result_id_events.get_events()
            if i.attr_value.value
        ]
        event_name_results = [
            i.attr_value.value
            for i in result_command_name_events.get_events()
            if i.attr_value.value
        ]
        # There should be 3 events as 3 commands have completed
        assert len(event_id_results) == 3
        # There should be 2 IDs per result as it ran against 2
        # devices each
        for ids in event_id_results:
            assert len(ids) == 2
        assert event_name_results == ["TestB"]

    @pytest.mark.timeout(TEST_TIMEOUT)
    def test_long_running_device_client_multi_command(
        self, multi_device_tango_context
    ):
        client = multi_device_tango_context.get_device(
            "test/longrunningclient/2"
        )

        result_id_events = EventCallback(fd=StringIO())
        client.subscribe_event(
            "lastResultCommandIDs",
            EventType.CHANGE_EVENT,
            result_id_events,
            wait=True,
        )

        result_command_name_events = EventCallback(fd=StringIO())
        client.subscribe_event(
            "lastResultCommandName",
            EventType.CHANGE_EVENT,
            result_command_name_events,
            wait=True,
        )

        client.ExecuteTestB()
        client.ExecuteTestC()
        client.ExecuteTestB()
        client.ExecuteTestC()
        time.sleep(5)

        event_id_results = [
            i.attr_value.value
            for i in result_id_events.get_events()
            if i.attr_value.value
        ]
        event_name_results = [
            i.attr_value.value
            for i in result_command_name_events.get_events()
            if i.attr_value.value
        ]
        # There should be 4 events as 4 commands have completed
        assert len(event_id_results) == 4
        # There should be 2 IDs per result as it ran against 2
        # devices each
        for ids in event_id_results:
            assert len(ids) == 2
        assert event_name_results == ["TestB", "TestC", "TestB", "TestC"]
