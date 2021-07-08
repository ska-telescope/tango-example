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

import logging
import threading
import time

# PyTango imports
import tango
from tango import AttrWriteType, DebugIt, DevState
from tango.server import Device, attribute, command, device_property, run

from ska_tango_examples.DevFactory import DevFactory

# Additional import
# PROTECTED REGION ID(Timer.additionnal_import) ENABLED START #

logging.basicConfig(level=logging.DEBUG)
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
        sleep_time
            - Sleep time
            - Type:'DevFloat'
    """

    # PROTECTED REGION ID(Timer.class_variable) ENABLED START #
    def event_subscription(self):
        self._dev_factory.get_device(self.secondsCounter).subscribe_event(
            "value",
            tango.EventType.CHANGE_EVENT,
            self.handle_event,
            stateless=True,
        )
        self._dev_factory.get_device(self.minutesCounter).subscribe_event(
            "value",
            tango.EventType.CHANGE_EVENT,
            self.handle_event,
            stateless=True,
        )

    def internal_reset_counters(self):
        with self._lock:
            self._dev_factory.get_device(self.minutesCounter).CounterReset(
                self._start_minutes
            )
            self._dev_factory.get_device(self.secondsCounter).CounterReset(
                self._start_seconds
            )

    def step_loop(self):
        with tango.EnsureOmniThread():
            while not self.get_state() == tango.DevState.OFF:
                with self._lock:
                    device = self._dev_factory.get_device(self.secondsCounter)
                    self.logger.debug("SECONDS %s", device.value)
                    device.decrement()

                time.sleep(self.sleep_time)

    def handle_event(self, evt):
        if evt.err:
            error = evt.errors[0]
            self.logger.error("%s %s", error.reason, error.desc)
            return

        if evt.device.value <= 0 and (
            not self.get_state() == tango.DevState.OFF
        ):
            self.logger.debug(
                "HANDLE EVENT %s %s", evt.device.dev_name(), evt.device.value
            )

            if evt.device.dev_name() == self.secondsCounter:
                if self.get_state() == DevState.ALARM:
                    with self._lock:
                        self.set_state(DevState.OFF)
                else:
                    with self._lock:
                        self._dev_factory.get_device(
                            self.secondsCounter
                        ).CounterReset(59)
                    device = self._dev_factory.get_device(self.minutesCounter)
                    with self._lock:
                        device.decrement()
                    self.logger.debug("MINUTES %s", device.value)
            else:
                with self._lock:
                    self.set_state(DevState.ALARM)

    def is_Start_allowed(self):
        return self.get_state() == tango.DevState.OFF

    def is_Stop_allowed(self):
        return not self.get_state() == tango.DevState.OFF

    def is_ResetCounters_allowed(self):
        return self.get_state() == tango.DevState.OFF

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

    sleep_time = device_property(dtype="DevFloat", default_value=1)

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
        self.logger = logging.getLogger(__name__)
        self._lock = threading.Lock()
        self._dev_factory = DevFactory()
        self._start_minutes = 0
        self._start_seconds = 0
        self.subscribed = False
        self.set_state(DevState.OFF)
        self.worker_thread = None
        # PROTECTED REGION END #    //  Timer.init_device

    def always_executed_hook(self):
        """Method always executed before any TANGO command is executed."""
        # PROTECTED REGION ID(Timer.always_executed_hook) ENABLED START #
        if not self.subscribed:
            self.event_subscription()
            self.subscribed = True
            self.internal_reset_counters()
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
        if value < 1:
            raise Exception("only positive values!")

        self._start_minutes = value
        # PROTECTED REGION END #    //  Timer.start_minutes_write

    def read_start_seconds(self):
        # PROTECTED REGION ID(Timer.start_seconds_read) ENABLED START #
        """Return the start_seconds attribute."""
        return self._start_seconds
        # PROTECTED REGION END #    //  Timer.start_seconds_read

    def write_start_seconds(self, value):
        # PROTECTED REGION ID(Timer.start_seconds_write) ENABLED START #
        """Set the start_seconds attribute."""
        if value < 1:
            raise Exception("only positive values!")

        self._start_seconds = value
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
        self.internal_reset_counters()
        # PROTECTED REGION END #    //  Timer.ResetCounters

    @command()
    @DebugIt()
    def Start(self):
        # PROTECTED REGION ID(Timer.Start) ENABLED START #
        """
        Set the device state to ON and start execution

        :return:None
        """
        self.set_state(tango.DevState.RUNNING)
        self.worker_thread = threading.Thread(target=self.step_loop)
        self.worker_thread.start()
        # PROTECTED REGION END #    //  Timer.Start

    @command()
    @DebugIt()
    def Stop(self):
        # PROTECTED REGION ID(Timer.Stop) ENABLED START #
        """
        set the device state to OFF and stop the execution

        :return:None
        """
        self.set_state(DevState.OFF)
        self.worker_thread.join()
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
