# -*- coding: utf-8 -*-
#
# This file is part of the TangoWorkshopCounter project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" TangoWorkshopCounter

TangoWorkshopCounter
"""

# PyTango imports
from tango import DebugIt
from tango.server import Device, attribute, command, run

# Additional import
# PROTECTED REGION ID(TangoWorkshopCounter.additionnal_import) ENABLED START #
# PROTECTED REGION END #    //  TangoWorkshopCounter.additionnal_import

__all__ = ["TangoWorkshopCounter", "main"]


class TangoWorkshopCounter(Device):
    """
    TangoWorkshopCounter
    """

    # PROTECTED REGION ID(TangoWorkshopCounter.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  TangoWorkshopCounter.class_variable

    # ----------
    # Attributes
    # ----------

    value = attribute(
        dtype="DevShort",
    )

    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        """Initialises the attributes and properties of the TangoWorkshopCounter."""
        Device.init_device(self)
        # PROTECTED REGION ID(TangoWorkshopCounter.init_device) ENABLED START #
        self._value = 0
        # PROTECTED REGION END #    //  TangoWorkshopCounter.init_device

    def always_executed_hook(self):
        """Method always executed before any TANGO command is executed."""
        # PROTECTED REGION ID(TangoWorkshopCounter.always_executed_hook) ENABLED START #
        # PROTECTED REGION END #    //  TangoWorkshopCounter.always_executed_hook

    def delete_device(self):
        """Hook to delete resources allocated in init_device.

        This method allows for any memory or other resources allocated in the
        init_device method to be released.  This method is called by the device
        destructor and by the device Init command.
        """
        # PROTECTED REGION ID(TangoWorkshopCounter.delete_device) ENABLED START #
        # PROTECTED REGION END #    //  TangoWorkshopCounter.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_value(self):
        # PROTECTED REGION ID(TangoWorkshopCounter.value_read) ENABLED START #
        """Return the value attribute."""
        return self._value
        # PROTECTED REGION END #    //  TangoWorkshopCounter.value_read

    # --------
    # Commands
    # --------

    @command()
    @DebugIt()
    def increment(self):
        # PROTECTED REGION ID(TangoWorkshopCounter.increment) ENABLED START #
        """

        :return:None
        """
        self._value += 1
        # PROTECTED REGION END #    //  TangoWorkshopCounter.increment


# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    """Main function of the TangoWorkshopCounter module."""
    # PROTECTED REGION ID(TangoWorkshopCounter.main) ENABLED START #
    return run((TangoWorkshopCounter,), args=args, **kwargs)
    # PROTECTED REGION END #    //  TangoWorkshopCounter.main


if __name__ == "__main__":
    main()
