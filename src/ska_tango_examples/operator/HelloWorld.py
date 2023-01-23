# -*- coding: utf-8 -*-
#
# This file is part of the HelloWorld project
#
# SKA
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" ska-tango-examples

An HelloWorld device that writes a log message periodically
5 seconds
"""

import logging
import threading
import time

# PyTango imports
import tango
from tango import DebugIt, DevState
from tango.server import Device, command, device_property, run

# Additional import
# PROTECTED REGION ID(HelloWorld.additionnal_import) ENABLED START #

logging.basicConfig(level=logging.DEBUG)
# PROTECTED REGION END #    //  HelloWorld.additionnal_import

__all__ = ["HelloWorld", "main"]


class HelloWorld(Device):
    """
    An HelloWorld device that writes a log message periodically

    **Properties:**

    - Device Property
        message
            - message to log
            - Type:'DevString'
        sleep_time
            - time to sleep between log messages
            - Type:'DevFloat'
    """

    def step_loop(self):
        with tango.EnsureOmniThread():
            while not self.get_state() == tango.DevState.OFF:
                with self._lock:
                    self.logger.info(self.message)

                time.sleep(self.sleep_time)

    def is_Start_allowed(self):
        return self.get_state() == tango.DevState.OFF

    def is_Stop_allowed(self):
        return not self.get_state() == tango.DevState.OFF

    # PROTECTED REGION END #    //  HelloWorld.class_variable

    # -----------------
    # Device Properties
    # -----------------

    message = device_property(dtype="DevString", default_value="Hello World!")

    sleep_time = device_property(dtype="DevFloat", default_value=1)

    # ----------
    # Attributes
    # ----------

    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        """Initialises the attributes and properties of the HelloWorld."""
        Device.init_device(self)
        # PROTECTED REGION ID(HelloWorld.init_device) ENABLED START #
        self.logger = logging.getLogger(__name__)
        self._lock = threading.Lock()
        self.set_state(DevState.OFF)
        self.worker_thread = None
        # PROTECTED REGION END #    //  HelloWorld.init_device

    # ------------------
    # Attributes methods
    # ------------------

    # --------
    # Commands
    # --------

    @command()
    @DebugIt()
    def Start(self):
        # PROTECTED REGION ID(HelloWorld.Start) ENABLED START #
        """
        Set the device state to ON and start execution

        :return:None
        """
        self.set_state(tango.DevState.RUNNING)
        self.logger.info(
            "Started logging '%s' each %.2f seconds",
            self.message,
            self.sleep_time,
        )
        self.worker_thread = threading.Thread(target=self.step_loop)
        self.worker_thread.start()
        # PROTECTED REGION END #    //  HelloWorld.Start

    @command()
    @DebugIt()
    def Stop(self):
        # PROTECTED REGION ID(HelloWorld.Stop) ENABLED START #
        """
        set the device state to OFF and stop the execution

        :return:None
        """
        self.set_state(DevState.OFF)
        self.logger.info("Stopped logging")
        self.worker_thread.join()
        # PROTECTED REGION END #    //  HelloWorld.Stop


# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    """Main function of the HelloWorld module."""
    # PROTECTED REGION ID(HelloWorld.main) ENABLED START #
    return run((HelloWorld,), args=args, **kwargs)
    # PROTECTED REGION END #    //  HelloWorld.main


if __name__ == "__main__":
    main()
