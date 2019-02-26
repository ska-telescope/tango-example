# -*- coding: utf-8 -*-
#
# This file is part of the Motor2 project
#
# Matteo
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" Motor2

Motor2
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
# PROTECTED REGION ID(Motor2.additionnal_import) ENABLED START #
# PROTECTED REGION END #    //  Motor2.additionnal_import

__all__ = ["Motor2", "main"]


class Motor2(Device):
    """
    Motor2
    """
    __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(Motor2.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  Motor2.class_variable

    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        Device.init_device(self)
        # PROTECTED REGION ID(Motor2.init_device) ENABLED START #
        # PROTECTED REGION END #    //  Motor2.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(Motor2.always_executed_hook) ENABLED START #
        pass
        # PROTECTED REGION END #    //  Motor2.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(Motor2.delete_device) ENABLED START #
        pass
        # PROTECTED REGION END #    //  Motor2.delete_device


    # --------
    # Commands
    # --------

    @command(
    )
    @DebugIt()
    def Start(self):
        # PROTECTED REGION ID(Motor2.Start) ENABLED START #
        self.set_state(DevState.RUNNING)
        # PROTECTED REGION END #    //  Motor2.Start

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(Motor2.main) ENABLED START #
    return run((Motor2,), args=args, **kwargs)
    # PROTECTED REGION END #    //  Motor2.main

if __name__ == '__main__':
    main()
