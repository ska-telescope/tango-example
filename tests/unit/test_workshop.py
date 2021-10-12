# pylint: disable=redefined-outer-name
import pytest
import tango
from tango.test_utils import DeviceTestContext

from ska_tango_examples.teams.TangoWorkshopCounter import TangoWorkshopCounter


@pytest.fixture
def tangoWorkshopCounter(request):
    """Create DeviceProxy for tests"""
    true_context = request.config.getoption("--true-context")
    if not true_context:
        with DeviceTestContext(TangoWorkshopCounter) as proxy:
            yield proxy
    else:
        database = tango.Database()
        instance_list = database.get_device_exported_for_class(
            "TangoWorkshopCounter"
        )
        for instance in instance_list.value_string:
            yield tango.DeviceProxy(instance)
            break


def test_increment(tangoWorkshopCounter):
    tangoWorkshopCounter.Init()
    value_before_inc = tangoWorkshopCounter.value
    tangoWorkshopCounter.increment()
    assert value_before_inc == tangoWorkshopCounter.value - 1
