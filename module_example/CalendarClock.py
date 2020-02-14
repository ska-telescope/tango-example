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
from datetime import datetime

from tango import AttrQuality, AttrWriteType, DispLevel, DevState, DevFailed, DeviceProxy
from tango.server import attribute, command, device_property
from tango import Database, DbDevInfo, DbServerInfo


from skabase.SKABaseDevice.SKABaseDevice import SKABaseDevice


CURRENT_YEAR = 1
CURRENT_MONTH = 2
CURRENT_DAY = 3
CURRENT_HOUR = 4
CURRENT_MINUTE = 5
CURRENT_SECOND = 6


class DateStyle(IntEnum):
    BRITISH = 0  # DevEnum's must start at 0
    AMERICAN = 1  # and increment by 1


class CalendarClockModel:
    """This model illustrates the humble object concept whereby the business logic is
    seperated from external component interfaces.
    """

    months = (31,28,31,30,31,30,31,31,30,31,30,31)
    _date_style = DateStyle.BRITISH

    @property
    def date_style(self):
        return self._date_style

    @staticmethod
    def leapyear(year):
        """
        The method leapyear returns True if the parameter year
        is a leap year, False otherwise
        """
        if not year % 4 == 0:
            return False
        elif not year % 100 == 0:
            return True
        elif not year % 400 == 0:
            return False
        else:
            return True

    def __init__(self, day, month, year, hour, minute, second):
        self.set_calendar(day, month, year)
        self.set_clock(hour, minute, second)

    def set_calendar(self, day, month, year):
        """
        day, month, year have to be integer values and year has to be
        a four digit year number
        """

        if type(day) == int and type(month) == int and type(year) == int:
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

        if type(hour) == int and 0 <= hour and hour < 24:
            self._hour = hour
        else:
            raise TypeError("Hour have to be integers between 0 and 23!")
        if type(minute) == int and 0 <= minute and minute < 60:
            self._minute = minute
        else:
            raise TypeError("Minute have to be integers between 0 and 59!")
        if type(second) == int and 0 <= second and second < 60:
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
            self._day= 1
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
        if self.get_device_state() != DevState.OFF:
            self.set_device_state(DevState.OFF)

    def __str__(self):
        datetime_style = "{0:02d}/{1:02d}/{2:04d} {3:02d}:{4:02d}:{5:02d}"
        if self._date_style == DateStyle.BRITISH:
            return datetime_style.format(
                self._day, self._month, self._year,
                self._hour, self._minute, self._second)
        elif self._date_style == DateStyle.AMERICAN:
            return datetime_style.format(
                self._month, self._day, self._year,
                self._hour, self._minute, self._second)


class CalendarClockDevice(SKABaseDevice):

    def __init__(self, *args, **kwargs):
        SKABaseDevice.__init__(self, *args, **kwargs)

    def init_device(self):
        SKABaseDevice.init_device(self)
        self.model = CalendarClockModel(CURRENT_DAY,
                                        CURRENT_MONTH,
                                        CURRENT_YEAR,
                                        CURRENT_HOUR,
                                        CURRENT_MINUTE,
                                        CURRENT_SECOND)
        self.model.get_device_state = self.get_state
        self.model.set_device_state = self.set_state
        self.set_state(DevState.UNKNOWN)

    @attribute(dtype=DateStyle, access=AttrWriteType.READ_WRITE)
    def date_style(self):
        return self.model.date_style

    def write_date_style(self, value):
        self.model._date_style = value

    @attribute
    def day(self):
        return self.model._day

    @attribute
    def month(self):
        return self.model._month

    @attribute
    def year(self):
        return self.model._year

    @attribute
    def hour(self):
        return self.model._hour

    @attribute
    def minute(self):
        return self.model._minute

    @attribute
    def second(self):
        return self.model._second

    @command
    def Advance(self):
        self.model.advance()

    @command
    def Tick(self):
        self.model.tick()

    @command
    def SwitchOn(self):
        self.model.swith_on()

    @command
    def SwitchOff(self):
        self.model.swith_off()

    @command(dtype_out=str)
    def GetFormattedTime(self):
        return str(self.model)


if __name__ == "__main__":

    db = Database()
    humble_device_one = DbDevInfo()
    humble_device_one.name = 'test/humbleobject/1'
    humble_device_one._class = 'CalendarClock'
    humble_device_one.server = 'CalendarClock/test'
    db.add_server(humble_device_one.server, humble_device_one, with_dserver=True)
    CalendarClock.run_server()
