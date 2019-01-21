#!/usr/bin/env python, SerialModel
# -*- coding: utf-8 -*-

"""Demo power supply tango device server"""

import time
import numpy

from tango import AttrQuality, AttrWriteType, DispLevel, DevState, DebugIt, GreenMode, SerialModel, Util, Interceptors
from tango.server import Device, attribute, command, pipe, device_property


import sys
# pydevd.settrace('10.254.254.254', port=23232, stdoutToServer=True, stderrToServer=True, suspend=False, trace_only_current_thread=False, patch_multiprocessing=True)
# import threading
# threading.settrace(pydevd.GetGlobalDebugger().trace_dispatch)


# class MyInter(Interceptors):
#     @DebugIt
#     def create_thread(self):
#         print('Hello!')
#         pydevd.settrace(suspend=True, trace_only_current_thread=True)
#
#     def delete_thread(self):
#         pass
#
#
# class TracingMixin(object):
#     """The callbacks in the FUSE Filesystem are C threads and breakpoints don't work normally.
#        This mixin adds callbacks to every function call so that we can breakpoint them."""
#
#     def __call__(self, op, path, *args):
#         pydevd.settrace(suspend=False, trace_only_current_thread=True, patch_multiprocessing=True)
#         return getattr(self, op)(path, *args)


class PowerSupply(Device):
    # green_mode = GreenMode.Asyncio

    voltage = attribute(label="Voltage", dtype=float,
                        display_level=DispLevel.OPERATOR,
                        access=AttrWriteType.READ,
                        unit="V", format="8.4f",
                        doc="the power supply voltage")

    current = attribute(label="Current", dtype=float,
                        display_level=DispLevel.EXPERT,
                        access=AttrWriteType.READ_WRITE,
                        unit="A", format="8.4f",
                        min_value=0.0, max_value=8.5,
                        min_alarm=0.1, max_alarm=8.4,
                        min_warning=0.5, max_warning=8.0,
                        fget="get_current",
                        fset="set_current",
                        doc="the power supply current")

    noise = attribute(label="Noise",
                      dtype=((int,),),
                      max_dim_x=1024, max_dim_y=1024)

    host = device_property(dtype=str)
    port = device_property(dtype=int, default_value=9788)

    def  init_device(self):
        Device.init_device(self)
        self.__current = 0.0
        self.set_state(DevState.STANDBY)

    def  read_voltage(self):
        self.info_stream("read_voltage(%s, %d)", self.host, self.port)
        return 240, time.time(), AttrQuality.ATTR_VALID

    def  get_current(self):
        return self.__current

    def  set_current(self, current):
        # pydevd.settrace('10.254.254.254', port=23232, stdoutToServer=True, stderrToServer=True, suspend=True, trace_only_current_thread=False, patch_multiprocessing=True)
        # should set the power supply current
        self.__current = current

    def  read_info(self):
        return 'Information', dict(manufacturer='Tango',
                                   model='PS2000',
                                   version_number=123)

    @DebugIt()
    def  read_noise(self):
        return numpy.random.random_integers(1000, size=(100, 100))

    @command
    def  TurnOn(self):
        # turn on the actual power supply here
        self.set_state(DevState.ON)

    @command
    def  TurnOff(self):
        # turn off the actual power supply here
        self.set_state(DevState.OFF)

    @command(dtype_in=float, doc_in="Ramp target current",
             dtype_out=bool, doc_out="True if ramping went well, "
             "False otherwise")
    def  Ramp(self, target_current):
        # should do the ramping
        return True


if __name__ == "__main__":
    # trick util to execute orb_run instead of the usual server_run
    import tango
    util = tango.Util([])
    util._original_server_run = util.server_run
    util.server_run = util.orb_run
    PowerSupply.run_server(['test'])