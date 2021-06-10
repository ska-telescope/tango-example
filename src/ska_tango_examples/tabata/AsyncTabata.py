# -*- coding: utf-8 -*-
#
# This file is part of the AsyncTabata project
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
import threading
import tango
from tango import DebugIt
from tango.server import run
from tango.server import Device
from tango.server import attribute, command
from tango.server import device_property
from tango import GreenMode, DevState
from tango import AttrWriteType
import enum

# Additional import
# PROTECTED REGION ID(AsyncTabata.additionnal_import) ENABLED START #
from ska_tango_examples.DevFactory import DevFactory
import logging
import debugpy
import asyncio

logging.basicConfig(level=logging.DEBUG)
# PROTECTED REGION END #    //  AsyncTabata.additionnal_import

__all__ = ["AsyncTabata", "main"]


class Running_state(enum.IntEnum):
    """Python enumerated type for Running_state attribute."""

    PREPARE = 0
    WORK = 1
    REST = 2


class AsyncTabata(Device):
    """
    Tabata training

    This class demonstrate how to create an async device in TANGO
    with synchronization (lock) effort to protect the device

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
    """

    # PROTECTED REGION ID(AsyncTabata.class_variable) ENABLED START #
    green_mode = GreenMode.Asyncio

    def event_subscription(self):
        DevFactory().get_dev_from_property(
            self, "prepCounter"
        ).subscribe_event(
            "value",
            tango.EventType.CHANGE_EVENT,
            self.handle_event,
            stateless=True,
        )
        DevFactory().get_dev_from_property(
            self, "workCounter"
        ).subscribe_event(
            "value",
            tango.EventType.CHANGE_EVENT,
            self.handle_event,
            stateless=True,
        )
        DevFactory().get_dev_from_property(
            self, "restCounter"
        ).subscribe_event(
            "value",
            tango.EventType.CHANGE_EVENT,
            self.handle_event,
            stateless=True,
        )
        DevFactory().get_dev_from_property(
            self, "cycleCounter"
        ).subscribe_event(
            "value",
            tango.EventType.CHANGE_EVENT,
            self.handle_event,
            stateless=True,
        )
        DevFactory().get_dev_from_property(
            self, "tabatasCounter"
        ).subscribe_event(
            "value",
            tango.EventType.CHANGE_EVENT,
            self.handle_event,
            stateless=True,
        )

    def handle_event(self, args):
        if args.device.value <= 0 and self.get_state() == DevState.ON:
            logging.debug(
                "HANDLE EVENT %s %s", args.device.dev_name(), args.device.value
            )
            if (
                args.device.dev_name()
                == DevFactory()
                .get_dev_from_property(self, "prepCounter")
                .dev_name()
            ):
                logging.debug("PREPARE -> WORK")
                args.device.CounterReset(self._prepare)
                self._running_state = Running_state.WORK
            if (
                args.device.dev_name()
                == DevFactory()
                .get_dev_from_property(self, "workCounter")
                .dev_name()
            ):
                logging.debug("WORK -> REST")
                args.device.CounterReset(self._work)
                self._running_state = Running_state.REST
            if (
                args.device.dev_name()
                == DevFactory()
                .get_dev_from_property(self, "restCounter")
                .dev_name()
            ):
                logging.debug("REST -> WORK")
                args.device.CounterReset(self._rest)
                self._running_state = Running_state.WORK
                DevFactory().get_dev_from_property(
                    self, "cycleCounter"
                ).decrement()
            if (
                args.device.dev_name()
                == DevFactory()
                .get_dev_from_property(self, "cycleCounter")
                .dev_name()
            ):
                logging.debug("TABATA DONE")
                args.device.CounterReset(self._cycles)
                DevFactory().get_dev_from_property(
                    self, "tabatasCounter"
                ).decrement()
            if (
                args.device.dev_name()
                == DevFactory()
                .get_dev_from_property(self, "tabatasCounter")
                .dev_name()
            ):
                logging.debug("WORKOUT DONE")
                with self._lock:
                    self.set_state(DevState.OFF)
                    self._running_state = Running_state.PREPARE
                logging.debug("State set at %s", self.get_state())

    async def internal_run(self):
        while self.get_state() == DevState.ON:
            logging.debug("step")
            run_state = await self.read_running_state()
            if run_state == Running_state.PREPARE:
                device = DevFactory().get_dev_from_property(
                    self, "prepCounter"
                )
                logging.debug("PREPARE %s", device.value)
                device.decrement()
            if run_state == Running_state.WORK:
                device = DevFactory().get_dev_from_property(
                    self, "workCounter"
                )
                logging.debug("WORK %s", device.value)
                device.decrement()
            if run_state == Running_state.REST:
                device = DevFactory().get_dev_from_property(
                    self, "restCounter"
                )
                logging.debug("REST %s", device.value)
                device.decrement()
            await asyncio.sleep(1)
            # time.sleep(1)

    # PROTECTED REGION END #    //  AsyncTabata.class_variable

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

    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        """Initialises the attributes and properties of the AsyncTabata."""
        Device.init_device(self)
        # PROTECTED REGION ID(AsyncTabata.init_device) ENABLED START #
        self._prepare = 10
        self._work = 20
        self._rest = 10
        self._cycles = 8
        self._tabatas = 1
        self._running_state = Running_state.PREPARE
        self.subscribed = False
        self.set_state(DevState.OFF)
        # The below commands are not really needed
        # since in GreenMode.Asyncio mode the monitor
        # lock is disabled by default. I put it here so
        # that it is clear what is happening
        util = tango.Util.instance()
        util.set_serial_model(tango.SerialModel.NO_SYNC)
        self._lock = threading.Lock()
        # PROTECTED REGION END #    //  AsyncTabata.init_device

    def always_executed_hook(self):
        """Method always executed before any TANGO command is executed."""
        # PROTECTED REGION ID(AsyncTabata.always_executed_hook) ENABLED START #
        if not self.subscribed:
            self.event_subscription()
            self.subscribed = True
            self.ResetCounters()
        # PROTECTED REGION END #    //  AsyncTabata.always_executed_hook

    def delete_device(self):
        """Hook to delete resources allocated in init_device.

        This method allows for any memory or other resources allocated in the
        init_device method to be released.  This method is called by the device
        destructor and by the device Init command.
        """
        # PROTECTED REGION ID(AsyncTabata.delete_device) ENABLED START #
        # PROTECTED REGION END #    //  AsyncTabata.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_prepare(self):
        # PROTECTED REGION ID(AsyncTabata.prepare_read) ENABLED START #
        """Return the prepare attribute."""
        return self._prepare
        # PROTECTED REGION END #    //  AsyncTabata.prepare_read

    def write_prepare(self, value):
        # PROTECTED REGION ID(AsyncTabata.prepare_write) ENABLED START #
        """Set the prepare attribute."""
        if value < 0:
            raise Exception("only positive value!")

        if self.get_state() == DevState.ON:
            raise Exception("cannot change values when device is running!")

        with self._lock:
            self._prepare = value
        # PROTECTED REGION END #    //  AsyncTabata.prepare_write

    def read_work(self):
        # PROTECTED REGION ID(AsyncTabata.work_read) ENABLED START #
        """Return the work attribute."""
        return self._work
        # PROTECTED REGION END #    //  AsyncTabata.work_read

    def write_work(self, value):
        # PROTECTED REGION ID(AsyncTabata.work_write) ENABLED START #
        """Set the work attribute."""
        if value < 0:
            raise Exception("only positive value!")

        if self.get_state() == DevState.ON:
            raise Exception("cannot change values when device is running!")

        with self._lock:
            self._work = value
        # PROTECTED REGION END #    //  AsyncTabata.work_write

    def read_rest(self):
        # PROTECTED REGION ID(AsyncTabata.rest_read) ENABLED START #
        """Return the rest attribute."""
        return self._rest
        # PROTECTED REGION END #    //  AsyncTabata.rest_read

    def write_rest(self, value):
        # PROTECTED REGION ID(AsyncTabata.rest_write) ENABLED START #
        """Set the rest attribute."""
        if value < 0:
            raise Exception("only positive value!")

        if self.get_state() == DevState.ON:
            raise Exception("cannot change values when device is running!")

        with self._lock:
            self._rest = value
        # PROTECTED REGION END #    //  AsyncTabata.rest_write

    def read_cycles(self):
        # PROTECTED REGION ID(AsyncTabata.cycles_read) ENABLED START #
        """Return the cycles attribute."""
        return self._cycles
        # PROTECTED REGION END #    //  AsyncTabata.cycles_read

    def write_cycles(self, value):
        # PROTECTED REGION ID(AsyncTabata.cycles_write) ENABLED START #
        """Set the cycles attribute."""
        if value < 0:
            raise Exception("only positive value!")

        if self.get_state() == DevState.ON:
            raise Exception("cannot change values when device is running!")

        with self._lock:
            self._cycles = value
        # PROTECTED REGION END #    //  AsyncTabata.cycles_write

    def read_tabatas(self):
        # PROTECTED REGION ID(AsyncTabata.tabatas_read) ENABLED START #
        """Return the tabatas attribute."""
        return self._tabatas
        # PROTECTED REGION END #    //  AsyncTabata.tabatas_read

    def write_tabatas(self, value):
        # PROTECTED REGION ID(AsyncTabata.tabatas_write) ENABLED START #
        """Set the tabatas attribute."""
        if value < 0:
            raise Exception("only positive value!")

        if self.get_state() == DevState.ON:
            raise Exception("cannot change values when device is running!")

        with self._lock:
            self._tabatas = value
        # PROTECTED REGION END #    //  AsyncTabata.tabatas_write

    async def read_running_state(self):
        # PROTECTED REGION ID(AsyncTabata.running_state_read) ENABLED START #
        """Return the running_state attribute."""
        return self._running_state
        # PROTECTED REGION END #    //  AsyncTabata.running_state_read

    # --------
    # Commands
    # --------

    @command()
    @DebugIt()
    async def Run(self):
        # PROTECTED REGION ID(AsyncTabata.Run) ENABLED START #
        """

        :return:None
        """
        with self._lock:
            if self.get_state() == DevState.ON:
                return
            self.set_state(DevState.ON)

        await self.internal_run()
        # loop = asyncio.get_event_loop()
        # loop.create_task(self.internal_run())
        # PROTECTED REGION END #    //  AsyncTabata.Run

    @command()
    @DebugIt()
    def Stop(self):
        # PROTECTED REGION ID(AsyncTabata.Stop) ENABLED START #
        """

        :return:None
        """
        with self._lock:
            if self.get_state() == DevState.OFF:
                return
            self.set_state(DevState.OFF)
        # PROTECTED REGION END #    //  AsyncTabata.Stop

    @command()
    @DebugIt()
    def ResetCounters(self):
        # PROTECTED REGION ID(AsyncTabata.ResetCounters) ENABLED START #
        """

        :return:None
        """
        DevFactory().get_dev_from_property(self, "prepCounter").CounterReset(
            self._prepare
        )
        DevFactory().get_dev_from_property(self, "workCounter").CounterReset(
            self._work
        )
        DevFactory().get_dev_from_property(self, "restCounter").CounterReset(
            self._rest
        )
        DevFactory().get_dev_from_property(self, "cycleCounter").CounterReset(
            self._cycles
        )
        DevFactory().get_dev_from_property(
            self, "tabatasCounter"
        ).CounterReset(self._tabatas)
        # PROTECTED REGION END #    //  AsyncTabata.ResetCounters


# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    """Main function of the AsyncTabata module."""
    # PROTECTED REGION ID(AsyncTabata.main) ENABLED START #
    debugpy.listen(5678)
    kwargs.setdefault("green_mode", GreenMode.Asyncio)
    return run((AsyncTabata,), args=args, **kwargs)
    # AsyncTabata.run_server()
    # PROTECTED REGION END #    //  AsyncTabata.main


if __name__ == "__main__":
    main()
