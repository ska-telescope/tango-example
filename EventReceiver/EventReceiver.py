# -*- coding: utf-8 -*-
#
# This file is part of the EventReceiver project
#
# Matteo Di Carlo
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" EventReceiver

EventReceiver Training Example
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
# PROTECTED REGION ID(EventReceiver.additionnal_import) ENABLED START #
from tango import DeviceProxy
# PROTECTED REGION END #    //  EventReceiver.additionnal_import

__all__ = ["EventReceiver", "main"]


class EventReceiver(Device):
    """
    EventReceiver Training Example
    """
    __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(EventReceiver.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  EventReceiver.class_variable

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
        # PROTECTED REGION ID(EventReceiver.init_device) ENABLED START #
        try:
            self.dev = DeviceProxy("test/motor/1")
        except:
            print ("Unexpected error on DeviceProxy creation:", sys.exc_info()[0])

        try:
            self.dev.subscribe_event("PerformanceValue", PyTango.EventType.CHANGE_EVENT, self.HandleEvent, stateless=True)
        except:
            print ("Unexpected error on (subscribe_event):", sys.exc_info()[0])

        try:
            self.attr_EventReceived = False
        except:
            print ("Unexpected error on (self.attr_EventReceived = False):", sys.exc_info()[0])

        # PROTECTED REGION END #    //  EventReceiver.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(EventReceiver.always_executed_hook) ENABLED START #
        pass
        # PROTECTED REGION END #    //  EventReceiver.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(EventReceiver.delete_device) ENABLED START #
        pass
        # PROTECTED REGION END #    //  EventReceiver.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_EventReceived(self):
        # PROTECTED REGION ID(EventReceiver.EventReceived_read) ENABLED START #
        try:
            return self.attr_EventReceived
        except: 
            print ("Unexpected error on (self.attr_EventReceived = False):", sys.exc_info()[0])
        # PROTECTED REGION END #    //  EventReceiver.EventReceived_read


    # --------
    # Commands
    # --------

    def HandleEvent (self, args):
        try:
            print("Event arrived")
            self.attr_EventReceived = True
        except:
            print ("Unexpected error on (self.attr_EventReceived = False):", sys.exc_info()[0])

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(EventReceiver.main) ENABLED START #
    return run((EventReceiver,), args=args, **kwargs)
    # PROTECTED REGION END #    //  EventReceiver.main

if __name__ == '__main__':
    main()
