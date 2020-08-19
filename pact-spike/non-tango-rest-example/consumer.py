import tango


class PowerSupplyConsumer:

    def __init__(self, dev_name):
        self.dev_name = dev_name
        self.dp = tango.DeviceProxy(self.dev_name)

    def get_voltage_attr(self):
        """what is the power supply voltage"""
        return self.dp.read_attribute("voltage")

    def get_current(self):
        """what is the power supply current"""
        return self.dp.current

    def ramp_command(self, target_current):
        return self.dp.ramp(target_current)
