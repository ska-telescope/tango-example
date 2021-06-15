# -*- coding: utf-8 -*-
#
# This file is part of the Counter project
#
# SKA
# INAF
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" ska-tango-examples

A simple counter:
- increment
- decrement
- reset
"""

# PyTango imports
from tango import AttrWriteType, DebugIt
from tango.server import Device, attribute, command, run

# Additional import
# PROTECTED REGION ID(Counter.additionnal_import) ENABLED START #

# PROTECTED REGION END #    //  Counter.additionnal_import

__all__ = ["Counter", "main"]


class Counter(Device):
    """
    This Device demonstrate the use of the TANGO event mechanism
    to send change events to clients.
    There's also a device attribute in polling so that events
    for that attribute are sent automatically.
    """

    # PROTECTED REGION ID(Counter.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  Counter.class_variable

    # ----------
    # Attributes
    # ----------

    value = attribute(
        dtype="DevShort",
    )

    fire_event_at = attribute(
        dtype="DevShort",
        access=AttrWriteType.READ_WRITE,
    )

    polled_value = attribute(
        dtype="DevShort",
        period=1000,
        abs_change=1,
    )

    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        """Initialises the attributes and properties of the Counter."""
        Device.init_device(self)
        # PROTECTED REGION ID(Counter.init_device) ENABLED START #
        self._value = 0
        self._fire_event_at = 0
        self.set_change_event("value", True, False)
        self.set_change_event("polled_value", True, True)
        # PROTECTED REGION END #    //  Counter.init_device

    def always_executed_hook(self):
        """Method always executed before any TANGO command is executed."""
        # PROTECTED REGION ID(Counter.always_executed_hook) ENABLED START #
        # PROTECTED REGION END #    //  Counter.always_executed_hook

    def delete_device(self):
        """Hook to delete resources allocated in init_device.

        This method allows for any memory or other resources allocated in the
        init_device method to be released.  This method is called by the device
        destructor and by the device Init command.
        """
        # PROTECTED REGION ID(Counter.delete_device) ENABLED START #
        # PROTECTED REGION END #    //  Counter.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_value(self):
        # PROTECTED REGION ID(Counter.value_read) ENABLED START #
        """Return the value attribute."""
        return self._value
        # PROTECTED REGION END #    //  Counter.value_read

    def read_fire_event_at(self):
        # PROTECTED REGION ID(Counter.fire_event_at_read) ENABLED START #
        """Return the fire_event_at attribute."""
        return self._fire_event_at
        # PROTECTED REGION END #    //  Counter.fire_event_at_read

    def write_fire_event_at(self, value):
        # PROTECTED REGION ID(Counter.fire_event_at_write) ENABLED START #
        """Set the fire_event_at attribute."""
        self._fire_event_at = value
        # PROTECTED REGION END #    //  Counter.fire_event_at_write

    def read_polled_value(self):
        # PROTECTED REGION ID(Counter.polled_value_read) ENABLED START #
        """Return the polled_value attribute."""
        return self._value
        # PROTECTED REGION END #    //  Counter.polled_value_read

    # --------
    # Commands
    # --------

    @command(
        dtype_out="DevShort",
    )
    @DebugIt()
    def increment(self):
        # PROTECTED REGION ID(Counter.increment) ENABLED START #
        """
        Increment the value of the counter by 1

        :return:'DevShort'
        """
        self._value += 1
        if self._value == self._fire_event_at:
            self.push_change_event("value", self._value)
        return self._value
        # PROTECTED REGION END #    //  Counter.increment

    @command(
        dtype_out="DevShort",
    )
    @DebugIt()
    def decrement(self):
        # PROTECTED REGION ID(Counter.decrement) ENABLED START #
        """
        Decrement the value of the counter by 1

        :return:'DevShort'
        """
        self._value -= 1
        if self._value == self._fire_event_at:
            self.push_change_event("value", self._value)
        return self._value
        # PROTECTED REGION END #    //  Counter.decrement

    @command(
        dtype_in="DevShort",
        dtype_out="DevShort",
    )
    @DebugIt()
    def CounterReset(self, argin):
        # PROTECTED REGION ID(Counter.CounterReset) ENABLED START #
        """
        Reset the counter to the input parameter

        :param argin: 'DevShort'

        :return:'DevShort'
        """
        self._value = argin
        if self._value == self._fire_event_at:
            self.push_change_event("value", self._value)
        return self._value
        # PROTECTED REGION END #    //  Counter.CounterReset


# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    """Main function of the Counter module."""
    # PROTECTED REGION ID(Counter.main) ENABLED START #
    return run((Counter,), args=args, **kwargs)
    # PROTECTED REGION END #    //  Counter.main


if __name__ == "__main__":
    main()
