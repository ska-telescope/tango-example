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

import enum

# PyTango imports
import numpy
import tango
from tango import (
    AttrWriteType,
    DebugIt,
    DevState,
    DispLevel,
)
import logging
from tango.server import Device, attribute, command, run

# Additional import
# PROTECTED REGION ID(Tabata.additionnal_import) ENABLED START #
from ska_tango_examples.tabata.DevFactory import DevFactory

# PROTECTED REGION END #    //  Tabata.additionnal_import

__all__ = ["Tabata", "main"]


class Running_state(enum.IntEnum):
    """Python enumerated type for Running_state attribute."""

    PREPARE = 0
    WORK = 1
    REST = 2


class Tabata(Device):
    """
    Tabata training
    """

    # PROTECTED REGION ID(Tabata.class_variable) ENABLED START #
    subscribed = False

    def get_dev_factory(self):
        if self._dev_factory is None:
            self._dev_factory = DevFactory()
        return self._dev_factory

    def event_subscription(self):
        self.get_dev_factory().get_prepare_counter().subscribe_event(
            "value",
            tango.EventType.CHANGE_EVENT,
            self.handle_event,
            stateless=True,
        )
        self.get_dev_factory().get_work_counter().subscribe_event(
            "value",
            tango.EventType.CHANGE_EVENT,
            self.handle_event,
            stateless=True,
        )
        self.get_dev_factory().get_rest_counter().subscribe_event(
            "value",
            tango.EventType.CHANGE_EVENT,
            self.handle_event,
            stateless=True,
        )
        self.get_dev_factory().get_cycles_counter().subscribe_event(
            "value",
            tango.EventType.CHANGE_EVENT,
            self.handle_event,
            stateless=True,
        )
        self.get_dev_factory().get_tabatas_counter().subscribe_event(
            "value",
            tango.EventType.CHANGE_EVENT,
            self.handle_event,
            stateless=True,
        )

    def handle_event(self, args):
        if args.attr_value == 0:
            if "prepare" in args.device.dev_name:
                args.device.Reset(self._prepare)
                self._runnint_state = Running_state.WORK
            if "work" in args.device.dev_name:
                args.device.Reset(self._work)
                self._runnint_state = Running_state.REST
                self.get_dev_factory().get_cycles_counter().decrement()
            if "rest" in args.device.dev_name:
                args.device.Reset(self._rest)
                self._runnint_state = Running_state.WORK
            if "cycles" in args.device.dev_name:
                args.device.Reset(self._cycles)
                self.get_dev_factory().get_tabatas_counter().decrement()
            if "tabatas" in args.device.dev_name:
                self.Stop()
                self.ResetCounters()

    # PROTECTED REGION END #    //  Tabata.class_variable

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
        dtype=Running_state,
    )

    counter_values = attribute(
        dtype=("DevUShort",),
        max_dim_x=5,
    )

    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        """Initialises the attributes and properties of the Tabata."""
        Device.init_device(self)
        # PROTECTED REGION ID(Tabata.init_device) ENABLED START #
        self._prepare = 10
        self._work = 20
        self._rest = 10
        self._cycles = 8
        self._tabatas = 1
        import debugpy; debugpy.debug_this_thread()
        self._runnint_state = Running_state.PREPARE
        self.set_state(DevState.OFF)
        self._dev_factory = None
        # PROTECTED REGION END #    //  Tabata.init_device

    def always_executed_hook(self):
        """Method always executed before any TANGO command is executed."""
        # PROTECTED REGION ID(Tabata.always_executed_hook) ENABLED START #
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
        if value < 20:
            raise Exception("work must be at least of 20 seconds!")
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
        if value > 20:
            raise Exception("rest must be maximum 20 seconds!")
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
        if value < 8:
            raise Exception("tabata must be at least of 8 cycles!")
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
            raise Exception("you cannot train in less of a tabata!")
        self._tabatas = value
        # PROTECTED REGION END #    //  Tabata.tabatas_write

    def read_running_state(self):
        # PROTECTED REGION ID(Tabata.running_state_read) ENABLED START #
        """Return the running_state attribute."""
        import debugpy; debugpy.debug_this_thread()
        return self._running_state
        # PROTECTED REGION END #    //  Tabata.running_state_read

    def read_counter_values(self):
        # PROTECTED REGION ID(Tabata.counter_values_read) ENABLED START #
        """Return the counter_values attribute."""
        return numpy.ndarray(
            [
                self.get_dev_factory().get_prepare_counter().value,
                self.get_dev_factory().get_work_counter().value,
                self.get_dev_factory().get_rest_counter().value,
                self.get_dev_factory().get_cycles_counter().value,
                self.get_dev_factory().get_tabatas_counter().value,
            ]
        )

        # PROTECTED REGION END #    //  Tabata.counter_values_read

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
        if not self.subscribed:
            self.event_subscription()
            self.subscribed = True
            self.ResetCounters()
        if not self.get_state() == DevState.ON:
            self.set_state(DevState.ON)
        # PROTECTED REGION END #    //  Tabata.Start

    @command()
    @DebugIt()
    def Stop(self):
        # PROTECTED REGION ID(Tabata.Stop) ENABLED START #
        """

        :return:None
        """
        if not self.get_state() == DevState.OFF:
            self.set_state(DevState.OFF)
        # PROTECTED REGION END #    //  Tabata.Stop

    @command(
        display_level=DispLevel.EXPERT,
        polling_period=1000,
    )
    @DebugIt()
    def Step(self):
        # PROTECTED REGION ID(Tabata.Step) ENABLED START #
        """

        :return:None
        """
        import debugpy; debugpy.debug_this_thread()
        if self.get_state() == DevState.ON:
            if self.running_state == Running_state.PREPARE:
                logging.info("get_prepare_counter().decrement")
                self.get_dev_factory().get_prepare_counter().decrement()
            if self.running_state == Running_state.WORK:
                logging.info("get_work_counter().decrement")
                self.get_dev_factory().get_work_counter().decrement()
            if self.running_state == Running_state.REST:
                logging.info("get_dev_factory().decrement")
                self.get_dev_factory().get_rest_counter().decrement()

        # PROTECTED REGION END #    //  Tabata.Step

    @command()
    @DebugIt()
    def ResetCounters(self):
        # PROTECTED REGION ID(Tabata.ResetCounters) ENABLED START #
        """

        :return:None
        """
        self.get_dev_factory().get_prepare_counter().CounterReset(
            self._prepare
        )
        self.get_dev_factory().get_work_counter().CounterReset(self._work)
        self.get_dev_factory().get_rest_counter().CounterReset(self._rest)
        self.get_dev_factory().get_cycles_counter().CounterReset(self._cycles)
        self.get_dev_factory().get_tabatas_counter().CounterReset(
            self._tabatas
        )
        # PROTECTED REGION END #    //  Tabata.ResetCounters


# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    """Main function of the Tabata module."""
    # PROTECTED REGION ID(Tabata.main) ENABLED START #
    return run((Tabata,), args=args, **kwargs)
    # PROTECTED REGION END #    //  Tabata.main


if __name__ == "__main__":
    main()
