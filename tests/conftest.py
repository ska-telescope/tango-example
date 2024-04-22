# pylint: disable=unused-argument
import logging

import pytest
import tango
import tango.test_context
from ska_tango_testing.harness import TangoTestHarness
from ska_tango_testing.mock.tango import MockTangoEventCallbackGroup
from tango.test_context import MultiDeviceTestContext

from ska_tango_examples.DevFactory import DevFactory
from ska_tango_examples.teams.long_running.Controller import LRController
from ska_tango_examples.teams.long_running.Station import Station
from ska_tango_examples.teams.long_running.Tile import Tile


def pytest_sessionstart(session):
    """
    Pytest hook; prints info about tango version.
    :param session: a pytest Session object
    :type session: :py:class:`pytest.Session`
    """
    print(tango.utils.info())


def pytest_addoption(parser):
    """
    Pytest hook; implemented to add the `--true-context` option, used to
    indicate that a true Tango subsystem is available, so there is no
    need for a :py:class:`tango.test_context.MultiDeviceTestContext`.
    :param parser: the command line options parser
    :type parser: :py:class:`argparse.ArgumentParser`
    """
    parser.addoption(
        "--true-context",
        action="store_true",
        default=False,
        help=(
            "Tell pytest that you have a true Tango context and don't "
            "need to spin up a Tango test context"
        ),
    )


@pytest.fixture
def tango_context(devices_to_load, request):
    true_context = request.config.getoption("--true-context")
    logging.info("true context: %s", true_context)
    if not true_context:
        with MultiDeviceTestContext(devices_to_load, process=False) as context:
            DevFactory._test_context = context
            yield context
    else:
        yield None


@pytest.fixture
def multi_device_tango_context():
    """
    Creates and returns a TANGO MultiDeviceTestContext object, with
    tango.DeviceProxy patched to work around a name-resolving issue.
    """
    harness = TangoTestHarness()
    # Controller
    harness.add_device(
        "test/lrccontroller/1",
        LRController,
        stations=["test/lrcstation/1", "test/lrcstation/2"],
    )
    # Stations
    for station, tiles in [
        ("test/lrcstation/1", ["test/lrctile/1", "test/lrctile/2"]),
        ("test/lrcstation/2", ["test/lrctile/3", "test/lrctile/4"]),
    ]:
        harness.add_device(
            station,
            Station,
            tiles=tiles,
        )
    # Tiles
    for tile in [
        "test/lrctile/1",
        "test/lrctile/2",
        "test/lrctile/3",
        "test/lrctile/4",
    ]:
        harness.add_device(
            tile,
            Tile,
        )

    with harness as context:
        yield context


@pytest.fixture
def multi_device_callback_group():
    return MockTangoEventCallbackGroup(
        "longRunningCommandResult",
        timeout=10,
    )
