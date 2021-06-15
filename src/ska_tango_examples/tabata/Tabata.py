# -*- coding: utf-8 -*-
#
# This file is part of the Tabata project
#
# SKA
# INAF
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" ska-tango-examples

Tabata training
"""

# PyTango imports
import tango
from tango import DebugIt
from tango.server import run
from tango.server import Device
from tango.server import attribute, command
from tango.server import device_property
from tango import DevState
from tango import AttrWriteType

# Additional import
# PROTECTED REGION ID(Tabata.additionnal_import) ENABLED START #
from ska_tango_examples.DevFactory import DevFactory
import logging
import time
import debugpy
import threading
from ska_tango_examples.tabata.RunningState import RunningState

logging.basicConfig(level=logging.DEBUG)
# PROTECTED REGION END #    //  Tabata.additionnal_import

__all__ = ["Tabata", "main"]


class Tabata(Device):
    """
    Tabata training

    This class demonstrate how to create an device in TANGO
    with default synchronization.
    When the command Start is called, a specific thread will
    work so that commands are free to be called.

    **Properties:**

    - Device Property
        prepCounter
            - Type:'DevString'
        workCounter
            - Type:'DevString'
        restCounter
            - Type:'DevString'
        cycleCounter
            - Type:'DevString'
        tabatasCounter
            - Type:'DevString'
        sleep_time
            - Type:'DevFloat'
    """

    # PROTECTED REGION ID(Tabata.class_variable) ENABLED START #
    def event_subscription(self):
        self._dev_factory.get_device(self.prepCounter).subscribe_event(
            "value",
            tango.EventType.CHANGE_EVENT,
            self.handle_event,
            stateless=True,
        )
        self._dev_factory.get_device(self.workCounter).subscribe_event(
            "value",
            tango.EventType.CHANGE_EVENT,
            self.handle_event,
            stateless=True,
        )
        self._dev_factory.get_device(self.restCounter).subscribe_event(
            "value",
            tango.EventType.CHANGE_EVENT,
            self.handle_event,
            stateless=True,
        )
        self._dev_factory.get_device(self.cycleCounter).subscribe_event(
            "value",
            tango.EventType.CHANGE_EVENT,
            self.handle_event,
            stateless=True,
        )
        self._dev_factory.get_device(self.tabatasCounter).subscribe_event(
            "value",
            tango.EventType.CHANGE_EVENT,
            self.handle_event,
            stateless=True,
        )

    def step_loop(self):
        with tango.EnsureOmniThread():
            while self.get_state() == DevState.ON:
                with self._lock:
                    if self.read_running_state() == RunningState.PREPARE:
                        device = self._dev_factory.get_device(self.prepCounter)
                        self.logger.debug("PREPARE %s", device.value)
                        device.decrement()
                    if self.read_running_state() == RunningState.WORK:
                        device = self._dev_factory.get_device(self.workCounter)
                        self.logger.debug("WORK %s", device.value)
                        device.decrement()
                    if self.read_running_state() == RunningState.REST:
                        device = self._dev_factory.get_device(self.restCounter)
                        self.logger.debug("REST %s", device.value)
                        device.decrement()

                time.sleep(self.sleep_time)

    def handle_event(self, evt):
        if evt.err:
            error = evt.errors[0]
            self.logger.error("%s %s", error.reason, error.desc)
            return

        if evt.device.value <= 0 and self.get_state() == DevState.ON:
            self.logger.debug(
                "HANDLE EVENT %s %s", evt.device.dev_name(), evt.device.value
            )
            if evt.device.dev_name() == self.prepCounter:
                with self._lock:
                    evt.device.CounterReset(self._prepare)
                    self._running_state = RunningState.WORK
                self.logger.debug("PREPARE -> WORK")

            if evt.device.dev_name() == self.workCounter:
                with self._lock:
                    evt.device.CounterReset(self._work)
                    self._running_state = RunningState.REST
                self.logger.debug("WORK -> REST")

            if evt.device.dev_name() == self.restCounter:
                with self._lock:
                    evt.device.CounterReset(self._rest)
                    self._running_state = RunningState.WORK
                    self._dev_factory.get_device(self.cycleCounter).decrement()
                self.logger.debug("REST -> WORK")

            if evt.device.dev_name() == self.cycleCounter:
                with self._lock:
                    evt.device.CounterReset(self._cycles)
                    self._dev_factory.get_device(
                        self.tabatasCounter
                    ).decrement()
                self.logger.debug("TABATA DONE")

            if evt.device.dev_name() == self.tabatasCounter:
                with self._lock:
                    self._running_state = RunningState.PREPARE
                    self.set_state(DevState.OFF)
                self.logger.debug("WORKOUT DONE")

    def internal_reset_counters(self):
        with self._lock:
            self._dev_factory.get_device(self.prepCounter).CounterReset(
                self._prepare
            )
            self._dev_factory.get_device(self.workCounter).CounterReset(
                self._work
            )
            self._dev_factory.get_device(self.restCounter).CounterReset(
                self._rest
            )
            self._dev_factory.get_device(self.cycleCounter).CounterReset(
                self._cycles
            )
            self._dev_factory.get_device(self.tabatasCounter).CounterReset(
                self._tabatas
            )

    def is_Start_allowed(self):
        return self.get_state() == tango.DevState.OFF

    def is_Stop_allowed(self):
        return self.get_state() == tango.DevState.ON

    def is_ResetCounters_allowed(self):
        return self.get_state() == tango.DevState.OFF

    # PROTECTED REGION END #    //  Tabata.class_variable

    # -----------------
    # Device Properties
    # -----------------

    prepCounter = device_property(
        dtype="DevString", default_value="test/counter/prepare"
    )

    workCounter = device_property(
        dtype="DevString", default_value="test/counter/work"
    )

    restCounter = device_property(
        dtype="DevString", default_value="test/counter/rest"
    )

    cycleCounter = device_property(
        dtype="DevString", default_value="test/counter/cycles"
    )

    tabatasCounter = device_property(
        dtype="DevString", default_value="test/counter/tabatas"
    )

    sleep_time = device_property(dtype="DevFloat", default_value=1)

    # ----------
    # Attributes
    # ----------

    prepare = attribute(
        dtype="DevUShort",
        access=AttrWriteType.READ_WRITE,
    )

    work = attribute(
        dtype="DevUShort",
        access=AttrWriteType.READ_WRITE,
    )

    rest = attribute(
        dtype="DevUShort",
        access=AttrWriteType.READ_WRITE,
    )

    cycles = attribute(
        dtype="DevUShort",
        access=AttrWriteType.READ_WRITE,
    )

    tabatas = attribute(
        dtype="DevUShort",
        access=AttrWriteType.READ_WRITE,
    )

    running_state = attribute(
        dtype=RunningState,
    )

    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        """Initialises the attributes and properties of the Tabata."""
        Device.init_device(self)
        # PROTECTED REGION ID(Tabata.init_device) ENABLED START #
        self.logger = logging.getLogger(__name__)
        self._lock = threading.Lock()
        self._dev_factory = DevFactory()
        self._prepare = 10
        self._work = 20
        self._rest = 10
        self._cycles = 8
        self._tabatas = 1
        self._running_state = RunningState.PREPARE
        self.subscribed = False
        self.set_state(DevState.OFF)
        self.worker_thread = None
        # PROTECTED REGION END #    //  Tabata.init_device

    def always_executed_hook(self):
        """Method always executed before any TANGO command is executed."""
        # PROTECTED REGION ID(Tabata.always_executed_hook) ENABLED START #
        if not self.subscribed:
            self.event_subscription()
            self.subscribed = True
            self.internal_reset_counters()
        # PROTECTED REGION END #    //  Tabata.always_executed_hook

    def delete_device(self):
        """Hook to delete resources allocated in init_device.

        This method allows for any memory or other resources allocated in the
        init_device method to be released.  This method is called by the device
        destructor and by the device Init command.
        """
        # PROTECTED REGION ID(Tabata.delete_device) ENABLED START #
        # PROTECTED REGION END #    //  Tabata.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_prepare(self):
        # PROTECTED REGION ID(Tabata.prepare_read) ENABLED START #
        """Return the prepare attribute."""
        return self._prepare
        # PROTECTED REGION END #    //  Tabata.prepare_read

    def write_prepare(self, value):
        # PROTECTED REGION ID(Tabata.prepare_write) ENABLED START #
        """Set the prepare attribute."""
        if value < 0:
            raise Exception("only positive value!")

        if self.get_state() == DevState.ON:
            raise Exception("cannot change values when device is running!")

        self._prepare = value
        # PROTECTED REGION END #    //  Tabata.prepare_write

    def read_work(self):
        # PROTECTED REGION ID(Tabata.work_read) ENABLED START #
        """Return the work attribute."""
        return self._work
        # PROTECTED REGION END #    //  Tabata.work_read

    def write_work(self, value):
        # PROTECTED REGION ID(Tabata.work_write) ENABLED START #
        """Set the work attribute."""
        if value < 1:
            raise Exception("only positive value!")

        if self.get_state() == DevState.ON:
            raise Exception("cannot change values when device is running!")

        self._work = value
        # PROTECTED REGION END #    //  Tabata.work_write

    def read_rest(self):
        # PROTECTED REGION ID(Tabata.rest_read) ENABLED START #
        """Return the rest attribute."""
        return self._rest
        # PROTECTED REGION END #    //  Tabata.rest_read

    def write_rest(self, value):
        # PROTECTED REGION ID(Tabata.rest_write) ENABLED START #
        """Set the rest attribute."""
        if value < 1:
            raise Exception("only positive value!")

        if self.get_state() == DevState.ON:
            raise Exception("cannot change values when device is running!")

        self._rest = value
        # PROTECTED REGION END #    //  Tabata.rest_write

    def read_cycles(self):
        # PROTECTED REGION ID(Tabata.cycles_read) ENABLED START #
        """Return the cycles attribute."""
        return self._cycles
        # PROTECTED REGION END #    //  Tabata.cycles_read

    def write_cycles(self, value):
        # PROTECTED REGION ID(Tabata.cycles_write) ENABLED START #
        """Set the cycles attribute."""
        if value < 1:
            raise Exception("only positive value!")

        if self.get_state() == DevState.ON:
            raise Exception("cannot change values when device is running!")

        self._cycles = value
        # PROTECTED REGION END #    //  Tabata.cycles_write

    def read_tabatas(self):
        # PROTECTED REGION ID(Tabata.tabatas_read) ENABLED START #
        """Return the tabatas attribute."""
        return self._tabatas
        # PROTECTED REGION END #    //  Tabata.tabatas_read

    def write_tabatas(self, value):
        # PROTECTED REGION ID(Tabata.tabatas_write) ENABLED START #
        """Set the tabatas attribute."""
        if value < 1:
            raise Exception("only positive value!")

        if self.get_state() == DevState.ON:
            raise Exception("cannot change values when device is running!")

        self._tabatas = value
        # PROTECTED REGION END #    //  Tabata.tabatas_write

    def read_running_state(self):
        # PROTECTED REGION ID(Tabata.running_state_read) ENABLED START #
        """Return the running_state attribute."""
        return self._running_state
        # PROTECTED REGION END #    //  Tabata.running_state_read

    # --------
    # Commands
    # --------

    @command()
    @DebugIt()
    def Start(self):
        # PROTECTED REGION ID(Tabata.Start) ENABLED START #
        """

        :return:None
        """
        self.set_state(DevState.ON)
        self.worker_thread = threading.Thread(target=self.step_loop)
        self.worker_thread.start()
        # PROTECTED REGION END #    //  Tabata.Start

    @command()
    @DebugIt()
    def Stop(self):
        # PROTECTED REGION ID(Tabata.Stop) ENABLED START #
        """

        :return:None
        """
        self.set_state(DevState.OFF)
        self.worker_thread.join()
        # PROTECTED REGION END #    //  Tabata.Stop

    @command()
    @DebugIt()
    def ResetCounters(self):
        # PROTECTED REGION ID(Tabata.ResetCounters) ENABLED START #
        """

        :return:None
        """
        self.internal_reset_counters()

        # PROTECTED REGION END #    //  Tabata.ResetCounters


# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    """Main function of the Tabata module."""
    # PROTECTED REGION ID(Tabata.main) ENABLED START #
    debugpy.listen(5678)
    return run((Tabata,), args=args, **kwargs)
    # PROTECTED REGION END #    //  Tabata.main


if __name__ == "__main__":
    main()
