# -*- coding: utf-8 -*-
#
# This file is part of the Motor project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" Motor

"""

# PyTango imports
import PyTango
from PyTango import DebugIt
from PyTango.server import run
from PyTango.server import Device, DeviceMeta
from PyTango.server import command
from PyTango import AttrQuality, DispLevel, DevState
from PyTango import AttrWriteType, PipeWriteType
# Additional import
# PROTECTED REGION ID(Motor.additionnal_import) ENABLED START #
# PROTECTED REGION END #    //  Motor.additionnal_import

__all__ = ["Motor", "main"]


class Motor(Device):
    """
    """
    __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(Motor.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  Motor.class_variable

    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        Device.init_device(self)
        # PROTECTED REGION ID(Motor.init_device) ENABLED START #
        # PROTECTED REGION END #    //  Motor.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(Motor.always_executed_hook) ENABLED START #
        pass
        # PROTECTED REGION END #    //  Motor.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(Motor.delete_device) ENABLED START #
        pass
        # PROTECTED REGION END #    //  Motor.delete_device


    # --------
    # Commands
    # --------

    @command(
    )
    @DebugIt()
    def start(self):
        # PROTECTED REGION ID(Motor.start) ENABLED START #
        self.SetState(DevState.ON)
        # PROTECTED REGION END #    //  Motor.start

    @command(
    )
    @DebugIt()
    def stop(self):
        # PROTECTED REGION ID(Motor.stop) ENABLED START #
        self.SetState(DevState.OFF)
        # PROTECTED REGION END #    //  Motor.stop

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(Motor.main) ENABLED START #
    return run((Motor,), args=args, **kwargs)
    # PROTECTED REGION END #    //  Motor.main

if __name__ == '__main__':
    main()
