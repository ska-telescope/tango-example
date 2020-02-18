# pylint: disable=C0103
""" This module illustates the humble object principal whereby the business logic is
seperated from the external interfaces.

class CalendarClockDevice
    This class is an implementation of a Tango Device. No business logic exists in this
    class.

class CalendarClockModel
    This class encapsulates all the business logic for the CalendarClock device.

Tests in tests/test_calendar_clock.py

    class TestCalendarClockModel
        This class tests the business logic without having to instantiate the Tango Device

    class TestCalendarClockDevice
        This class uses `DeviceTestContext` to test the Tango device by instantiating the
        device class and proxies to device.
"""

from enum import IntEnum

from tango import AttrWriteType, DevState, Except, ErrSeverity
from tango.server import attribute, command, run, device_property

from skabase.SKABaseDevice.SKABaseDevice import SKABaseDevice


DEFAULT_YEAR = 1
DEFAULT_MONTH = 2
DEFAULT_DAY = 3
DEFAULT_HOUR = 4
DEFAULT_MINUTE = 5
DEFAULT_SECOND = 6


class DateStyle(IntEnum):
    """Style of the date"""

    BRITISH = 0  # DevEnum's must start at 0
    AMERICAN = 1  # and increment by 1


class CalendarClockModel:  # pylint: disable=R0902
    """This model illustrates the humble object concept whereby the business logic is
    seperated from external component interfaces.
    """

    months = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
    date_style = DateStyle.BRITISH

    @staticmethod
    def leapyear(year):
        """
        The method leapyear returns True if the parameter year
        is a leap year, False otherwise
        """
        if not year % 4 == 0:
            return False
        if not year % 100 == 0:
            return True
        if not year % 400 == 0:
            return False
        return True

    @property
    def calendar_date(self):
        """Formatted date"""
        date_format = "{0:02d}/{1:02d}/{2:04d}"
        if self.date_style == DateStyle.BRITISH:
            return date_format.format(self.day, self.month, self.year)

        return date_format.format(self.month, self.day, self.year)

    @property
    def clock_time(self):
        """Formatted time"""
        time_format = "{0:02d}:{1:02d}:{2:02d}"
        return time_format.format(self.hour, self.minute, self.second)

    def __init__(self, day, month, year, hour, minute, second):  # pylint: disable=R0913
        """Init the model"""
        self.year = None
        self.month = None
        self.day = None
        self.hour = None
        self.minute = None
        self.second = None

        self.set_calendar(day, month, year)
        self.set_clock(hour, minute, second)

    def reset(self):
        """Resets the model"""
        self.day = DEFAULT_DAY
        self.month = DEFAULT_MONTH
        self.year = DEFAULT_YEAR
        self.hour = DEFAULT_HOUR
        self.minute = DEFAULT_MINUTE
        self.second = DEFAULT_SECOND
        self.date_style = DateStyle.BRITISH

    def set_calendar(self, day, month, year):
        """
        day, month, year have to be integer values and year has to be
        a four digit year number
        """

        if isinstance(day, int) and isinstance(month, int) and isinstance(year, int):
            self.day = day
            self.month = month
            self.year = year
        else:
            raise TypeError("day, month, year have to be integers!")

    def set_clock(self, hour, minute, second):
        """
        The parameters hour, minute and second have to be
        integers and must satisfy the following equations:
        0 <= h < 24
        0 <= m < 60
        0 <= s < 60
        """

        if isinstance(hour, int) and 0 <= hour < 24:
            self.hour = hour
        else:
            raise TypeError("Hour have to be integers between 0 and 23!")
        if isinstance(minute, int) and 0 <= minute < 60:
            self.minute = minute
        else:
            raise TypeError("Minute have to be integers between 0 and 59!")
        if isinstance(second, int) and 0 <= second < 60:
            self.second = second
        else:
            raise TypeError("Second have to be integers between 0 and 59!")

    def tick(self):
        """
        This method lets the clock "tick", this means that the
        internal time will be advanced by one second.

        Examples:
        >>> x = Clock(12,59,59)
        >>> print(x)
        12:59:59
        >>> x.tick()
        >>> print(x)
        13:00:00
        >>> x.tick()
        >>> print(x)
        13:00:01
        """

        if self.second == 59:
            self.second = 0
            if self.minute == 59:
                self.minute = 0
                if self.hour == 23:
                    self.hour = 0
                    self.advance()
                else:
                    self.hour += 1
            else:
                self.minute += 1
        else:
            self.second += 1

    def advance(self):
        """
        This method advances to the next date.
        """
        max_days = self.months[self.month - 1]
        if self.month == 2 and self.leapyear(self.year):
            max_days += 1
        if self.day == max_days:
            self.day = 1
            if self.month == 12:
                self.month = 1
                self.year += 1
            else:
                self.month += 1
        else:
            self.day += 1

    def switch_on(self):
        """ Some sample code of how behaviour is driven by device state"""
        current_state = self.get_device_state()

        if current_state == DevState.ON:
            return

        if current_state not in [DevState.INIT, DevState.STANDBY]:
            self.set_device_state(DevState.ON)

        if current_state == DevState.STANDBY:
            self.logger.info("Switching on from STANDBY state")
            self.set_device_state(DevState.ON)

        if current_state == DevState.INIT:
            raise Exception("'SwitchOn' command failed. CalendarClock is in 'INIT' state.")

    def switch_off(self):
        """Switch the device off"""
        if self.get_device_state() != DevState.OFF:
            self.logger.info("Swithed off CalendarClockModel")
            self.set_device_state(DevState.OFF)

    def __str__(self):
        """String representation of the model"""
        datetime_style = "{0:02d}/{1:02d}/{2:04d} {3:02d}:{4:02d}:{5:02d}"
        if self.date_style == DateStyle.BRITISH:
            return datetime_style.format(
                self.day, self.month, self.year, self.hour, self.minute, self.second
            )
        return datetime_style.format(
            self.month, self.day, self.year, self.hour, self.minute, self.second
        )


