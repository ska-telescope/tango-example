# pylint: disable=redefined-outer-name
from io import StringIO
from time import sleep

import pytest
from tango import DevFailed, EventType
from tango.test_utils import DeviceTestContext
from tango.utils import EventCallback

from ska_tango_examples.teams.SampleLongRunningDevice import (
    QueueManager,
    ResultCode,
    SampleLongRunningDevice,
)

TEST_TIMEOUT = 5


class TestQueueManager:
    @pytest.mark.timeout(TEST_TIMEOUT)
    def test_Init(self):
        device = None
        max_queue_size = 2
        q = QueueManager(None, device, max_queue_size)
        assert q._max_queue_size == max_queue_size
        assert q._work_queue.maxsize == max_queue_size
        assert q._worker_thread.isAlive() is True
        assert q._tango_device is device
        assert q._command_result == []
        assert q._command_ids_in_queue == []
        assert q._commands_in_queue == []
        assert q._command_status == []

        # Check that is_stopping exists the thread
        q.is_stopping.set()
        sleep(0.5)
        assert q._worker_thread.isAlive() is False


@pytest.fixture(scope="function")
def device():
    """Creates and returns a TANGO DeviceTestContext object
    for SampleLongRunningDevice.SampleLongRunningDevice.
    """
    properties = {}
    tc = DeviceTestContext(
        SampleLongRunningDevice,
        properties=properties,
        process=True,
    )
    tc.start()
    yield tc.device
    tc.stop()


