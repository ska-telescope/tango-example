# -*- coding: utf-8 -*-
#
# This file is part of the ForAttrTabata project
#
# SKA
# INAF
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" ska-tango-examples

Demonstrate the use of the forwarded attribute
"""

# PyTango imports
from tango.server import run
from tango.server import Device
from tango.server import attribute

# Additional import
# PROTECTED REGION ID(ForAttrTabata.additionnal_import) ENABLED START #
# PROTECTED REGION END #    //  ForAttrTabata.additionnal_import

__all__ = ["ForAttrTabata", "main"]


class ForAttrTabata(Device):
    """
    Demonstrate the use of the forwarded attribute
    """

    # PROTECTED REGION ID(ForAttrTabata.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  ForAttrTabata.class_variable

    prepare = attribute(name="prepare", label="prepare", forwarded=True)
    work = attribute(name="work", label="work", forwarded=True)
    rest = attribute(name="rest", label="rest", forwarded=True)
    cycle = attribute(name="cycle", label="cycle", forwarded=True)
    tabata = attribute(name="tabata", label="tabata", forwarded=True)
    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        """Initialises the attributes and properties of the ForAttrTabata."""
        Device.init_device(self)
        # PROTECTED REGION ID(ForAttrTabata.init_device) ENABLED START #
        # PROTECTED REGION END #    //  ForAttrTabata.init_device

    def always_executed_hook(self):
        """Method always executed before any TANGO command is executed."""
        # PROTECTED REGION ID(ForAttrTabata.always_executed_hook) ENABLED START # noqa E501
        # PROTECTED REGION END #    //  ForAttrTabata.always_executed_hook

    def delete_device(self):
        """Hook to delete resources allocated in init_device.

        This method allows for any memory or other resources allocated in the
        init_device method to be released.  This method is called by the device
        destructor and by the device Init command.
        """
        # PROTECTED REGION ID(ForAttrTabata.delete_device) ENABLED START #
        # PROTECTED REGION END #    //  ForAttrTabata.delete_device

    # --------
    # Commands
    # --------


# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    """Main function of the ForAttrTabata module."""
    # PROTECTED REGION ID(ForAttrTabata.main) ENABLED START #
    return run((ForAttrTabata,), args=args, **kwargs)
    # PROTECTED REGION END #    //  ForAttrTabata.main


if __name__ == "__main__":
    main()
