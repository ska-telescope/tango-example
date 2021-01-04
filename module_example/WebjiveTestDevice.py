# -*- coding: utf-8 -*-
#
# This file is part of the WebjiveTestDevice project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" WebjiveTestDevice

"""

# PyTango imports
import PyTango
from PyTango import DebugIt
from PyTango.server import run
from PyTango.server import Device, DeviceMeta
from PyTango.server import attribute, command
from PyTango import AttrQuality, DispLevel, DevState
from PyTango import AttrWriteType, PipeWriteType
# Additional import
# PROTECTED REGION ID(WebjiveTestDevice.additionnal_import) ENABLED START #
import random
import numpy as np
import json

# PROTECTED REGION END #    //  WebjiveTestDevice.additionnal_import

__all__ = ["WebjiveTestDevice", "main"]


class WebjiveTestDevice(Device):
    """
    """
    __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(WebjiveTestDevice.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  WebjiveTestDevice.class_variable

    # ----------
    # Attributes
    # ----------

    routingTable = attribute(
        dtype="DevString",
        label="Routing Table",
        doc="JSON String encoding the current routing configuration",
    )

    RandomAttr = attribute(
        dtype='double',
    )

    DishState = attribute(
        dtype='DevEnum',
        access=AttrWriteType.WRITE,
        enum_labels=["Standby", "Ready", "Slew", "Track", "Scan", "Stow", "Error", ],
    )

    spectrum_att = attribute(
        dtype=('double',),
        max_dim_x=2048,
    )

    current = attribute(label="Current", dtype=float,
                        display_level=DispLevel.EXPERT,
                        access=AttrWriteType.READ_WRITE,
                        unit="A", format="8.4f",
                        min_value=0.0, max_value=8.5,
                        min_alarm=0.1, max_alarm=8.4,
                        min_warning=0.5, max_warning=8.0,
                        fget="get_current",
                        fset="set_current",
                        doc="the power supply current")

    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        Device.init_device(self)
        self.set_change_event("RandomAttr", True, False)
        self.set_change_event("DishState", True, False)
        self.set_current(0.0)
        self.set_state(DevState.STANDBY)
        # PROTECTED REGION ID(WebjiveTestDevice.init_device) ENABLED START #
        # PROTECTED REGION END #    //  WebjiveTestDevice.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(WebjiveTestDevice.always_executed_hook) ENABLED START #
        pass
        # PROTECTED REGION END #    //  WebjiveTestDevice.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(WebjiveTestDevice.delete_device) ENABLED START #
        pass
        # PROTECTED REGION END #    //  WebjiveTestDevice.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_routingTable(self):
        # PROTECTED REGION ID(LowCbfNetwork.routingTable_read) ENABLED START #
        """Return the routingTable attribute."""

        return """{ "routes": [ { "src": { "channel": 123 }, "dst": { "port": 12 } }, { "src": { "channel": 345 }, "dst": { "port": 34 } } ] }"""

    def read_RandomAttr(self):
        # PROTECTED REGION ID(WebjiveTestDevice.RandomAttr_read) ENABLED START #
        self.RandomAttr = random.random() * 100
        return self.RandomAttr
        # PROTECTED REGION END #    //  WebjiveTestDevice.RandomAttr_read

    def write_DishState(self, value):
        # PROTECTED REGION ID(WebjiveTestDevice.DishState_write) ENABLED START #
        pass
        # PROTECTED REGION END #    //  WebjiveTestDevice.DishState_write

    def read_spectrum_att(self):
        # PROTECTED REGION ID(WebjiveTestDevice.spectrum_att_read) ENABLED START #
        a = np.array(random.random() * 100)

        for count in range(1, 1024):
            a = np.append(a, random.random() * 100)

        self.spectrum_att = a
        return self.spectrum_att
        # PROTECTED REGION END #    //  WebjiveTestDevice.spectrum_att_read

    def get_current(self):
        """Get the current"""
        return self.__current

    def set_current(self, current):
        """Set the current"""
        self.__current = current

    # --------
    # Commands
    # --------
    #{'foo': 19, 'bar': {'baz': 'Kimberly Robinson', 'poo': 3.33}}

    @command(
        dtype_in="DevString",
        doc_in="JSON String describing one or more routing rules to add.",
    )
    def AddRoutes(self, argin):
        # PROTECTED REGION ID(LowCbfNetwork.AddRoutes) ENABLED START #
        """

        :param argin: 'DevString'
        JSON String describing one or more routing rules to add.
        e.g. '{"routes": [{"src": {"channel": 123}, "dst": {"port": 12}}] }'
        We assume src is a channel and dst is a port.

        :return:None
        """
        routes = json.loads(argin)["routes"]
        print(routes)
        return routes

    @command(dtype_in=bool, doc_in="Get JSON",
             dtype_out=str, doc_out="Get JSON")
    def json(self, led):
        """Get JSON output"""
        jsonOut = {'foo': 19, 'bar': {'baz': 'Kimberly Robinson', 'poo': 3.33}}
        print(json.dumps(jsonOut))
        return json.dumps(jsonOut)

    @command(dtype_in=bool, doc_in="Control led status",
             dtype_out=str, doc_out="Get server response")
    def led(self, led):
        """Control led status"""
        # should do the ramping. This doesn't.
        return str(led)

    @command(dtype_in=float, doc_in="Ramp target current",
             dtype_out=float, doc_out="target_current"
                                     "False otherwise")
    def ramp(self, target_current):
        """Ramp voltage to the target current"""
        # should do the ramping. This doesn't.
        self.set_current(target_current)
        return target_current

    @command(dtype_in=bool, doc_in="Boolean type",
             dtype_out=str, doc_out="Return the type of input Arg")

    def testBoolean(self, argin):
        """Return the type"""
        return str(argin)

    @command(dtype_in=int, doc_in="Integer type",
             dtype_out=str, doc_out="Return the type of input Arg")

    def testInt(self, argin):
        """Return the type"""
        return str(type(argin))+str(argin)

    @command(dtype_in=float, doc_in="Float type",
             dtype_out=str, doc_out="Return the type of input Arg")

    def testFloat(self, argin):
        """Return the type"""
        return str(type(argin))+str(argin)
    
    @command(dtype_in=str, doc_in="String type",
             dtype_out=str, doc_out="Return the type of input Arg")

    def testStr(self, argin):
        """Return the type"""
        return str(type(argin))+str(argin)

    @command(dtype_in='DevEnum', doc_in="DevEnum type",
             dtype_out=str, doc_out="Return the type of input Arg")

    def testDevEnum(self, argin):
        """Return the type"""
        return str(type(argin))+str(argin)

    @command(dtype_in='DevVarCharArray', doc_in="DevVarCharArray type",
             dtype_out=str, doc_out="Return the type of input Arg")

    def testDevVarCharArray(self, argin):
        """Return the type"""
        return str(type(argin))+str(argin)

    @command(dtype_in='DevVarShortArray', doc_in="DevVarShortArray type",
             dtype_out=str, doc_out="Return the type of input Arg")

    def testDevVarShortArray(self, argin):
        """Return the type"""
        return str(type(argin))+str(argin)
    
    @command(dtype_in='DevVarLongArray', doc_in="DevVarLongArray type",
             dtype_out=str, doc_out="Return the type of input Arg")

    def testDevVarLongArray(self, argin):
        """Return the type"""
        return str(type(argin))+str(argin)

    @command(dtype_in='DevVarStringArray', doc_in="DevVarStringArray type",
             dtype_out=str, doc_out="Return the type of input Arg")

    def testDevVarStringArray(self, argin):
        """Return the type"""
        return str(type(argin))+str(argin)

# ----------
# DevVarStringArray 
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(WebjiveTestDevice.main) ENABLED START #
    return run((WebjiveTestDevice,), args=args, **kwargs)
    # PROTECTED REGION END #    //  WebjiveTestDevice.main

if __name__ == '__main__':
    main()
