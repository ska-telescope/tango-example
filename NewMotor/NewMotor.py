# -*- coding: utf-8 -*-
#
# This file is part of the NewMotor project
#
# Matteo
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" NewMotor

NewMotor
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
# PROTECTED REGION ID(NewMotor.additionnal_import) ENABLED START #
import random
# PROTECTED REGION END #    //  NewMotor.additionnal_import

__all__ = ["NewMotor", "main"]


class NewMotor(Device):
    """
    NewMotor
    """
    __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(NewMotor.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  NewMotor.class_variable

    # ----------
    # Attributes
    # ----------

    Performance = attribute(
        dtype='double', polling_period=3000, rel_change=5,
    )

    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        Device.init_device(self)
        self.set_change_event("Performance", True, False)
        # PROTECTED REGION ID(NewMotor.init_device) ENABLED START #
        # PROTECTED REGION END #    //  NewMotor.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(NewMotor.always_executed_hook) ENABLED START #
        pass
        # PROTECTED REGION END #    //  NewMotor.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(NewMotor.delete_device) ENABLED START #
        pass
        # PROTECTED REGION END #    //  NewMotor.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_Performance(self):
        # PROTECTED REGION ID(NewMotor.Performance_read) ENABLED START #
        return random.uniform(0, 1)
        # PROTECTED REGION END #    //  NewMotor.Performance_read


    # --------
    # Commands
    # --------

    @command(
    )
    @DebugIt()
    def Start(self):
        # PROTECTED REGION ID(NewMotor.Start) ENABLED START #
        self.set_state(DevState.RUNNING)
        # PROTECTED REGION END #    //  NewMotor.Start

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(NewMotor.main) ENABLED START #
    return run((NewMotor,), args=args, **kwargs)
    # PROTECTED REGION END #    //  NewMotor.main

if __name__ == '__main__':
    main()
