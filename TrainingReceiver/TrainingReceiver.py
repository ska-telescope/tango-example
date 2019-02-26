# -*- coding: utf-8 -*-
#
# This file is part of the TrainingReceiver project
#
# matteo
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" TrainingReceiver

TrainingReceiver
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
# PROTECTED REGION ID(TrainingReceiver.additionnal_import) ENABLED START #
from tango import DeviceProxy
# PROTECTED REGION END #    //  TrainingReceiver.additionnal_import

__all__ = ["TrainingReceiver", "main"]


class TrainingReceiver(Device):
    """
    TrainingReceiver
    """
    __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(TrainingReceiver.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  TrainingReceiver.class_variable

    # ----------
    # Attributes
    # ----------

    EventReceived = attribute(
        dtype='bool',
    )

    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        Device.init_device(self)
        # PROTECTED REGION ID(TrainingReceiver.init_device) ENABLED START #
        try:
            self.dev = DeviceProxy("test/new_motor/1")
        except:
            print ("Unexpected error on DeviceProxy creation:", sys.exc_info()[0])

        try:
            self.dev.subscribe_event("Performance", PyTango.EventType.CHANGE_EVENT, self.HandleEvent, stateless=True)
        except:
            print ("Unexpected error on (subscribe_event):", sys.exc_info()[0])

        try:
            self.attr_EventReceived = False
        except:
            print ("Unexpected error on (self.attr_EventReceived = False):", sys.exc_info()[0])
        # PROTECTED REGION END #    //  TrainingReceiver.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(TrainingReceiver.always_executed_hook) ENABLED START #
        pass
        # PROTECTED REGION END #    //  TrainingReceiver.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(TrainingReceiver.delete_device) ENABLED START #
        pass
        # PROTECTED REGION END #    //  TrainingReceiver.delete_device


    def HandleEvent (self, args):
        try:
            print("Event arrived")
            self.attr_EventReceived = True
        except:
            print ("Unexpected error on (self.attr_EventReceived = False):", sys.exc_info()[0])
    # ------------------
    # Attributes methods
    # ------------------

    def read_EventReceived(self):
        # PROTECTED REGION ID(TrainingReceiver.EventReceived_read) ENABLED START #
        return self.attr_EventReceived
        # PROTECTED REGION END #    //  TrainingReceiver.EventReceived_read


    # --------
    # Commands
    # --------

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(TrainingReceiver.main) ENABLED START #
    return run((TrainingReceiver,), args=args, **kwargs)
    # PROTECTED REGION END #    //  TrainingReceiver.main

if __name__ == '__main__':
    main()
