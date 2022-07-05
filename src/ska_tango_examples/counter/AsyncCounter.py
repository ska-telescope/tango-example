# -*- coding: utf-8 -*-
# pylint: disable=invalid-overridden-method
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

from tango import GreenMode
from tango.server import Device, run

# PyTango imports
from ska_tango_examples.counter.Counter import Counter

# Additional import
# PROTECTED REGION ID(Counter.additionnal_import) ENABLED START #

# PROTECTED REGION END #    //  Counter.additionnal_import

__all__ = ["AsyncCounter", "main"]


class AsyncCounter(Counter):
    """
    This Device demonstrate the use of the TANGO event mechanism
    to send change events to clients.
    There's also a device attribute in polling so that events
    for that attribute are sent automatically.
    """

    # PROTECTED REGION ID(Counter.class_variable) ENABLED START #
    green_mode = GreenMode.Asyncio
    # PROTECTED REGION END #    //  Counter.class_variable

    # ---------------
    # General methods
    # ---------------

    async def init_device(self):
        """Initialises the attributes and properties of the Counter."""
        await Device.init_device(self)
        # PROTECTED REGION ID(Counter.init_device) ENABLED START #
        self._value = 0
        self._fire_event_at = 0
        self.set_change_event("value", True, False)
        self.set_change_event("polled_value", True, True)
        # PROTECTED REGION END #    //  Counter.init_device


# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    """Main function of the Counter module."""
    # PROTECTED REGION ID(Counter.main) ENABLED START #
    kwargs.setdefault("green_mode", GreenMode.Asyncio)
    return run((AsyncCounter,), args=args, **kwargs)
    # PROTECTED REGION END #    //  Counter.main


if __name__ == "__main__":
    main()
