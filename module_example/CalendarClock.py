# pylint: disable=C0103
""" This module illustates the humble object principal whereby the business logic is
seperated from the external interfaces.

class CalendarClock
    This class is an implementation of a Tango Device. No business logic exists in this
    class.

class CalendarClockModel
    This class encapsulates all the business logic for the CalendarClock device.

class TestCalendarClockModel
    This class tests the business logic without having to instantiate the Tango Device

class TestCalendarClock
    This class uses `DeviceTestContext` to test the Tango device by instantiating the
    device class
"""

from enum import IntEnum

from tango import AttrWriteType, DevState
from tango.server import attribute, command, run

from skabase.SKABaseDevice.SKABaseDevice import SKABaseDevice


CURRENT_YEAR = 1
CURRENT_MONTH = 2
CURRENT_DAY = 3
CURRENT_HOUR = 4
CURRENT_MINUTE = 5
CURRENT_SECOND = 6


class DateStyle(IntEnum):
    """Style of the date"""

    BRITISH = 0  # DevEnum's must start at 0
    AMERICAN = 1  # and increment by 1


class CalendarClockModel:  # pylint: disable=R0902
    """This model illustrates the humble object concept whereby the business logic is
    seperated from external component interfaces.
    """

    months = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
    _date_style = DateStyle.BRITISH

    @property
    def date_style(self):
        """date-style property"""
        return self._date_style

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

    def __init__(self, day, month, year, hour, minute, second):  # pylint: disable=R0913
        """Init the model"""
        self._year = None
        self._month = None
        self._day = None
        self._hour = None
        self._minute = None
        self._second = None

        self.set_calendar(day, month, year)
        self.set_clock(hour, minute, second)

    def set_calendar(self, day, month, year):
        """
        day, month, year have to be integer values and year has to be
        a four digit year number
        """

        if isinstance(day, int) and isinstance(month, int) and isinstance(year, int):
            self._day = day
            self._month = month
            self._year = year
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
            self._hour = hour
        else:
            raise TypeError("Hour have to be integers between 0 and 23!")
        if isinstance(minute, int) and 0 <= minute < 60:
            self._minute = minute
        else:
            raise TypeError("Minute have to be integers between 0 and 59!")
        if isinstance(second, int) and 0 <= second < 60:
            self._second = second
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

        if self._second == 59:
            self._second = 0
            if self._minute == 59:
                self._minute = 0
                if self._hour == 23:
                    self._hour = 0
                else:
                    self._hour += 1
            else:
                self._minute += 1
        else:
            self._second += 1

    def advance(self):
        """
        This method advances to the next date.
        """
        max_days = self.months[self._month-1]
        if self._month == 2 and self.leapyear(self._year):
            max_days += 1
        if self._day == max_days:
            self._day = 1
            if self._month == 12:
                self._month = 1
                self._year += 1
            else:
                self._month += 1
        else:
            self._day += 1

    def swith_on(self):
        """ Some sample code of how behaviour is driven by device state"""

        if self.get_device_state() == DevState.ON:
            return

        if self.get_device_state() not in [DevState.INIT, DevState.STANDBY]:
            self.set_device_state(DevState.ON)

        if self.get_device_state() == DevState.OFF:
            self.set_device_state(DevState.ON)

    def swith_off(self):
        """Switch the device off"""
        if self.get_device_state() != DevState.OFF:
            self.set_device_state(DevState.OFF)

    def __str__(self):
        """String representation of the model"""
        datetime_style = "{0:02d}/{1:02d}/{2:04d} {3:02d}:{4:02d}:{5:02d}"
        if self._date_style == DateStyle.BRITISH:
            return datetime_style.format(
                self._day, self._month, self._year,
                self._hour, self._minute, self._second)
        return datetime_style.format(
            self._month, self._day, self._year,
            self._hour, self._minute, self._second)


class CalendarClockDevice(SKABaseDevice):
    """The Tango device CalendarClockDevice"""

    def __init__(self, *args, **kwargs):
        """Init the class"""
        SKABaseDevice.__init__(self, *args, **kwargs)

    def init_device(self):
        """Init the device"""
        SKABaseDevice.init_device(self)
        self.model = CalendarClockModel(CURRENT_DAY,
                                        CURRENT_MONTH,
                                        CURRENT_YEAR,
                                        CURRENT_HOUR,
                                        CURRENT_MINUTE,
                                        CURRENT_SECOND)
        self.model.get_device_state = self.get_state # pylint: disable=W0201
        self.model.set_device_state = self.set_state # pylint: disable=W0201
        self.set_state(DevState.UNKNOWN)

    @attribute(dtype=DateStyle, access=AttrWriteType.READ_WRITE)
    def date_style(self):
        """date_style attribute"""
        return self.model.date_style

    def write_date_style(self, value):
        """Set the date_style"""
        self.model._date_style = value  # pylint: disable=W0212

    @attribute
    def day(self):
        """The day of the month"""
        return self.model._day  # pylint: disable=W0212

    @attribute
    def month(self):
        """The month in the year"""
        return self.model._month  # pylint: disable=W0212

    @attribute
    def year(self):
        """The year"""
        return self.model._year  # pylint: disable=W0212

    @attribute
    def hour(self):
        """The hour in the day"""
        return self.model._hour  # pylint: disable=W0212

    @attribute
    def minute(self):
        """The minute in the hour"""
        return self.model._minute  # pylint: disable=W0212

    @attribute
    def second(self):
        """The second in the minute"""
        return self.model._second  # pylint: disable=W0212

    @command
    def Advance(self): # pylint: disable=C0103
        """Advande the clock 1 day"""
        self.model.advance()

    @command
    def Tick(self): # pylint: disable=C0103
        """Advande the clock 1 second"""
        self.model.tick()

    @command
    def SwitchOn(self): # pylint: disable=C0103
        """Swith the device on"""
        self.model.swith_on()

    @command
    def SwitchOff(self): # pylint: disable=C0103
        """Swith the device off"""
        self.model.swith_off()

    @command(dtype_out=str)
    def GetFormattedTime(self): # pylint: disable=C0103
        """Get the formatted string of the datetime"""
        return str(self.model)


def main(args=None, **kwargs):
    """Run CalendarClockDevice"""
    return run((CalendarClockDevice,), args=args, **kwargs)

if __name__ == '__main__':
    main()
