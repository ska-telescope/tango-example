import tango

def get_calendar_day(dev_name):
    """what day is it today"""
    dp = tango.DeviceProxy(dev_name)
    return dp.read_attribute("day")

def get_calendar_date(dev_name):
    """what date is it today"""
    dp = tango.DeviceProxy(dev_name)
    return dp.read_attribute("calendar_date")