class CalendarClockDevice(SKABaseDevice):
    """The Tango device CalendarClockDevice"""

    TimeZone = device_property(dtype="str", default_value="UTC")

    def __init__(self, *args, **kwargs):
        self.model = CalendarClockModel(
            DEFAULT_DAY, DEFAULT_MONTH, DEFAULT_YEAR, DEFAULT_HOUR, DEFAULT_MINUTE, DEFAULT_SECOND
        )
        super().__init__(*args, **kwargs)

    def init_device(self):
        super().init_device()
        self.model.get_device_state = self.get_state  # pylint: disable=W0201
        self.model.set_device_state = self.set_state  # pylint: disable=W0201
        self.model.logger = self.logger  # pylint: disable=W0201
        self.model.timezone = self.TimeZone  # pylint: disable=W0201
        self.model.reset()
        self.set_state(DevState.UNKNOWN)

    @attribute(dtype=DateStyle, access=AttrWriteType.READ_WRITE)
    def date_style(self):
        """date_style attribute"""
        return self.model.date_style

    def write_date_style(self, value):
        """Set the date_style"""
        self.model.date_style = value

    @attribute
    def day(self):
        """The day of the month"""
        return self.model.day

    @attribute
    def month(self):
        """The month in the year"""
        return self.model.month

    @attribute
    def year(self):
        """The year"""
        return self.model.year

    @attribute(
        dtype=str, doc="Date string in the format 'dd/mm/yyyy'.", access=AttrWriteType.READ_WRITE
    )
    def calendar_date(self):
        """Show formatted date"""
        return self.model.calendar_date

    def write_calendar_date(self, value):
        """Set the date"""
        day, month, year = list(map(lambda x: int(x), value.split("/")))
        self.model.set_calendar(day, month, year)

    @attribute(
        dtype=str, doc="Time string in the format 'hh:mm:ss'.", access=AttrWriteType.READ_WRITE
    )
    def clock_time(self):
        """Show the formatted time"""
        return self.model.clock_time

    def write_clock_time(self, value):
        """Set the time"""
        hour, minute, second = list(map(lambda x: int(x), value.split(":")))
        self.model.set_clock(hour, minute, second)

    @attribute
    def hour(self):
        """The hour in the day"""
        return self.model.hour

    @attribute
    def minute(self):
        """The minute in the hour"""
        return self.model.minute

    @attribute
    def second(self):
        """The second in the minute"""
        return self.model.second

    @command
    def Advance(self):  # pylint: disable=C0103
        """Advande the clock 1 day"""
        self.model.advance()

    @command
    def Tick(self):  # pylint: disable=C0103
        """Advande the clock 1 second"""
        self.model.tick()

    @command
    def SwitchOn(self):  # pylint: disable=C0103
        """Swith the device on"""
        self.model.switch_on()

    @command
    def SwitchOff(self):  # pylint: disable=C0103
        """Swith the device off"""
        self.model.switch_off()

    @command(dtype_out=str)
    def GetFormattedTime(self):  # pylint: disable=C0103
        """Get the formatted string of the datetime"""
        return str(self.model)


def main(args=None, **kwargs):
    """Run CalendarClockDevice"""
    return run((CalendarClockDevice,), args=args, **kwargs)


if __name__ == "__main__":
    main()
