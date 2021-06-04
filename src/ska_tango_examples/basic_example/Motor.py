# -*- coding: utf-8 -*-
#
# This file is part of the Motor project
#
# GPL v3
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" Motor

Motor training example
"""

# PyTango imports
import logging
from tango import DebugIt
from tango.server import run
from tango.server import Device
from tango.server import attribute, command
from tango import DevState

# Additional import
# PROTECTED REGION ID(Motor.additionnal_import) ENABLED START #
import random
from ska_tango_examples.DevFactory import DevFactory

# PyTango imports

# PROTECTED REGION END #    //  Motor.additionnal_import

__all__ = ["Motor", "main"]


class Motor(Device):
    """
    Motor training example
    """

    # PROTECTED REGION ID(Motor.class_variable) ENABLED START #
    def get_dev_factory(self):

        if self._dev_factory is None:
            self._dev_factory = DevFactory()
        return self._dev_factory

    # PROTECTED REGION END #    //  Motor.class_variable

    # ----------
    # Attributes
    # ----------

    PerformanceValue = attribute(
        dtype="DevDouble",
        polling_period=3000,
        rel_change=5,
        abs_change=5,
    )

    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        """Initialises the attributes and properties of the Motor."""
        super().init_device()
        # PROTECTED REGION ID(Motor.init_device) ENABLED START #
        logging.info("set_change_event on PerformanceValue")
        self.set_change_event("PerformanceValue", True, False)
        self._dev_factory = None
        self.powerSupply = None
        # PROTECTED REGION END #    //  Motor.init_device

    def always_executed_hook(self):
        """Method always executed before any TANGO command is executed."""
        # PROTECTED REGION ID(Motor.always_executed_hook) ENABLED START #
        try:
            if self.powerSupply is None:
                logging.info("Connect to power Supply device")
                self.powerSupply = self.get_dev_factory().get_device(
                    "test/powersupply/1"
                )
        except Exception as ex:
            logging.info(
                "Unexpected error on DeviceProxy creation %s", str(ex)
            )
        # PROTECTED REGION END #    //  Motor.always_executed_hook

    def delete_device(self):
        """Hook to delete resources allocated in init_device.

        This method allows for any memory or other resources allocated in the
        init_device method to be released.  This method is called by the device
        destructor and by the device Init command.
        """
        # PROTECTED REGION ID(Motor.delete_device) ENABLED START #
        # PROTECTED REGION END #    //  Motor.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_PerformanceValue(self):
        # PROTECTED REGION ID(Motor.PerformanceValue_read) ENABLED START #
        # import debugpy; debugpy.debug_this_thread()
        return random.uniform(0, 1)
        # PROTECTED REGION END #    //  Motor.PerformanceValue_read

    # --------
    # Commands
    # --------

    @command()
    @DebugIt()
    def TurnOn(self):
        # PROTECTED REGION ID(Motor.TurnOn) ENABLED START #
        try:
            power_state = self.powerSupply.state()
            if power_state != DevState.ON:
                self.powerSupply.turn_on()
        except Exception as ex:
            logging.info("No power state %s", ex)

        self.set_state(DevState.ON)
        # PROTECTED REGION END #    //  Motor.TurnOn

    @command()
    @DebugIt()
    def TurnOff(self):
        # PROTECTED REGION ID(Motor.TurnOff) ENABLED START #
        self.set_state(DevState.OFF)
        logging.info("Motor Off")
        # PROTECTED REGION END #    //  Motor.TurnOff

    @command()
    @DebugIt()
    def Start(self):
        # PROTECTED REGION ID(Motor.Start) ENABLED START #
        self.set_state(DevState.RUNNING)
        logging.info("Motor Running")
        # PROTECTED REGION END #    //  Motor.Start


# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    """Main function of the Motor module."""
    # PROTECTED REGION ID(Motor.main) ENABLED START #
    return run((Motor,), args=args, **kwargs)
    # PROTECTED REGION END #    //  Motor.main


if __name__ == "__main__":
    main()
