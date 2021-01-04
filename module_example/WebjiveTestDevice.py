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

    RandomAttr = attribute(
        dtype='double',
    )

    DishState = attribute(
        dtype='DevEnum',
        access=AttrWriteType.WRITE,
        enum_labels=["Standby", "Ready", "Slew", "Track", "Scan", "Stow", "Error", ],
    )

    routingTable = attribute(
        dtype='str',
        label="Routing Table",
        doc="JSON String encoding the current routing configuration",
    )

    spectrum_att = attribute(
        dtype=('double',),
        max_dim_x=2048,
    )

    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        Device.init_device(self)
        self.set_change_event("RandomAttr", True, False)
        self.set_change_event("DishState", True, False)
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

    def read_RandomAttr(self):
        # PROTECTED REGION ID(WebjiveTestDevice.RandomAttr_read) ENABLED START #
        self.RandomAttr = random.random() * 100
        return self.RandomAttr
        # PROTECTED REGION END #    //  WebjiveTestDevice.RandomAttr_read

    def write_DishState(self, value):
        # PROTECTED REGION ID(WebjiveTestDevice.DishState_write) ENABLED START #
        pass
        # PROTECTED REGION END #    //  WebjiveTestDevice.DishState_write

    def read_routingTable(self):
        # PROTECTED REGION ID(WebjiveTestDevice.routingTable_read) ENABLED START #
        return """{ "routes": [ { "src": { "channel": """ + str(random.randint(0, 100)) + """ }
               , "dst": { "port": """ + str(random.randint(0, 20)) + """ } }
               , { "src": { "channel": """ + str(random.randint(100, 500)) + """ }, 
               "dst": { "port": """ + str(random.randint(0, 30)) + """ } } ] }"""
        # PROTECTED REGION END #    //  WebjiveTestDevice.routingTable_read

    def read_spectrum_att(self):
        # PROTECTED REGION ID(WebjiveTestDevice.spectrum_att_read) ENABLED START #
        a = np.array(random.random() * 100)

        for count in range(1, 1024):
            a = np.append(a, random.random() * 100)

        self.spectrum_att = a
        return self.spectrum_att
        # PROTECTED REGION END #    //  WebjiveTestDevice.spectrum_att_read


    # --------
    # Commands
    # --------

    @command(
    dtype_in='str', 
    doc_in="JSON String describing one or more routing rules to add.", 
    dtype_out='str', 
    )
    @DebugIt()
    def AddRoutes(self, argin):
        # PROTECTED REGION ID(WebjiveTestDevice.AddRoutes) ENABLED START #
        routes = json.loads(argin)["routes"]
        print(routes)
        return routes
        # PROTECTED REGION END #    //  WebjiveTestDevice.AddRoutes

    @command(
    dtype_in='bool', 
    doc_in="Get JSON", 
    dtype_out='str', 
    doc_out="Get JSON", 
    )
    @DebugIt()
    def json(self, argin):
        # PROTECTED REGION ID(WebjiveTestDevice.json) ENABLED START #
        jsonOut = {'foo': 19, 'bar': {'baz': 'Kimberly Robinson', 'poo': 3.33}}
        print(json.dumps(jsonOut))
        return json.dumps(jsonOut)
        # PROTECTED REGION END #    //  WebjiveTestDevice.json

    @command(
    dtype_in='bool', 
    doc_in="Control led status", 
    dtype_out='str', 
    doc_out="Get server response", 
    )
    @DebugIt()
    def led(self, argin):
        # PROTECTED REGION ID(WebjiveTestDevice.led) ENABLED START #
        return str(led)
        # PROTECTED REGION END #    //  WebjiveTestDevice.led

    @command(
    dtype_in='float', 
    doc_in="Ramp target current", 
    dtype_out='float', 
    doc_out="target_current\nFalse otherwise", 
    )
    @DebugIt()
    def ramp(self, argin):
        # PROTECTED REGION ID(WebjiveTestDevice.ramp) ENABLED START #
        self.set_current(argin)
        return argin
        # PROTECTED REGION END #    //  WebjiveTestDevice.ramp

    @command(
    dtype_in='bool', 
    doc_in="Boolean type", 
    dtype_out='str', 
    doc_out="Return the type of input Arg", 
    )
    @DebugIt()
    def testBoolean(self, argin):
        # PROTECTED REGION ID(WebjiveTestDevice.testBoolean) ENABLED START #
        return str(argin)
        # PROTECTED REGION END #    //  WebjiveTestDevice.testBoolean

    @command(
    dtype_in='int16', 
    doc_in="Integer Type", 
    dtype_out='str', 
    doc_out="Return the type of input Arg", 
    )
    @DebugIt()
    def testInt(self, argin):
        # PROTECTED REGION ID(WebjiveTestDevice.testInt) ENABLED START #
        return str(type(argin))+str(argin)
        # PROTECTED REGION END #    //  WebjiveTestDevice.testInt

    @command(
    dtype_in='float', 
    doc_in="Float Type", 
    dtype_out='str', 
    doc_out="Return the type of input Arg", 
    )
    @DebugIt()
    def testFloat(self, argin):
        # PROTECTED REGION ID(WebjiveTestDevice.testFloat) ENABLED START #
        return str(type(argin))+str(argin)
        # PROTECTED REGION END #    //  WebjiveTestDevice.testFloat

    @command(
    dtype_in='str', 
    doc_in="String Type", 
    dtype_out='str', 
    doc_out="Return the type of input Arg", 
    )
    @DebugIt()
    def testStr(self, argin):
        # PROTECTED REGION ID(WebjiveTestDevice.testStr) ENABLED START #
        return str(type(argin))+str(argin)
        # PROTECTED REGION END #    //  WebjiveTestDevice.testStr

    @command(
    dtype_in='DevEnum', 
    doc_in="Enum Type", 
    dtype_out='str', 
    doc_out="Return the type of input Arg", 
    )
    @DebugIt()
    def testDevEnum(self, argin):
        # PROTECTED REGION ID(WebjiveTestDevice.testDevEnum) ENABLED START #
        return str(type(argin))+str(argin)
        # PROTECTED REGION END #    //  WebjiveTestDevice.testDevEnum

    @command(
    dtype_in=('char',), 
    doc_in="VarCharArray Type", 
    dtype_out='str', 
    doc_out="Return the type of input Arg", 
    )
    @DebugIt()
    def testDevVarCharArray(self, argin):
        # PROTECTED REGION ID(WebjiveTestDevice.testDevVarCharArray) ENABLED START #
        return str(type(argin))+str(argin)
        # PROTECTED REGION END #    //  WebjiveTestDevice.testDevVarCharArray

    @command(
    dtype_in=('int16',), 
    doc_in="DevVarShortArray type", 
    dtype_out='str', 
    doc_out="Return the type of input Arg", 
    )
    @DebugIt()
    def testDevVarShortArray(self, argin):
        # PROTECTED REGION ID(WebjiveTestDevice.testDevVarShortArray) ENABLED START #
        return str(type(argin)) + str(argin)
        # PROTECTED REGION END #    //  WebjiveTestDevice.testDevVarShortArray

    @command(
    dtype_in=('int',), 
    doc_in="DevVarLongArray type", 
    dtype_out='str', 
    doc_out="Return the type of input Arg", 
    )
    @DebugIt()
    def testDevVarLongArray(self, argin):
        # PROTECTED REGION ID(WebjiveTestDevice.testDevVarLongArray) ENABLED START #
        return str(type(argin))+str(argin)
        # PROTECTED REGION END #    //  WebjiveTestDevice.testDevVarLongArray

    @command(
    dtype_in=('str',), 
    doc_in="DevVarStringArray", 
    dtype_out='str', 
    doc_out="Return the type of input Arg", 
    )
    @DebugIt()
    def testDevVarStringArray(self, argin):
        # PROTECTED REGION ID(WebjiveTestDevice.testDevVarStringArray) ENABLED START #
        return str(type(argin))+str(argin)
        # PROTECTED REGION END #    //  WebjiveTestDevice.testDevVarStringArray

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(WebjiveTestDevice.main) ENABLED START #
    return run((WebjiveTestDevice,), args=args, **kwargs)
    # PROTECTED REGION END #    //  WebjiveTestDevice.main

if __name__ == '__main__':
    main()
