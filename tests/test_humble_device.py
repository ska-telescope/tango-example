
import pytest

from tango import DevState
from tango.test_utils import DeviceTestContext

from module_example.HumbleDevice import CalendarClock, DateStyle


CURRENT_YEAR = 1
CURRENT_MONTH = 2
CURRENT_DAY = 3
CURRENT_HOUR = 4
CURRENT_MINUTE = 5
CURRENT_SECOND = 6

@pytest.fixture(scope="class")
def tango_context(request):
    """Creates and returns a TANGO DeviceTestContext object.

    Parameters
    ----------
    request: _pytest.fixtures.SubRequest
        A request object gives access to the requesting test context.
    """
    properties = {
        }
   
    tango_context = DeviceTestContext(CalendarClock, properties=properties)
    tango_context.start()
    yield tango_context
    tango_context.stop()

@pytest.fixture(scope="function")
def initialize_device(tango_context):
    """Re-initializes the device.

    Parameters
    ----------
    tango_context: tango.test_context.DeviceTestContext
        Context to run a device without a database.
    """
    yield tango_context.device.Init()


class TestCalendarClock:

    def test_Advance(self, tango_context, initialize_device):
        assert tango_context.device.year == CURRENT_YEAR
        assert tango_context.device.month == CURRENT_MONTH
        assert tango_context.device.day == CURRENT_DAY
        
        next_day = CURRENT_DAY + 1
        tango_context.device.Advance()

        assert tango_context.device.year == CURRENT_YEAR
        assert tango_context.device.month == CURRENT_MONTH
        assert tango_context.device.day == next_day

    def test_Tick(self, tango_context, initialize_device):
        assert tango_context.device.hour == CURRENT_HOUR
        assert tango_context.device.minute == CURRENT_MINUTE
        assert tango_context.device.second == CURRENT_SECOND

        next_second = CURRENT_SECOND + 1
        tango_context.device.Tick()

        assert tango_context.device.hour == CURRENT_HOUR
        assert tango_context.device.minute == CURRENT_MINUTE
        assert tango_context.device.second == next_second

    def test_SwitchOn(self, tango_context, initialize_device):
        assert tango_context.device.State() == DevState.UNKNOWN
        tango_context.device.SwitchOn()
        assert tango_context.device.State() == DevState.ON
        tango_context.device.SwitchOn()
        assert tango_context.device.State() == DevState.ON


    def test_SwitchOff(self, tango_context, initialize_device):
        assert tango_context.device.State() == DevState.UNKNOWN
        tango_context.device.SwitchOff()
        assert tango_context.device.State() == DevState.OFF
  
    def test_GetFormattedTime(self, tango_context, initialize_device):
        datetime_style = "{0:02d}/{1:02d}/{2:04d} {3:02d}:{4:02d}:{5:02d}"
        assert tango_context.device.date_style == DateStyle.BRITISH
        assert tango_context.device.GetFormattedTime() == (
            datetime_style.format(
                CURRENT_DAY, CURRENT_MONTH, CURRENT_YEAR, CURRENT_HOUR, CURRENT_MINUTE,
                CURRENT_SECOND))

        tango_context.device.date_style = DateStyle.AMERICAN

        assert tango_context.device.date_style == DateStyle.AMERICAN
        assert tango_context.device.GetFormattedTime() == (
            datetime_style.format(
                CURRENT_MONTH, CURRENT_DAY, CURRENT_YEAR, CURRENT_HOUR, CURRENT_MINUTE,
                CURRENT_SECOND))