class TestSampleLongRunningDevice:
    @pytest.mark.timeout(TEST_TIMEOUT)
    def test_ShortCommand(self, device):
        """Make sure non long running commands are OK"""
        res_return_got = device.Short()
        assert "ShortCommand completed" in res_return_got[1]

    @pytest.mark.timeout(TEST_TIMEOUT)
    def test_short_while_long_running(self, device):
        """Make sure a normal command can execute during a long running"""
        status_events = EventCallback(fd=StringIO())
        device.subscribe_event(
            "longRunningCommandStatus",
            EventType.CHANGE_EVENT,
            status_events,
            wait=True,
        )

        # Wait unitl the long runing command is in progress
        device.NonAbortingLongRunning(1.0)
        status_events = self.get_events(status_events, 1)
        assert len(status_events) == 1
        assert "IN PROGRESS" in status_events[0][1]

        result = device.Short()
        assert "ShortCommand completed" in result[1]

    @pytest.mark.timeout(TEST_TIMEOUT)
    def test_unique_ids(self, device):
        """Test ID uniqueness"""
        result_a = device.AbortingLongRunning(1.0)
        result_b = device.AbortingLongRunning(1.0)

        assert "AbortingLongRunning" in result_a[1][0]
        assert result_a[1][0] != result_b[1][0]

    @pytest.mark.timeout(TEST_TIMEOUT)
    def test_queue_full(self, device):
        """Test that a full queue raises an exception"""
        with pytest.raises(DevFailed) as exc:
            for _ in range(5):
                device.AbortingLongRunning(1.0)
        assert (
            exc.value.args[0].reason
            == "Command rejected because queue is full"
        )

    @pytest.mark.timeout(TEST_TIMEOUT)
    def test_aborting_exception(self, device):
        """Test that when aborting a new long running command gets rejected"""
        device.NonAbortingLongRunning(1.0)
        device.AbortCommands()
        with pytest.raises(DevFailed) as exc:
            device.NonAbortingLongRunning(1.0)
        assert (
            exc.value.args[0].reason
            == "Command rejected because queue is aborting"
        )

    @pytest.mark.timeout(TEST_TIMEOUT)
    def test_multi_long_running(self, device):
        """Test that we can schedule multiple long running commands and that
        the attributes are updated accordingly"""
        command_events = EventCallback(fd=StringIO())
        device.subscribe_event(
            "longRunningCommandsInQueue",
            EventType.CHANGE_EVENT,
            command_events,
            wait=True,
        )

        result_events = EventCallback(fd=StringIO())
        device.subscribe_event(
            "longRunningCommandResult",
            EventType.CHANGE_EVENT,
            result_events,
            wait=True,
        )

        id_events = EventCallback(fd=StringIO())
        device.subscribe_event(
            "longRunningCommandIDsInQueue",
            EventType.CHANGE_EVENT,
            id_events,
            wait=True,
        )

        status_events = EventCallback(fd=StringIO())
        device.subscribe_event(
            "longRunningCommandStatus",
            EventType.CHANGE_EVENT,
            status_events,
            wait=True,
        )

        device.TestA()
        device.TestB()
        device.TestC()

        # Check longRunningCommandsInQueue events
        command_events = self.get_events(command_events, 5)
        assert len(command_events) == 5
        assert command_events == [
            ("TestA",),
            ("TestA", "TestB"),
            ("TestA", "TestB", "TestC"),
            ("TestB", "TestC"),
            ("TestC",),
        ]

        # Check longRunningCommandIDsInQueue events
        id_events = self.get_events(id_events, 5)
        assert len(id_events) == 5
        cleaned_events = self.strip_timestamps(id_events)
        assert cleaned_events == [
            ["TestA"],
            ["TestA", "TestB"],
            ["TestA", "TestB", "TestC"],
            ["TestB", "TestC"],
            ["TestC"],
        ]
        # Check longRunningCommandResult events
        result_events = self.get_events(result_events, 3)
        assert len(result_events) == 3
        for command_name, result in zip(
            ["TestA", "TestB", "TestC"], result_events
        ):
            assert command_name in result[0]
            assert command_name in result[1]

        # Check longRunningCommandStatus events
        status_events = self.get_events(status_events, 3)
        assert len(status_events) == 3
        for command_name, result in zip(
            ["TestA", "TestB", "TestC"], status_events
        ):
            assert command_name in result[0]
            assert result[1] == "IN PROGRESS"

    @pytest.mark.timeout(TEST_TIMEOUT)
    def test_multi_long_running_progress(self, device):
        """Test that progress events fire and is correct"""
        progress_events = EventCallback(fd=StringIO())
        device.subscribe_event(
            "longRunningCommandProgress",
            EventType.CHANGE_EVENT,
            progress_events,
            wait=True,
        )

        device.TestProgress(0.5)
        progress_events = self.get_events(progress_events, 6)
        assert len(progress_events) == 6
        for result in progress_events:
            assert "TestProgress" in result[0]
        progress_events = [progress[1] for progress in progress_events]
        for event_percentage, percentage in zip(
            progress_events, [1, 25, 50, 74, 99, 100]
        ):
            assert event_percentage == str(percentage)

    @pytest.mark.timeout(TEST_TIMEOUT)
    def test_not_allowed(self, device):
        """Test that `is_allowed` is applied"""
        status_events = EventCallback(fd=StringIO())
        device.subscribe_event(
            "longRunningCommandStatus",
            EventType.CHANGE_EVENT,
            status_events,
            wait=True,
        )

        result_events = EventCallback(fd=StringIO())
        device.subscribe_event(
            "longRunningCommandResult",
            EventType.CHANGE_EVENT,
            result_events,
            wait=True,
        )

        # Command should be queued
        result = device.NotAllowed()
        assert ResultCode.QUEUED == result[0][0]
        assert "NotAllowed" in result[1][0]

        # Check that it starts
        status_events = self.get_events(status_events, 1)
        assert "NotAllowed" in status_events[0][0]
        assert "IN PROGRESS" in status_events[0][1]

        result_events = self.get_events(result_events, 1)
        assert "_NotAllowed" in result_events[0][0]
        assert "ResultCode.NOT_ALLOWED" in result_events[0][1]

    @pytest.mark.timeout(TEST_TIMEOUT)
    def test_aborted_long_running_command(self, device):
        """Test that a running long running command oborts while in progress"""
        result_events = EventCallback(fd=StringIO())
        device.subscribe_event(
            "longRunningCommandResult",
            EventType.CHANGE_EVENT,
            result_events,
            wait=True,
        )

        status_events = EventCallback(fd=StringIO())
        device.subscribe_event(
            "longRunningCommandStatus",
            EventType.CHANGE_EVENT,
            status_events,
            wait=True,
        )

        result = device.AbortingLongRunning(1.0)
        assert ResultCode.QUEUED == result[0][0]
        assert "AbortingLongRunning" in result[1][0]

        # Make sure the command is in progress before aborting
        status_events = self.get_events(status_events, 1)
        assert "AbortingLongRunning" in status_events[0][0]
        assert "IN PROGRESS" in status_events[0][1]

        result = device.AbortCommands()
        assert "Abort completed" in result[1][0]
        result_events = self.get_events(result_events, 1)
        assert "_AbortingLongRunning" in result_events[0][0]
        assert "<ResultCode.ABORTED: 7>" in result_events[0][1]
        assert "AbortingLongRunningCommand Aborted" in result_events[0][1]

    @pytest.mark.timeout(TEST_TIMEOUT)
    def test_aborted_long_running_command_queue(self, device):
        """Test that we empty out the queue on abort"""
        result_events = EventCallback(fd=StringIO())
        device.subscribe_event(
            "longRunningCommandResult",
            EventType.CHANGE_EVENT,
            result_events,
            wait=True,
        )

        queue_events = EventCallback(fd=StringIO())
        device.subscribe_event(
            "longRunningCommandsInQueue",
            EventType.CHANGE_EVENT,
            queue_events,
            wait=True,
        )

        device.AbortingLongRunning(1.0)
        device.NonAbortingLongRunning(1.0)
        device.NonAbortingLongRunning(1.0)
        device.AbortCommands()

        result_events = self.get_events(result_events, 3)
        for command, result in zip(
            [
                "AbortingLongRunning",
                "NonAbortingLongRunning",
                "NonAbortingLongRunning",
            ],
            result_events,
        ):
            assert command in result[0]
            assert "ResultCode.ABORTED" in result[1]

    @pytest.mark.timeout(TEST_TIMEOUT)
    def test_init(self, device):
        """Test that Init resets QueueManager"""
        device.AbortingLongRunning(1.0)
        device.NonAbortingLongRunning(1.0)
        device.NonAbortingLongRunning(1.0)
        assert device.longRunningCommandIDsInQueue
        device.Init()
        assert not device.longRunningCommandIDsInQueue

    def get_events(self, event_call_back, event_count):
        event_values = []
        for _ in range(10):  # Give it a few chances to get there
            event_values = []
            for event in event_call_back.get_events():
                if event.attr_value and event.attr_value.value:
                    event_values.append(event.attr_value.value)
            if len(event_values) == event_count:
                break
            sleep(0.5)
        return event_values

    def strip_timestamps(self, events):
        cleaned_events = []
        for i in events:
            row = []
            for j in i:
                row.append(j.split("_")[1])
            cleaned_events.append(row)
        return cleaned_events
