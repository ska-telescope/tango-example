# -*- coding: utf-8 -*-
#
# This file is part of the Motor project
#
# GPL v3
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" Motor

Motor training example
"""

# PyTango imports
import PyTango
from PyTango import DebugIt
from PyTango.server import run
from PyTango.server import Device, DeviceMeta
from PyTango.server import attribute, command
from PyTango import AttrQuality, DispLevel, DevState
from PyTango import AttrWriteType, PipeWriteType
# Additional import
# PROTECTED REGION ID(Motor.additionnal_import) ENABLED START #
import random
from tango import DeviceProxy
# PROTECTED REGION END #    //  Motor.additionnal_import

__all__ = ["Motor", "main"]


class Motor(Device):
    """
    Motor training example
    """
    __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(Motor.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  Motor.class_variable

    # ----------
    # Attributes
    # ----------

    PerformanceValue = attribute(
        dtype='double', polling_period=2000, abs_change=10, rel_change=10,
    )

    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        Device.init_device(self)
        self.set_change_event("PerformanceValue", True, False)
        # PROTECTED REGION ID(Motor.init_device) ENABLED START #
        self.powerSupply = DeviceProxy("test/power_supply/1")
        self.set_change_event("PerformanceValue", True)
        # PROTECTED REGION END #    //  Motor.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(Motor.always_executed_hook) ENABLED START #
        pass
        # PROTECTED REGION END #    //  Motor.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(Motor.delete_device) ENABLED START #
        pass
        # PROTECTED REGION END #    //  Motor.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_PerformanceValue(self):
        # PROTECTED REGION ID(Motor.PerformanceValue_read) ENABLED START #
        return random.uniform(0, 1)
        # PROTECTED REGION END #    //  Motor.PerformanceValue_read


    # --------
    # Commands
    # --------

    @command(
    )
    @DebugIt()
    def TurnOn(self):
        # PROTECTED REGION ID(Motor.TurnOn) ENABLED START #
        try: 
            power_state = self.powerSupply.state()
            if(power_state != DevState.ON):
                self.powerSupply.turn_on()
        except:
            print("No power state")

        self.set_state(DevState.ON)
        # PROTECTED REGION END #    //  Motor.TurnOn

    @command(
    )
    @DebugIt()
    def TurnOff(self):
        # PROTECTED REGION ID(Motor.TurnOff) ENABLED START #
        self.set_state(DevState.OFF)
        # PROTECTED REGION END #    //  Motor.TurnOff

    @command(
    )
    @DebugIt()
    def Start(self):
        # PROTECTED REGION ID(Motor.Start) ENABLED START #
        self.set_state(DevState.RUNNING)
        # PROTECTED REGION END #    //  Motor.Start

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(Motor.main) ENABLED START #
    return run((Motor,), args=args, **kwargs)
    # PROTECTED REGION END #    //  Motor.main

if __name__ == '__main__':
    main()
