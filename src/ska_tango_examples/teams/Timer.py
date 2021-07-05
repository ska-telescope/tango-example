# pylint: disable=unused-import
# pylint: disable=unnecessary-pass
# -*- coding: utf-8 -*-
#
# This file is part of the Timer project
#
# SKA
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" ska-tango-examples

A Timer countdown device composed by
minutes and seconds.
"""

# PyTango imports
import tango  # noqa: F401
from tango import AttrQuality  # noqa: F401
from tango import DevState  # noqa: F401
from tango import DispLevel  # noqa: F401
from tango import PipeWriteType  # noqa: F401
from tango import AttrWriteType, DebugIt
from tango.server import Device, attribute, command, device_property, run

# Additional import
# PROTECTED REGION ID(Timer.additionnal_import) ENABLED START #
# PROTECTED REGION END #    //  Timer.additionnal_import

__all__ = ["Timer", "main"]


class Timer(Device):
    """
    A Timer countdown device composed by
    minutes and seconds.

    **Properties:**

    - Device Property
        minutesCounter
            - device name for the minutes counter
            - Type:'DevString'
        secondsCounter
            - Device name for the seconds counter
            - Type:'DevString'
        step_loop
            - Sleep time
            - Type:'DevFloat'
    """

    # PROTECTED REGION ID(Timer.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  Timer.class_variable

    # -----------------
    # Device Properties
    # -----------------

    minutesCounter = device_property(
        dtype="DevString", default_value="test/counter/minutes"
    )

    secondsCounter = device_property(
        dtype="DevString", default_value="test/counter/seconds"
    )

    step_loop = device_property(dtype="DevFloat", default_value=1)

    # ----------
    # Attributes
    # ----------

    start_minutes = attribute(
        dtype="DevShort",
        access=AttrWriteType.READ_WRITE,
    )

    start_seconds = attribute(
        dtype="DevShort",
        access=AttrWriteType.READ_WRITE,
    )

    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        """Initialises the attributes and properties of the Timer."""
        Device.init_device(self)
        # PROTECTED REGION ID(Timer.init_device) ENABLED START #
        self._start_minutes = 0
        self._start_seconds = 0
        # PROTECTED REGION END #    //  Timer.init_device

    def always_executed_hook(self):
        """Method always executed before any TANGO command is executed."""
        # PROTECTED REGION ID(Timer.always_executed_hook) ENABLED START #
        # PROTECTED REGION END #    //  Timer.always_executed_hook

    def delete_device(self):
        """Hook to delete resources allocated in init_device.

        This method allows for any memory or other resources allocated in the
        init_device method to be released.  This method is called by the device
        destructor and by the device Init command.
        """
        # PROTECTED REGION ID(Timer.delete_device) ENABLED START #
        # PROTECTED REGION END #    //  Timer.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_start_minutes(self):
        # PROTECTED REGION ID(Timer.start_minutes_read) ENABLED START #
        """Return the start_minutes attribute."""
        return self._start_minutes
        # PROTECTED REGION END #    //  Timer.start_minutes_read

    def write_start_minutes(self, value):
        # PROTECTED REGION ID(Timer.start_minutes_write) ENABLED START #
        """Set the start_minutes attribute."""
        pass  # noqa: W0107
        # PROTECTED REGION END #    //  Timer.start_minutes_write

    def read_start_seconds(self):
        # PROTECTED REGION ID(Timer.start_seconds_read) ENABLED START #
        """Return the start_seconds attribute."""
        return self._start_seconds
        # PROTECTED REGION END #    //  Timer.start_seconds_read

    def write_start_seconds(self, value):
        # PROTECTED REGION ID(Timer.start_seconds_write) ENABLED START #
        """Set the start_seconds attribute."""
        pass  # noqa: W0107
        # PROTECTED REGION END #    //  Timer.start_seconds_write

    # --------
    # Commands
    # --------

    @command()
    @DebugIt()
    def ResetCounters(self):
        # PROTECTED REGION ID(Timer.ResetCounters) ENABLED START #
        """
        Reset the counters minutes and seconds

        :return:None
        """
        pass
        # PROTECTED REGION END #    //  Timer.ResetCounters

    @command()
    @DebugIt()
    def Start(self):
        # PROTECTED REGION ID(Timer.Start) ENABLED START #
        """
        Set the device state to ON and start execution

        :return:None
        """
        pass  # noqa: W0107
        # PROTECTED REGION END #    //  Timer.Start

    @command()
    @DebugIt()
    def Stop(self):
        # PROTECTED REGION ID(Timer.Stop) ENABLED START #
        """
        set the device state to OFF and stop the execution

        :return:None
        """
        pass  # noqa: W0107
        # PROTECTED REGION END #    //  Timer.Stop


# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    """Main function of the Timer module."""
    # PROTECTED REGION ID(Timer.main) ENABLED START #
    return run((Timer,), args=args, **kwargs)
    # PROTECTED REGION END #    //  Timer.main


if __name__ == "__main__":
    main()
