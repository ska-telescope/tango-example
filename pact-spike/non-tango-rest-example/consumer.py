import tango

def get_voltage(dev_name):
    """what is the power supply voltage"""
    dp = tango.DeviceProxy(dev_name)
    return dp.read_attribute("voltage")

def get_current(dev_name):
    """what is the power supply current"""
    dp = tango.DeviceProxy(dev_name)
    return dp.read_attribute("current")
