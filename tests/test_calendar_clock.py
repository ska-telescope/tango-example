import pytest

from unittest.mock import Mock

from tango import DevState, DevFailed
from tango.test_utils import DeviceTestContext

from module_example.CalendarClock import (
    CalendarClockDevice,
    DateStyle,
    CalendarClockModel,
    DEFAULT_YEAR,
    DEFAULT_MONTH,
    DEFAULT_DAY,
    DEFAULT_HOUR,
    DEFAULT_MINUTE,
    DEFAULT_SECOND,
)


@pytest.fixture(scope="function")
def tango_context(request):
    """Creates and returns a TANGO DeviceTestContext object.

    Parameters
    ----------
    request: _pytest.fixtures.SubRequest
        A request object gives access to the requesting test context.
    """
    properties = {}
    tango_context = DeviceTestContext(CalendarClockDevice, properties=properties)
    tango_context.start()
    yield tango_context
    tango_context.stop()


class TestCalendarClockDevice:
    def test_date(self, tango_context):
        tango_context.device.calendar_date = "25/10/2020"
        assert tango_context.device.day == 25
        assert tango_context.device.month == 10
        assert tango_context.device.year == 2020

    def test_time(self, tango_context):
        tango_context.device.clock_time = "04:05:59"
        assert tango_context.device.hour == 4
        assert tango_context.device.minute == 5
        assert tango_context.device.second == 59

    def test_Advance(self, tango_context):
        tango_context.device.Advance()
        assert tango_context.device.calendar_date == "04/02/0001"

    def test_SwitchOn(self, tango_context):
        assert tango_context.device.State() == DevState.UNKNOWN
        tango_context.device.SwitchOn()
        assert tango_context.device.State() == DevState.ON
        tango_context.device.SwitchOn()
        assert tango_context.device.State() == DevState.ON

    def test_SwitchOff(self, tango_context):
        assert tango_context.device.State() == DevState.UNKNOWN
        tango_context.device.SwitchOff()
        assert tango_context.device.State() == DevState.OFF

    def test_Init(self, tango_context):

        assert tango_context.device.day == DEFAULT_DAY
        tango_context.device.Advance()
        assert tango_context.device.day == DEFAULT_DAY + 1
        tango_context.device.Init()
        assert tango_context.device.day == DEFAULT_DAY

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


@pytest.fixture
def calender_clock_model():
    clock = CalendarClockModel(1, 2, 3, 4, 5, 6)
    clock.logger = Mock()
    return clock


@pytest.fixture(scope="function", params=[["17", 2, 2020], [17, "2", 2020], [17, 2, "2020"], ])
def invalid_calendar_values(request):
    day, month, year = request.param
    return day, month, year


@pytest.fixture(
    scope="function",
    params=[
        ["23", 59, 59],
        [-1, 59, 59],
        [24, 59, 59],
        [23, "59", 59],
        [23, -1, 59],
        [23, 60, 59],
        [23, 59, "59"],
        [23, 59, -1],
        [23, 59, 60],
    ],
)
def invalid_clock_values(request):
    hour, minute, year = request.param
    return hour, minute, year


class TestCalendarClockModel:
    def test_switch_off(self, calender_clock_model):
        calender_clock_model.get_device_state = Mock(return_value=DevState.OFF)
        calender_clock_model.set_device_state = Mock()
        calender_clock_model.switch_off()
        calender_clock_model.set_device_state.assert_not_called()

        calender_clock_model.get_device_state = Mock(return_value=DevState.ON)
        calender_clock_model.set_device_state = Mock()
        calender_clock_model.switch_off()
        calender_clock_model.logger.info.assert_called_with("Swithed off CalendarClockModel")
        calender_clock_model.set_device_state.assert_called_with(DevState.OFF)

    def test_switch_on(self, calender_clock_model):
        calender_clock_model.get_device_state = Mock(return_value=DevState.OFF)
        calender_clock_model.set_device_state = Mock()
        calender_clock_model.switch_on()
        calender_clock_model.set_device_state.assert_called_with(DevState.ON)

        calender_clock_model.get_device_state = Mock(return_value=DevState.ON)
        calender_clock_model.set_device_state = Mock()
        calender_clock_model.switch_on()
        calender_clock_model.set_device_state.assert_not_called()

        calender_clock_model.get_device_state = Mock(return_value=DevState.INIT)
        calender_clock_model.set_device_state = Mock()
        with pytest.raises(Exception):
            calender_clock_model.switch_on()
        calender_clock_model.set_device_state.assert_not_called()

    def test_formatting(self, calender_clock_model):
        assert str(calender_clock_model) == "01/02/0003 04:05:06"
        calender_clock_model.date_style = DateStyle.AMERICAN
        assert str(calender_clock_model) == "02/01/0003 04:05:06"

    def test_advance_day(self, calender_clock_model):
        calender_clock_model.advance()
        assert calender_clock_model.calendar_date == "02/02/0003"

    def test_advance_month(self, calender_clock_model):
        calender_clock_model.set_calendar(31, 1, 2020)
        calender_clock_model.advance()
        assert calender_clock_model.calendar_date == "01/02/2020"

    def test_advance_year(self, calender_clock_model):
        calender_clock_model.set_calendar(31, 12, 2020)
        calender_clock_model.advance()
        assert calender_clock_model.calendar_date == "01/01/2021"

    def test_tick_second(self, calender_clock_model):
        calender_clock_model.tick()
        assert str(calender_clock_model) == "01/02/0003 04:05:07"

    def test_tick_minute(self, calender_clock_model):
        calender_clock_model.set_clock(1, 20, 59)
        calender_clock_model.tick()
        assert str(calender_clock_model) == "01/02/0003 01:21:00"

    def test_tick_hour(self, calender_clock_model):
        calender_clock_model.set_clock(1, 59, 59)
        calender_clock_model.tick()
        assert str(calender_clock_model) == "01/02/0003 02:00:00"

    def test_tick_advance(self, calender_clock_model):
        calender_clock_model.set_clock(23, 59, 59)
        calender_clock_model.set_calendar(31, 1, 2020)
        calender_clock_model.tick()
        assert str(calender_clock_model) == "01/02/2020 00:00:00"

    def test_set_clock(self, calender_clock_model):
        calender_clock_model.set_clock(2, 3, 4)
        assert str(calender_clock_model) == "01/02/0003 02:03:04"

    def test_set_clock_invalid(self, calender_clock_model, invalid_clock_values):
        with pytest.raises(TypeError):
            calender_clock_model.set_clock(*invalid_clock_values)

    def test_set_calendar(self, calender_clock_model):
        calender_clock_model.set_calendar(3, 4, 5)
        assert str(calender_clock_model) == "03/04/0005 04:05:06"

    def test_set_calendar_invalid(self, calender_clock_model, invalid_calendar_values):
        with pytest.raises(TypeError):
            calender_clock_model.set_calendar(*invalid_calendar_values)

    def test_leap_year(self, calender_clock_model):
        assert calender_clock_model.leapyear(1804)
        assert not calender_clock_model.leapyear(1803)
