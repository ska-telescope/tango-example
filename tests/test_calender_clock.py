
import pytest

from unittest.mock import Mock

from tango import DevState, DevFailed
from tango.test_utils import DeviceTestContext

from module_example.CalendarClock import CalendarClockDevice, DateStyle, CalendarClockModel


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

    tango_context = DeviceTestContext(CalendarClockDevice, properties=properties)
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


class TestCalendarClockDevice:

    def test_SetDateTime(self, tango_context, initialize_device):
        tango_context.device.SetDateTime("25/10/2020 04:05:59")
        assert tango_context.device.day == 25
        assert tango_context.device.month == 10
        assert tango_context.device.year == 2020
        assert tango_context.device.hour == 4
        assert tango_context.device.minute == 5
        assert tango_context.device.second == 59

        tango_context.device.Tick()
        assert tango_context.device.second == 0
        assert tango_context.device.minute == 6

    def test_InitResetsDevice(self, tango_context, initialize_device):

        assert tango_context.device.day == CURRENT_DAY
        tango_context.device.Advance()
        assert tango_context.device.day == CURRENT_DAY + 1
        tango_context.device.Init()
        assert tango_context.device.day == CURRENT_DAY

        assert tango_context.device.date_style == DateStyle.BRITISH
        tango_context.device.date_style = DateStyle.AMERICAN
        assert tango_context.device.date_style == DateStyle.AMERICAN
        tango_context.device.Init()
        assert tango_context.device.date_style == DateStyle.BRITISH

        assert tango_context.device.State() == DevState.UNKNOWN
        tango_context.device.SwitchOn()
        assert tango_context.device.State() == DevState.ON
        tango_context.device.Init()
        assert tango_context.device.State() == DevState.UNKNOWN

        assert tango_context.device.State() == DevState.UNKNOWN
        tango_context.device.SwitchOff()
        assert tango_context.device.State() == DevState.OFF
        tango_context.device.Init()
        assert tango_context.device.State() == DevState.UNKNOWN

    def test_Advance(self, tango_context, initialize_device):
        assert tango_context.device.year == CURRENT_YEAR
        assert tango_context.device.month == CURRENT_MONTH
        assert tango_context.device.day == CURRENT_DAY
        tango_context.device.Advance()
        assert tango_context.device.year == CURRENT_YEAR
        assert tango_context.device.month == CURRENT_MONTH
        assert tango_context.device.day == CURRENT_DAY + 1

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


@pytest.fixture
def calender_clock_model():
    clock = CalendarClockModel(1,2,3,4,5,6)
    clock.logger = Mock()
    return clock


class TestCalendarClockModel:

    def test_switch_off(self, calender_clock_model):
        calender_clock_model.get_device_state  = Mock(return_value = DevState.OFF)
        calender_clock_model.set_device_state  = Mock()
        calender_clock_model.switch_off()
        calender_clock_model.set_device_state.assert_not_called()

        calender_clock_model.get_device_state  = Mock(return_value = DevState.ON)
        calender_clock_model.set_device_state  = Mock()
        calender_clock_model.switch_off()
        calender_clock_model.logger.info.assert_called_with('Swithed off CalendarClockModel')
        calender_clock_model.set_device_state.assert_called_with(DevState.OFF)

    def test_switch_on(self, calender_clock_model):
        calender_clock_model.get_device_state  = Mock(return_value = DevState.OFF)
        calender_clock_model.set_device_state  = Mock()
        calender_clock_model.switch_on()
        calender_clock_model.set_device_state.assert_called_with(DevState.ON)

        calender_clock_model.get_device_state  = Mock(return_value = DevState.ON)
        calender_clock_model.set_device_state  = Mock()
        calender_clock_model.switch_on()
        calender_clock_model.set_device_state.assert_not_called()

        calender_clock_model.get_device_state  = Mock(return_value = DevState.INIT)
        calender_clock_model.set_device_state  = Mock()
        with pytest.raises(DevFailed):
            calender_clock_model.switch_on()
        calender_clock_model.set_device_state.assert_not_called()

    def test_formatting(self, calender_clock_model):
        assert '01/02/0003 04:05:06' == str(calender_clock_model)

    def test_advance(self, calender_clock_model):
        calender_clock_model.advance()
        assert '02/02/0003 04:05:06' == str(calender_clock_model)

    def test_tick(self, calender_clock_model):
        calender_clock_model.tick()
        assert '01/02/0003 04:05:07' == str(calender_clock_model)

    def test_set_clock(self, calender_clock_model):
        calender_clock_model.set_clock(2,3,4)
        assert '01/02/0003 02:03:04' == str(calender_clock_model)

    def test_set_calendar(self, calender_clock_model):
        calender_clock_model.set_calendar(3,4,5)
        assert '03/04/0005 04:05:06' == str(calender_clock_model)

    def test_leap_year(self, calender_clock_model):
        assert calender_clock_model.leapyear(1804)
        assert not calender_clock_model.leapyear(1803)