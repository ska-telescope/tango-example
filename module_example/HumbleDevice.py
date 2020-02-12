from datetime import datetime

from tango import AttrQuality, AttrWriteType, DispLevel, DevState, DevFailed, DeviceProxy
from tango.server import attribute, command, device_property
from tango import Database, DbDevInfo, DbServerInfo

from skabase.SKABaseDevice.SKABaseDevice import SKABaseDevice


class PrinterScannerModel:
    
    def print(self):
        pass
    
    def copy(self):
        pass
    
    def scan(self):
        pass


class CalendarClock:

    months = (31,28,31,30,31,30,31,31,30,31,30,31)
    date_style = "British"

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
        self.set_Calendar(day, month, year)
        self.set_Clock(hour, minute, second)
        # self._days = day
        # self._months = month
        # self._years = year
        # self._hours = hours
        # self._minutes = minutes
        # self._seconds = seconds

    def set_Calendar(self, day, month, year):
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
    
    def set_Clock(self, hour, minute, second):
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

        max_days = self.months[self.__months-1]
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

    def __str__(self):
        if self.date_style == "British":
            return "{0:02d}/{1:02d}/{2:4d}".format(self._day,
                                                   self._month,
                                                   self._year) + \
                   "{0:02d}:{1:02d}:{2:02d}".format(self._hour,
                                                self._minute,
                                                self._second)
        else: 
            # assuming American style
            return "{0:02d}/{1:02d}/{2:4d}".format(self._month,
                                                   self._day,
                                                   self._year) + \
                    "{0:02d}:{1:02d}:{2:02d}".format(self._hour,
                                                self._minute,
                                                self._second)
                            

class HumbleDevice(SKABaseDevice):

    def __init__(self, *args, **kwargs):
        SKABaseDevice.__init__(self, *args, **kwargs)
        
    def init_device(self):
        SKABaseDevice.init_device(self)
        nou = datetime.now()
        self.model = CalendarClock(
            nou.day, nou.month, nou.year, nou.hour, nou.minute, nou.second
        )

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


if __name__ == "__main__":
    
    db = Database()
    humble_device_one = DbDevInfo()
    humble_device_one.name = 'test/humbleobject/1'
    humble_device_one._class = 'HumbleDevice'
    humble_device_one.server = 'HumbleDevice/test'
    db.add_server(humble_device_one.server, humble_device_one, with_dserver=True)
    HumbleDevice.run_server()







































# class Logic:
    
#     def __init__(self):
#         self._read_activity_message = "CONST.STR_INIT_LEAF_NODE"
#         self.SkaLevel = 3
#         self.el = 50.0
#         self.az = 0
#         self.RaDec_AzEl_Conversion = False
#         self.ele_max_lim = 90
#         self.horizon_el = 0
#         self.ele_min_lim = 17.5
#         self.dish_name = 'd1'
#         self.observer_location_lat = '18:31:48:00'
#         self.observer_location_long = '73:50:23.99'
#         self.observer_altitude = 570
#         self.el_limit = False

#         self._admin_mode = 0                                    #Setting adminMode to "ONLINE"
#         self._health_state = 0                                  #Setting healthState to "OK"
#         self._simulation_mode = False                           #Enabling the simulation mode

#         self._event_ids = set()

#         print("Logic!!!")

#     def subscribe_to_event(self, proxy, event_type, event_callback, attribute_name=None):

#         try:
#             if event_type == tango.EventType.INTERFACE_CHANGE_EVENT:
#                 subs = lambda etype: proxy.subscribe_event(
#                     etype, event_callback)
#                 self._interface_change_event_id = subs(event_type)
#             else:
#                 subs = lambda etype: proxy.subscribe_event(
#                     attribute_name, etype, event_callback, stateless=True)
#                 self._event_ids.add(subs(event_type))
#         except tango.DevFailed as exc:
#             log_msg = "Exception occurred while subscribing to Dish attributes" + str(dev_failed)
#             self.logger.error(log_msg)
#             self._read_activity_message = "Exception occurred while subscribing to Dish attributes" + str(dev_failed)
#             exc_reasons = set([arg.reason for arg in exc.args])
#             if 'API_AttributePollingNotStarted' in exc_reasons:
#                 pass
#             elif 'API_EventPropertiesNotSet' in exc_reasons:
#                 pass
#             else:
#                 raiseclass Logic:
    
#     def __init__(self):
#         self._read_activity_message = "CONST.STR_INIT_LEAF_NODE"
#         self.SkaLevel = 3
#         self.el = 50.0
#         self.az = 0
#         self.RaDec_AzEl_Conversion = False
#         self.ele_max_lim = 90
#         self.horizon_el = 0
#         self.ele_min_lim = 17.5
#         self.dish_name = 'd1'
#         self.observer_location_lat = '18:31:48:00'
#         self.observer_location_long = '73:50:23.99'
#         self.observer_altitude = 570
#         self.el_limit = False

#         self._admin_mode = 0                                    #Setting adminMode to "ONLINE"
#         self._health_state = 0                                  #Setting healthState to "OK"
#         self._simulation_mode = False                           #Enabling the simulation mode

#         self._event_ids = set()

#         print("Logic!!!")

#     def subscribe_to_event(self, proxy, event_type, event_callback, attribute_name=None):

#         try:
#             if event_type == tango.EventType.INTERFACE_CHANGE_EVENT:
#                 subs = lambda etype: proxy.subscribe_event(
#                     etype, event_callback)
#                 self._interface_change_event_id = subs(event_type)
#             else:
#                 subs = lambda etype: proxy.subscribe_event(
#                     attribute_name, etype, event_callback, stateless=True)
#                 self._event_ids.add(subs(event_type))
#         except tango.DevFailed as exc:
#             log_msg = "Exception occurred while subscribing to Dish attributes" + str(dev_failed)
#             self.logger.error(log_msg)
#             self._read_activity_message = "Exception occurred while subscribing to Dish attributes" + str(dev_failed)
#             exc_reasons = set([arg.reason for arg in exc.args])
#             if 'API_AttributePollingNotStarted' in exc_reasons:
#                 pass
#             elif 'API_EventPropertiesNotSet' in exc_reasons:
#                 pass
#             else:
#                 raise