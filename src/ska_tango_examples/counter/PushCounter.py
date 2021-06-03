# -*- coding: utf-8 -*-
# pylint: disable=unnecessary-pass
#
# This file is part of the PushCounter project
#
# SKA
# INAF
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" ska-tango-examples

This class represent a counter that push a change event every time
there`s a change in the value of the counter.
"""

# PyTango imports
from tango import DebugIt
from tango.server import command, run

from ska_tango_examples.counter.Counter import Counter

# Additional import

__all__ = ["PushCounter", "main"]


class PushCounter(Counter):
    """
    This class represent a counter that push a change event every time
    there`s a change in the value of the counter.
    """

    # ----------
    # Attributes
    # ----------

    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        """Initialises the attributes and properties of the PushCounter."""
        Counter.init_device(self)
        # set_change_event	(
        # string	attr_name,
        # bool implemented,
        # bool detect = true
        # )
        # Set an implemented flag for the attribute to indicate that the server
        # fires change events manually, without the polling to be started.
        # If the detect parameter is set to true, the criteria specified for
        # the change event are verified and the event is only pushed if they
        # are fulfilled.
        # If detect is set to false the event is fired without any
        # value checking!
        self.set_change_event("value", True, True)

    def always_executed_hook(self):
        """Method always executed before any TANGO command is executed."""
        pass

    def delete_device(self):
        """Hook to delete resources allocated in init_device.

        This method allows for any memory or other resources allocated in the
        init_device method to be released.  This method is called by the device
        destructor and by the device Init command.
        """
        pass

    # ------------------
    # Attributes methods
    # ------------------

    # --------
    # Commands
    # --------
    @command(
        dtype_out="DevShort",
    )
    @DebugIt()
    def increment(self):
        res = super().increment()
        self.push_change_event("value", res)
        return res

    @command(
        dtype_out="DevShort",
    )
    @DebugIt()
    def decrement(self):
        res = super().decrement()
        self.push_change_event("value", res)
        return res

    @command(
        dtype_in="DevShort",
        dtype_out="DevShort",
    )
    @DebugIt()
    def CounterReset(self, argin):
        res = super().CounterReset(argin)
        self.push_change_event("value", res)
        return res


# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    """Main function of the PushCounter module."""
    return run((PushCounter,), args=args, **kwargs)


if __name__ == "__main__":
    main()
