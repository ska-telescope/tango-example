# pylint: disable=redefined-outer-name
import logging
from unittest.mock import Mock

import pytest
import tango
from tango import DevState
from tango.test_utils import DeviceTestContext

from ska_tango_examples.teams.CalendarClock import (
    DEFAULT_DAY,
    CalendarClockDevice,
    CalendarClockModel,
    DateStyle,
)


@pytest.fixture(scope="function")
def calendarclock(request):
    """Creates and returns a TANGO DeviceTestContext object.

    Parameters
    ----------
    request: _pytest.fixtures.SubRequest
        A request object gives access to the requesting test context.
    """
    if request is not None:
        logging.info(str(request))
    properties = {}
    tc = DeviceTestContext(
        CalendarClockDevice, properties=properties, process=True
    )
    true_context = request.config.getoption("--true-context")
    if not true_context:
        tc = DeviceTestContext(
            CalendarClockDevice, properties=properties, process=True
        )
        tc.start()
        yield tc.device
        tc.stop()
    else:
        database = tango.Database()
        instance_list = database.get_device_exported_for_class(
            "CalendarClockDevice"
        )
        for instance in instance_list.value_string:
            yield tango.DeviceProxy(instance)


class TestCalendarClockDevice:
    def test_Init(self, calendarclock):
        calendarclock.Init()
        assert calendarclock.day == DEFAULT_DAY
        calendarclock.Advance()
        assert calendarclock.day == DEFAULT_DAY + 1
        calendarclock.Init()
        assert calendarclock.day == DEFAULT_DAY

        assert calendarclock.date_style == DateStyle.BRITISH
        calendarclock.date_style = DateStyle.AMERICAN
        assert calendarclock.date_style == DateStyle.AMERICAN
        calendarclock.Init()
        assert calendarclock.date_style == DateStyle.BRITISH

        assert calendarclock.State() == DevState.UNKNOWN
        calendarclock.SwitchOn()
        assert calendarclock.State() == DevState.ON
        calendarclock.Init()
        assert calendarclock.State() == DevState.UNKNOWN

        assert calendarclock.State() == DevState.UNKNOWN
        calendarclock.SwitchOff()
        assert calendarclock.State() == DevState.OFF
        calendarclock.Init()
        assert calendarclock.State() == DevState.UNKNOWN

    def test_date(self, calendarclock):
        calendarclock.calendar_date = "25/10/2020"
        assert calendarclock.day == 25
        assert calendarclock.month == 10
        assert calendarclock.year == 2020

    def test_time(self, calendarclock):
        calendarclock.clock_time = "04:05:59"
        assert calendarclock.hour == 4
        assert calendarclock.minute == 5
        assert calendarclock.second == 59

    def test_Advance(self, calendarclock):
        calendarclock.calendar_date = "03/02/0001"
        calendarclock.Advance()
        assert calendarclock.calendar_date == "04/02/0001"

    def test_SwitchOn(self, calendarclock):
        calendarclock.Init()
        assert calendarclock.State() == DevState.UNKNOWN
        calendarclock.SwitchOn()
        assert calendarclock.State() == DevState.ON
        calendarclock.SwitchOn()
        assert calendarclock.State() == DevState.ON

    def test_SwitchOff(self, calendarclock):
        calendarclock.Init()
        assert calendarclock.State() == DevState.UNKNOWN
        calendarclock.SwitchOff()
        assert calendarclock.State() == DevState.OFF


@pytest.fixture
def calender_clock_model():
    clock = CalendarClockModel(1, 2, 3, 4, 5, 6)
    clock.logger = Mock()
    return clock


@pytest.fixture(
    scope="function",
    params=[
        ["17", 2, 2020],
        [17, "2", 2020],
        [17, 2, "2020"],
    ],
)
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
        calender_clock_model.logger.info.assert_called_with(
            "Swithed off CalendarClockModel"
        )
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

        calender_clock_model.get_device_state = Mock(
            return_value=DevState.INIT
        )
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

    def test_set_clock_invalid(
        self, calender_clock_model, invalid_clock_values
    ):
        with pytest.raises(TypeError):
            calender_clock_model.set_clock(*invalid_clock_values)

    def test_set_calendar(self, calender_clock_model):
        calender_clock_model.set_calendar(3, 4, 5)
        assert str(calender_clock_model) == "03/04/0005 04:05:06"

    def test_set_calendar_invalid(
        self, calender_clock_model, invalid_calendar_values
    ):
        with pytest.raises(TypeError):
            calender_clock_model.set_calendar(*invalid_calendar_values)

    def test_leap_year(self, calender_clock_model):
        assert calender_clock_model.leapyear(1804)
        assert not calender_clock_model.leapyear(1803)
