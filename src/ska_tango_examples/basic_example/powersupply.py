#!/usr/bin/env python, SerialModel
# -*- coding: utf-8 -*-

"""Demo power supply tango device server"""

import time

import numpy
from tango import DevState  # GreenMode
from tango import AttrQuality, AttrWriteType, DebugIt, DispLevel
from tango.server import Device, attribute, command, device_property


class PowerSupply(Device):
    """
    Example power supply device from the PyTango documentation.
    """

    # green_mode = GreenMode.Asyncio

    voltage = attribute(
        label="Voltage",
        dtype=float,
        display_level=DispLevel.OPERATOR,
        access=AttrWriteType.READ,
        unit="V",
        format="8.4f",
        doc="the power supply voltage",
    )

    current = attribute(
        label="Current",
        dtype=float,
        display_level=DispLevel.EXPERT,
        access=AttrWriteType.READ_WRITE,
        unit="A",
        format="8.4f",
        min_value=0.0,
        max_value=8.5,
        min_alarm=0.1,
        max_alarm=8.4,
        min_warning=0.5,
        max_warning=8.0,
        fget="get_current",
        fset="set_current",
        doc="the power supply current",
    )

    noise = attribute(
        label="Noise", dtype=((int,),), max_dim_x=1024, max_dim_y=1024
    )

    host = device_property(dtype=str)
    port = device_property(dtype=int, default_value=9788)

    def __init__(self, device_class, device_name):
        super().__init__(device_class, device_name)
        self.__current = 0.0

    def init_device(self):
        """Initialise device"""
        Device.init_device(self)
        self.set_current(0.0)
        self.set_state(DevState.STANDBY)

    def read_voltage(self):
        """Read voltage"""
        self.info_stream("read_voltage(%s, %d)", self.host, self.port)
        return 240, time.time(), AttrQuality.ATTR_VALID

    def get_current(self):
        """Get the current"""
        return self.__current

    def set_current(self, current):
        """Set the current"""
        self.__current = current

    def read_info(self):
        """Get device information"""
        return "Information", dict(
            manufacturer="Tango", model="PS2000", version_number=123
        )

    @DebugIt()
    def read_noise(self):
        """Get a matrix of random noise"""
        return numpy.random.random_integers(1000, size=(100, 100))

    @command
    def turn_on(self):
        """Turn the device on"""
        # turn on the actual power supply here
        self.set_state(DevState.ON)

    @command
    def turn_off(self):
        """Turn the device off"""
        # turn off the actual power supply here
        self.set_state(DevState.OFF)

    @command(
        dtype_in=float,
        doc_in="Ramp target current",
        dtype_out=bool,
        doc_out="True if ramping went well, " "False otherwise",
    )
    def ramp(self, target_current):
        """Ramp voltage to the target current"""
        # should do the ramping. This doesn't.
        self.set_current(target_current)
        return True


if __name__ == "__main__":
    PowerSupply.run_server()
    # PowerSupply.run_server(['test'])
