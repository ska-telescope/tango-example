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
import debugpy
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
        debugpy.debug_this_thread()
        if args.device.value <= 0:
            logging.debug(
                "HANDLE EVENT %s %s", args.device.dev_name(), args.device.value
            )
            if (
                args.device.dev_name()
                == self.get_dev_factory().get_prepare_counter().dev_name()
            ):
                logging.debug("PREPARE -> WORK")
                args.device.CounterReset(self._prepare)
                self._running_state = Running_state.WORK
            if (
                args.device.dev_name()
                == self.get_dev_factory().get_work_counter().dev_name()
            ):
                logging.debug("WORK -> REST")
                args.device.CounterReset(self._work)
                self._running_state = Running_state.REST
                self.get_dev_factory().get_cycles_counter().decrement()
            if (
                args.device.dev_name()
                == self.get_dev_factory().get_rest_counter().dev_name()
            ):
                logging.debug("REST -> WORK")
                args.device.CounterReset(self._rest)
                self._running_state = Running_state.WORK
            if (
                args.device.dev_name()
                == self.get_dev_factory().get_cycles_counter().dev_name()
            ):
                logging.debug("TABATA DONE")
                args.device.CounterReset(self._cycles)
                self.get_dev_factory().get_tabatas_counter().decrement()
            if (
                args.device.dev_name()
                == self.get_dev_factory().get_tabatas_counter().dev_name()
            ):
                logging.debug("WORKOUT DONE")
                self.Stop()

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
        self._running_state = Running_state.PREPARE
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
        if value < 0:
            raise Exception("only positive value!")
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
        if value < 0:
            raise Exception("only positive value!")
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
        if value < 0:
            raise Exception("only positive value!")
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
        if value < 0:
            raise Exception("only positive value!")
        self._tabatas = value
        # PROTECTED REGION END #    //  Tabata.tabatas_write

    def read_running_state(self):
        # PROTECTED REGION ID(Tabata.running_state_read) ENABLED START #
        """Return the running_state attribute."""
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
        debugpy.debug_this_thread()
        if self.get_state() == DevState.ON:
            if self.read_running_state() == Running_state.PREPARE:
                device = self.get_dev_factory().get_prepare_counter()
                logging.debug("PREPARE %s", device.value)
                device.decrement()
            if self.read_running_state() == Running_state.WORK:
                device = self.get_dev_factory().get_work_counter()
                logging.debug("WORK %s", device.value)
                device.decrement()
            if self.read_running_state() == Running_state.REST:
                device = self.get_dev_factory().get_rest_counter()
                logging.debug("REST %s", device.value)
                device.decrement()

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
