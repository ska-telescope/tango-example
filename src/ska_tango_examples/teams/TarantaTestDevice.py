# -*- coding: utf-8 -*-
#
# This file is part of the TarantaTestDevice project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" TarantaTestDevice

"""

import json
import logging

# Additional import
# PROTECTED REGION ID(TarantaTestDevice.additionnal_import) ENABLED START #
import random

import numpy as np

# PyTango imports
from tango import AttrWriteType, DebugIt, DevState
from tango.server import Device, DeviceMeta, attribute, command, run

auto_dishState = True
auto_obsState = True
# PROTECTED REGION END #    //  TarantaTestDevice.additionnal_import


__all__ = ["TarantaTestDevice", "main"]


class TarantaTestDevice(Device):
    """ """

    __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(TarantaTestDevice.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  TarantaTestDevice.class_variable

    # ----------
    # Attributes
    # ----------

    RandomAttr = attribute(
        dtype="double",
    )

    Int_RO_001 = attribute(
        dtype="DevShort",
    )

    Int_RO_002 = attribute(
        dtype="DevShort",
    )

    Int_RO_003 = attribute(
        dtype="DevShort",
    )

    Int_RO_004 = attribute(
        dtype="DevShort",
    )

    Int_RO_005 = attribute(
        dtype="DevShort",
    )

    Int_RO_006 = attribute(
        dtype="DevShort",
    )

    Int_RO_007 = attribute(
        dtype="DevShort",
    )

    Int_RO_008 = attribute(
        dtype="DevShort",
    )

    Int_RO_009 = attribute(
        dtype="DevShort",
    )

    Int_RO_010 = attribute(
        dtype="DevShort",
    )

    Int_RO_011 = attribute(
        dtype="DevShort",
    )

    Int_RO_012 = attribute(
        dtype="DevShort",
    )

    Int_RO_013 = attribute(
        dtype="DevShort",
    )

    Int_RO_014 = attribute(
        dtype="DevShort",
    )

    Int_RO_015 = attribute(
        dtype="DevShort",
    )

    Int_RO_016 = attribute(
        dtype="DevShort",
    )

    Int_RO_017 = attribute(
        dtype="DevShort",
    )

    Int_RO_018 = attribute(
        dtype="DevShort",
    )

    Int_RO_019 = attribute(
        dtype="DevShort",
    )

    Int_RO_020 = attribute(
        dtype="DevShort",
    )

    Int_RO_021 = attribute(
        dtype="DevShort",
    )

    Int_RO_022 = attribute(
        dtype="DevShort",
    )

    Int_RO_023 = attribute(
        dtype="DevShort",
    )

    Int_RO_024 = attribute(
        dtype="DevShort",
    )

    Int_RO_025 = attribute(
        dtype="DevShort",
    )

    Int_RO_026 = attribute(
        dtype="DevShort",
    )

    Int_RO_027 = attribute(
        dtype="DevShort",
    )

    Int_RO_028 = attribute(
        dtype="DevShort",
    )

    Int_RO_029 = attribute(
        dtype="DevShort",
    )

    Int_RO_030 = attribute(
        dtype="DevShort",
    )

    Int_RO_031 = attribute(
        dtype="DevShort",
    )

    Int_RO_032 = attribute(
        dtype="DevShort",
    )

    Int_RO_033 = attribute(
        dtype="DevShort",
    )

    Int_RO_034 = attribute(
        dtype="DevShort",
    )

    Int_RO_035 = attribute(
        dtype="DevShort",
    )

    Int_RO_036 = attribute(
        dtype="DevShort",
    )

    Int_RO_037 = attribute(
        dtype="DevShort",
    )

    Int_RO_038 = attribute(
        dtype="DevShort",
    )

    Int_RO_039 = attribute(
        dtype="DevShort",
    )

    Int_RO_040 = attribute(
        dtype="DevShort",
    )

    Int_RO_041 = attribute(
        dtype="DevShort",
    )

    Int_RO_042 = attribute(
        dtype="DevShort",
    )

    Int_RO_043 = attribute(
        dtype="DevShort",
    )

    Int_RO_044 = attribute(
        dtype="DevShort",
    )

    Int_RO_045 = attribute(
        dtype="DevShort",
    )

    Int_RO_046 = attribute(
        dtype="DevShort",
    )

    Int_RO_047 = attribute(
        dtype="DevShort",
    )

    Int_RO_048 = attribute(
        dtype="DevShort",
    )

    Int_RO_049 = attribute(
        dtype="DevShort",
    )

    Int_RO_050 = attribute(
        dtype="DevShort",
    )

    Int_RO_051 = attribute(
        dtype="DevShort",
    )

    Int_RO_052 = attribute(
        dtype="DevShort",
    )

    Int_RO_053 = attribute(
        dtype="DevShort",
    )

    Int_RO_054 = attribute(
        dtype="DevShort",
    )

    Int_RO_055 = attribute(
        dtype="DevShort",
    )

    Int_RO_056 = attribute(
        dtype="DevShort",
    )

    Int_RO_057 = attribute(
        dtype="DevShort",
    )

    Int_RO_058 = attribute(
        dtype="DevShort",
    )

    Int_RO_059 = attribute(
        dtype="DevShort",
    )

    Int_RO_060 = attribute(
        dtype="DevShort",
    )

    Int_RO_061 = attribute(
        dtype="DevShort",
    )

    Int_RO_062 = attribute(
        dtype="DevShort",
    )

    Int_RO_063 = attribute(
        dtype="DevShort",
    )

    Int_RO_064 = attribute(
        dtype="DevShort",
    )

    Int_RO_065 = attribute(
        dtype="DevShort",
    )

    Int_RO_066 = attribute(
        dtype="DevShort",
    )

    Int_RO_067 = attribute(
        dtype="DevShort",
    )

    Int_RO_068 = attribute(
        dtype="DevShort",
    )

    Int_RO_069 = attribute(
        dtype="DevShort",
    )

    Int_RO_070 = attribute(
        dtype="DevShort",
    )

    Int_RO_071 = attribute(
        dtype="DevShort",
    )

    Int_RO_072 = attribute(
        dtype="DevShort",
    )

    Int_RO_073 = attribute(
        dtype="DevShort",
    )

    Int_RO_074 = attribute(
        dtype="DevShort",
    )

    Int_RO_075 = attribute(
        dtype="DevShort",
    )

    Int_RO_076 = attribute(
        dtype="DevShort",
    )

    Int_RO_077 = attribute(
        dtype="DevShort",
    )

    Int_RO_078 = attribute(
        dtype="DevShort",
    )

    Int_RO_079 = attribute(
        dtype="DevShort",
    )

    Int_RO_080 = attribute(
        dtype="DevShort",
    )

    Int_RO_081 = attribute(
        dtype="DevShort",
    )

    Int_RO_082 = attribute(
        dtype="DevShort",
    )

    Int_RO_083 = attribute(
        dtype="DevShort",
    )

    Int_RO_084 = attribute(
        dtype="DevShort",
    )

    Int_RO_085 = attribute(
        dtype="DevShort",
    )

    Int_RO_086 = attribute(
        dtype="DevShort",
    )

    Int_RO_087 = attribute(
        dtype="DevShort",
    )

    Int_RO_088 = attribute(
        dtype="DevShort",
    )

    Int_RO_089 = attribute(
        dtype="DevShort",
    )

    Int_RO_090 = attribute(
        dtype="DevShort",
    )

    Int_RO_091 = attribute(
        dtype="DevShort",
    )

    Int_RO_092 = attribute(
        dtype="DevShort",
    )

    Int_RO_093 = attribute(
        dtype="DevShort",
    )

    Int_RO_094 = attribute(
        dtype="DevShort",
    )

    Int_RO_095 = attribute(
        dtype="DevShort",
    )

    Int_RO_096 = attribute(
        dtype="DevShort",
    )

    Int_RO_097 = attribute(
        dtype="DevShort",
    )

    Int_RO_098 = attribute(
        dtype="DevShort",
    )

    Int_RO_099 = attribute(
        dtype="DevShort",
    )

    Int_RO_100 = attribute(
        dtype="DevShort",
    )

    DishState = attribute(
        dtype="DevEnum",
        access=AttrWriteType.READ_WRITE,
        enum_labels=[
            "Standby",
            "Ready",
            "Slew",
            "Track",
            "Scan",
            "Stow",
            "Error",
        ],
    )

    routingTable = attribute(
        dtype="str",
        label="Routing Table",
        doc="JSON String encoding the current routing configuration",
    )

    CspObsState = attribute(
        dtype="DevEnum",
        access=AttrWriteType.READ_WRITE,
        enum_labels=[
            "Empty",
            "Resourcing",
            "Idle",
            "Configuring",
            "Ready",
            "Scanning",
            "Aborting",
            "Aborted",
            "Resetting",
            "Fault",
            "Restarting",
        ],
    )

    CbfObsState = attribute(
        dtype="DevEnum",
        access=AttrWriteType.READ_WRITE,
        enum_labels=[
            "Empty",
            "Resourcing",
            "Idle",
            "Configuring",
            "Ready",
            "Scanning",
            "Aborting",
            "Aborted",
            "Resetting",
            "Fault",
            "Restarting",
        ],
    )

    stringRW = attribute(
        dtype="str",
        access=AttrWriteType.READ_WRITE,
        label="StringAttr READ_WRITE",
        doc="StringAttr READ_WRITE",
    )

    stringR = attribute(
        dtype="str",
        label="string READ",
        doc="StringAttr READ",
    )

    spectrum_att = attribute(
        dtype=("double",),
        max_dim_x=2048,
    )

    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        Device.init_device(self)
        self.set_change_event("RandomAttr", True, False)

        self.set_change_event("Int_RO_001", True, False)
        self.set_change_event("Int_RO_002", True, False)
        self.set_change_event("Int_RO_003", True, False)
        self.set_change_event("Int_RO_004", True, False)
        self.set_change_event("Int_RO_005", True, False)
        self.set_change_event("Int_RO_006", True, False)
        self.set_change_event("Int_RO_007", True, False)
        self.set_change_event("Int_RO_008", True, False)
        self.set_change_event("Int_RO_009", True, False)
        self.set_change_event("Int_RO_010", True, False)
        self.set_change_event("Int_RO_011", True, False)
        self.set_change_event("Int_RO_012", True, False)
        self.set_change_event("Int_RO_013", True, False)
        self.set_change_event("Int_RO_014", True, False)
        self.set_change_event("Int_RO_015", True, False)
        self.set_change_event("Int_RO_016", True, False)
        self.set_change_event("Int_RO_017", True, False)
        self.set_change_event("Int_RO_018", True, False)
        self.set_change_event("Int_RO_019", True, False)
        self.set_change_event("Int_RO_020", True, False)
        self.set_change_event("Int_RO_021", True, False)
        self.set_change_event("Int_RO_022", True, False)
        self.set_change_event("Int_RO_023", True, False)
        self.set_change_event("Int_RO_024", True, False)
        self.set_change_event("Int_RO_025", True, False)
        self.set_change_event("Int_RO_026", True, False)
        self.set_change_event("Int_RO_027", True, False)
        self.set_change_event("Int_RO_028", True, False)
        self.set_change_event("Int_RO_029", True, False)
        self.set_change_event("Int_RO_030", True, False)
        self.set_change_event("Int_RO_031", True, False)
        self.set_change_event("Int_RO_032", True, False)
        self.set_change_event("Int_RO_033", True, False)
        self.set_change_event("Int_RO_034", True, False)
        self.set_change_event("Int_RO_035", True, False)
        self.set_change_event("Int_RO_036", True, False)
        self.set_change_event("Int_RO_037", True, False)
        self.set_change_event("Int_RO_038", True, False)
        self.set_change_event("Int_RO_039", True, False)
        self.set_change_event("Int_RO_040", True, False)
        self.set_change_event("Int_RO_041", True, False)
        self.set_change_event("Int_RO_042", True, False)
        self.set_change_event("Int_RO_043", True, False)
        self.set_change_event("Int_RO_044", True, False)
        self.set_change_event("Int_RO_045", True, False)
        self.set_change_event("Int_RO_046", True, False)
        self.set_change_event("Int_RO_047", True, False)
        self.set_change_event("Int_RO_048", True, False)
        self.set_change_event("Int_RO_049", True, False)
        self.set_change_event("Int_RO_050", True, False)
        self.set_change_event("Int_RO_051", True, False)
        self.set_change_event("Int_RO_052", True, False)
        self.set_change_event("Int_RO_053", True, False)
        self.set_change_event("Int_RO_054", True, False)
        self.set_change_event("Int_RO_055", True, False)
        self.set_change_event("Int_RO_056", True, False)
        self.set_change_event("Int_RO_057", True, False)
        self.set_change_event("Int_RO_058", True, False)
        self.set_change_event("Int_RO_059", True, False)
        self.set_change_event("Int_RO_060", True, False)
        self.set_change_event("Int_RO_061", True, False)
        self.set_change_event("Int_RO_062", True, False)
        self.set_change_event("Int_RO_063", True, False)
        self.set_change_event("Int_RO_064", True, False)
        self.set_change_event("Int_RO_065", True, False)
        self.set_change_event("Int_RO_066", True, False)
        self.set_change_event("Int_RO_067", True, False)
        self.set_change_event("Int_RO_068", True, False)
        self.set_change_event("Int_RO_069", True, False)
        self.set_change_event("Int_RO_070", True, False)
        self.set_change_event("Int_RO_071", True, False)
        self.set_change_event("Int_RO_072", True, False)
        self.set_change_event("Int_RO_073", True, False)
        self.set_change_event("Int_RO_074", True, False)
        self.set_change_event("Int_RO_075", True, False)
        self.set_change_event("Int_RO_076", True, False)
        self.set_change_event("Int_RO_077", True, False)
        self.set_change_event("Int_RO_078", True, False)
        self.set_change_event("Int_RO_079", True, False)
        self.set_change_event("Int_RO_080", True, False)
        self.set_change_event("Int_RO_081", True, False)
        self.set_change_event("Int_RO_082", True, False)
        self.set_change_event("Int_RO_083", True, False)
        self.set_change_event("Int_RO_084", True, False)
        self.set_change_event("Int_RO_085", True, False)
        self.set_change_event("Int_RO_086", True, False)
        self.set_change_event("Int_RO_087", True, False)
        self.set_change_event("Int_RO_088", True, False)
        self.set_change_event("Int_RO_089", True, False)
        self.set_change_event("Int_RO_090", True, False)
        self.set_change_event("Int_RO_091", True, False)
        self.set_change_event("Int_RO_092", True, False)
        self.set_change_event("Int_RO_093", True, False)
        self.set_change_event("Int_RO_094", True, False)
        self.set_change_event("Int_RO_095", True, False)
        self.set_change_event("Int_RO_096", True, False)
        self.set_change_event("Int_RO_097", True, False)
        self.set_change_event("Int_RO_098", True, False)
        self.set_change_event("Int_RO_099", True, False)
        self.set_change_event("Int_RO_100", True, False)

        self.set_change_event("DishState", True, False)
        # PROTECTED REGION ID(TarantaTestDevice.init_device) ENABLED START #
        self.__stringRW = "stringRW"
        self.__stringR = "stringR"
        self.__routingTable = (
            """{ "routes": [ { "src": { "channel": """,
            str(random.randint(0, 100)),
            """ }, "dst": { "port": """,
            str(random.randint(0, 20)),
            """ } }, { "src": { "channel": """,
            str(random.randint(100, 500)),
            """ }, "dst": { "port": """,
            str(random.randint(0, 30)),
            """ } } ] }""",
        )  # noqa: W291
        self.set_state(DevState.STANDBY)
        # PROTECTED REGION END #    //  TarantaTestDevice.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(TarantaTestDevice.always_executed_hook) ENABLED START # noqa E501
        pass
        # PROTECTED REGION END #    //  TarantaTestDevice.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(TarantaTestDevice.delete_device) ENABLED START #
        pass
        # PROTECTED REGION END #    //  TarantaTestDevice.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_RandomAttr(self):
        # PROTECTED REGION ID(TarantaTestDevice.RandomAttr_read) ENABLED START # noqa E501
        self.RandomAttr = random.random() * 100
        return self.RandomAttr
        # PROTECTED REGION END #    //  TarantaTestDevice.RandomAttr_read

    def read_Int_RO_001(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_001) ENABLED START # noqa E501
        self.Int_RO_001 = random.randint(0, 100)
        return self.Int_RO_001
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_001

    def read_Int_RO_002(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_002) ENABLED START # noqa E501
        self.Int_RO_002 = random.randint(0, 100)
        return self.Int_RO_002
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_002

    def read_Int_RO_003(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_003) ENABLED START # noqa E501
        self.Int_RO_003 = random.randint(0, 100)
        return self.Int_RO_003
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_003

    def read_Int_RO_004(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_004) ENABLED START # noqa E501
        self.Int_RO_004 = random.randint(0, 100)
        return self.Int_RO_004
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_004

    def read_Int_RO_005(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_005) ENABLED START # noqa E501
        self.Int_RO_005 = random.randint(0, 100)
        return self.Int_RO_005
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_005

    def read_Int_RO_006(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_006) ENABLED START # noqa E501
        self.Int_RO_006 = random.randint(0, 100)
        return self.Int_RO_006
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_006

    def read_Int_RO_007(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_007) ENABLED START # noqa E501
        self.Int_RO_007 = random.randint(0, 100)
        return self.Int_RO_007
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_007

    def read_Int_RO_008(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_008) ENABLED START # noqa E501
        self.Int_RO_008 = random.randint(0, 100)
        return self.Int_RO_008
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_008

    def read_Int_RO_009(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_009) ENABLED START # noqa E501
        self.Int_RO_009 = random.randint(0, 100)
        return self.Int_RO_009
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_009

    def read_Int_RO_010(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_010) ENABLED START # noqa E501
        self.Int_RO_010 = random.randint(0, 100)
        return self.Int_RO_010
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_010

    def read_Int_RO_011(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_011) ENABLED START # noqa E501
        self.Int_RO_011 = random.randint(0, 100)
        return self.Int_RO_011
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_011

    def read_Int_RO_012(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_012) ENABLED START # noqa E501
        self.Int_RO_012 = random.randint(0, 100)
        return self.Int_RO_012
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_012

    def read_Int_RO_013(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_013) ENABLED START # noqa E501
        self.Int_RO_013 = random.randint(0, 100)
        return self.Int_RO_013
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_013

    def read_Int_RO_014(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_014) ENABLED START # noqa E501
        self.Int_RO_014 = random.randint(0, 100)
        return self.Int_RO_014
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_014

    def read_Int_RO_015(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_015) ENABLED START # noqa E501
        self.Int_RO_015 = random.randint(0, 100)
        return self.Int_RO_015
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_015

    def read_Int_RO_016(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_016) ENABLED START # noqa E501
        self.Int_RO_016 = random.randint(0, 100)
        return self.Int_RO_016
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_016

    def read_Int_RO_017(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_017) ENABLED START # noqa E501
        self.Int_RO_017 = random.randint(0, 100)
        return self.Int_RO_017
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_017

    def read_Int_RO_018(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_018) ENABLED START # noqa E501
        self.Int_RO_018 = random.randint(0, 100)
        return self.Int_RO_018
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_018

    def read_Int_RO_019(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_019) ENABLED START # noqa E501
        self.Int_RO_019 = random.randint(0, 100)
        return self.Int_RO_019
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_019

    def read_Int_RO_020(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_020) ENABLED START # noqa E501
        self.Int_RO_020 = random.randint(0, 100)
        return self.Int_RO_020
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_020

    def read_Int_RO_021(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_021) ENABLED START # noqa E502
        self.Int_RO_021 = random.randint(0, 100)
        return self.Int_RO_021
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_021

    def read_Int_RO_022(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_022) ENABLED START # noqa E502
        self.Int_RO_022 = random.randint(0, 100)
        return self.Int_RO_022
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_022

    def read_Int_RO_023(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_023) ENABLED START # noqa E502
        self.Int_RO_023 = random.randint(0, 100)
        return self.Int_RO_023
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_023

    def read_Int_RO_024(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_024) ENABLED START # noqa E502
        self.Int_RO_024 = random.randint(0, 100)
        return self.Int_RO_024
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_024

    def read_Int_RO_025(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_025) ENABLED START # noqa E502
        self.Int_RO_025 = random.randint(0, 100)
        return self.Int_RO_025
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_025

    def read_Int_RO_026(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_026) ENABLED START # noqa E502
        self.Int_RO_026 = random.randint(0, 100)
        return self.Int_RO_026
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_026

    def read_Int_RO_027(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_027) ENABLED START # noqa E502
        self.Int_RO_027 = random.randint(0, 100)
        return self.Int_RO_027
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_027

    def read_Int_RO_028(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_028) ENABLED START # noqa E502
        self.Int_RO_028 = random.randint(0, 100)
        return self.Int_RO_028
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_028

    def read_Int_RO_029(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_029) ENABLED START # noqa E502
        self.Int_RO_029 = random.randint(0, 100)
        return self.Int_RO_029
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_029

    def read_Int_RO_030(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_030) ENABLED START # noqa E502
        self.Int_RO_030 = random.randint(0, 100)
        return self.Int_RO_030
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_030

    def read_Int_RO_031(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_031) ENABLED START # noqa E503
        self.Int_RO_031 = random.randint(0, 100)
        return self.Int_RO_031
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_031

    def read_Int_RO_032(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_032) ENABLED START # noqa E503
        self.Int_RO_032 = random.randint(0, 100)
        return self.Int_RO_032
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_032

    def read_Int_RO_033(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_033) ENABLED START # noqa E503
        self.Int_RO_033 = random.randint(0, 100)
        return self.Int_RO_033
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_033

    def read_Int_RO_034(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_034) ENABLED START # noqa E503
        self.Int_RO_034 = random.randint(0, 100)
        return self.Int_RO_034
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_034

    def read_Int_RO_035(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_035) ENABLED START # noqa E503
        self.Int_RO_035 = random.randint(0, 100)
        return self.Int_RO_035
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_035

    def read_Int_RO_036(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_036) ENABLED START # noqa E503
        self.Int_RO_036 = random.randint(0, 100)
        return self.Int_RO_036
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_036

    def read_Int_RO_037(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_037) ENABLED START # noqa E503
        self.Int_RO_037 = random.randint(0, 100)
        return self.Int_RO_037
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_037

    def read_Int_RO_038(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_038) ENABLED START # noqa E503
        self.Int_RO_038 = random.randint(0, 100)
        return self.Int_RO_038
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_038

    def read_Int_RO_039(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_039) ENABLED START # noqa E503
        self.Int_RO_039 = random.randint(0, 100)
        return self.Int_RO_039
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_039

    def read_Int_RO_040(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_040) ENABLED START # noqa E503
        self.Int_RO_040 = random.randint(0, 100)
        return self.Int_RO_040
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_040

    def read_Int_RO_041(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_041) ENABLED START # noqa E504
        self.Int_RO_041 = random.randint(0, 100)
        return self.Int_RO_041
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_041

    def read_Int_RO_042(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_042) ENABLED START # noqa E504
        self.Int_RO_042 = random.randint(0, 100)
        return self.Int_RO_042
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_042

    def read_Int_RO_043(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_043) ENABLED START # noqa E504
        self.Int_RO_043 = random.randint(0, 100)
        return self.Int_RO_043
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_043

    def read_Int_RO_044(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_044) ENABLED START # noqa E504
        self.Int_RO_044 = random.randint(0, 100)
        return self.Int_RO_044
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_044

    def read_Int_RO_045(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_045) ENABLED START # noqa E504
        self.Int_RO_045 = random.randint(0, 100)
        return self.Int_RO_045
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_045

    def read_Int_RO_046(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_046) ENABLED START # noqa E504
        self.Int_RO_046 = random.randint(0, 100)
        return self.Int_RO_046
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_046

    def read_Int_RO_047(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_047) ENABLED START # noqa E504
        self.Int_RO_047 = random.randint(0, 100)
        return self.Int_RO_047
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_047

    def read_Int_RO_048(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_048) ENABLED START # noqa E504
        self.Int_RO_048 = random.randint(0, 100)
        return self.Int_RO_048
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_048

    def read_Int_RO_049(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_049) ENABLED START # noqa E504
        self.Int_RO_049 = random.randint(0, 100)
        return self.Int_RO_049
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_049

    def read_Int_RO_050(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_050) ENABLED START # noqa E504
        self.Int_RO_050 = random.randint(0, 100)
        return self.Int_RO_050
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_050

    def read_Int_RO_051(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_051) ENABLED START # noqa E505
        self.Int_RO_051 = random.randint(0, 100)
        return self.Int_RO_051
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_051

    def read_Int_RO_052(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_052) ENABLED START # noqa E505
        self.Int_RO_052 = random.randint(0, 100)
        return self.Int_RO_052
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_052

    def read_Int_RO_053(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_053) ENABLED START # noqa E505
        self.Int_RO_053 = random.randint(0, 100)
        return self.Int_RO_053
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_053

    def read_Int_RO_054(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_054) ENABLED START # noqa E505
        self.Int_RO_054 = random.randint(0, 100)
        return self.Int_RO_054
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_054

    def read_Int_RO_055(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_055) ENABLED START # noqa E505
        self.Int_RO_055 = random.randint(0, 100)
        return self.Int_RO_055
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_055

    def read_Int_RO_056(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_056) ENABLED START # noqa E505
        self.Int_RO_056 = random.randint(0, 100)
        return self.Int_RO_056
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_056

    def read_Int_RO_057(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_057) ENABLED START # noqa E505
        self.Int_RO_057 = random.randint(0, 100)
        return self.Int_RO_057
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_057

    def read_Int_RO_058(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_058) ENABLED START # noqa E505
        self.Int_RO_058 = random.randint(0, 100)
        return self.Int_RO_058
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_058

    def read_Int_RO_059(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_059) ENABLED START # noqa E505
        self.Int_RO_059 = random.randint(0, 100)
        return self.Int_RO_059
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_059

    def read_Int_RO_060(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_060) ENABLED START # noqa E505
        self.Int_RO_060 = random.randint(0, 100)
        return self.Int_RO_060
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_060

    def read_Int_RO_061(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_061) ENABLED START # noqa E506
        self.Int_RO_061 = random.randint(0, 100)
        return self.Int_RO_061
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_061

    def read_Int_RO_062(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_062) ENABLED START # noqa E506
        self.Int_RO_062 = random.randint(0, 100)
        return self.Int_RO_062
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_062

    def read_Int_RO_063(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_063) ENABLED START # noqa E506
        self.Int_RO_063 = random.randint(0, 100)
        return self.Int_RO_063
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_063

    def read_Int_RO_064(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_064) ENABLED START # noqa E506
        self.Int_RO_064 = random.randint(0, 100)
        return self.Int_RO_064
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_064

    def read_Int_RO_065(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_065) ENABLED START # noqa E506
        self.Int_RO_065 = random.randint(0, 100)
        return self.Int_RO_065
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_065

    def read_Int_RO_066(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_066) ENABLED START # noqa E506
        self.Int_RO_066 = random.randint(0, 100)
        return self.Int_RO_066
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_066

    def read_Int_RO_067(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_067) ENABLED START # noqa E506
        self.Int_RO_067 = random.randint(0, 100)
        return self.Int_RO_067
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_067

    def read_Int_RO_068(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_068) ENABLED START # noqa E506
        self.Int_RO_068 = random.randint(0, 100)
        return self.Int_RO_068
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_068

    def read_Int_RO_069(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_069) ENABLED START # noqa E506
        self.Int_RO_069 = random.randint(0, 100)
        return self.Int_RO_069
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_069

    def read_Int_RO_070(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_070) ENABLED START # noqa E506
        self.Int_RO_070 = random.randint(0, 100)
        return self.Int_RO_060
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_070

    def read_Int_RO_071(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_071) ENABLED START # noqa E507
        self.Int_RO_071 = random.randint(0, 100)
        return self.Int_RO_071
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_071

    def read_Int_RO_072(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_072) ENABLED START # noqa E507
        self.Int_RO_072 = random.randint(0, 100)
        return self.Int_RO_072
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_072

    def read_Int_RO_073(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_073) ENABLED START # noqa E507
        self.Int_RO_073 = random.randint(0, 100)
        return self.Int_RO_073
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_073

    def read_Int_RO_074(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_074) ENABLED START # noqa E507
        self.Int_RO_074 = random.randint(0, 100)
        return self.Int_RO_074
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_074

    def read_Int_RO_075(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_075) ENABLED START # noqa E507
        self.Int_RO_075 = random.randint(0, 100)
        return self.Int_RO_075
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_075

    def read_Int_RO_076(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_076) ENABLED START # noqa E507
        self.Int_RO_076 = random.randint(0, 100)
        return self.Int_RO_076
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_076

    def read_Int_RO_077(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_077) ENABLED START # noqa E507
        self.Int_RO_077 = random.randint(0, 100)
        return self.Int_RO_077
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_077

    def read_Int_RO_078(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_078) ENABLED START # noqa E507
        self.Int_RO_078 = random.randint(0, 100)
        return self.Int_RO_078
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_078

    def read_Int_RO_079(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_079) ENABLED START # noqa E507
        self.Int_RO_079 = random.randint(0, 100)
        return self.Int_RO_079
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_079

    def read_Int_RO_080(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_080) ENABLED START # noqa E507
        self.Int_RO_080 = random.randint(0, 100)
        return self.Int_RO_080
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_080

    def read_Int_RO_081(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_081) ENABLED START # noqa E508
        self.Int_RO_081 = random.randint(0, 100)
        return self.Int_RO_081
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_081

    def read_Int_RO_082(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_082) ENABLED START # noqa E508
        self.Int_RO_082 = random.randint(0, 100)
        return self.Int_RO_082
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_082

    def read_Int_RO_083(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_083) ENABLED START # noqa E508
        self.Int_RO_083 = random.randint(0, 100)
        return self.Int_RO_083
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_083

    def read_Int_RO_084(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_084) ENABLED START # noqa E508
        self.Int_RO_084 = random.randint(0, 100)
        return self.Int_RO_084
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_084

    def read_Int_RO_085(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_085) ENABLED START # noqa E508
        self.Int_RO_085 = random.randint(0, 100)
        return self.Int_RO_085
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_085

    def read_Int_RO_086(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_086) ENABLED START # noqa E508
        self.Int_RO_086 = random.randint(0, 100)
        return self.Int_RO_086
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_086

    def read_Int_RO_087(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_087) ENABLED START # noqa E508
        self.Int_RO_087 = random.randint(0, 100)
        return self.Int_RO_087
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_087

    def read_Int_RO_088(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_088) ENABLED START # noqa E508
        self.Int_RO_088 = random.randint(0, 100)
        return self.Int_RO_088
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_088

    def read_Int_RO_089(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_089) ENABLED START # noqa E508
        self.Int_RO_089 = random.randint(0, 100)
        return self.Int_RO_089
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_089

    def read_Int_RO_090(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_090) ENABLED START # noqa E508
        self.Int_RO_090 = random.randint(0, 100)
        return self.Int_RO_090
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_090

    def read_Int_RO_091(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_091) ENABLED START # noqa E509
        self.Int_RO_091 = random.randint(0, 100)
        return self.Int_RO_091
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_091

    def read_Int_RO_092(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_092) ENABLED START # noqa E509
        self.Int_RO_092 = random.randint(0, 100)
        return self.Int_RO_092
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_092

    def read_Int_RO_093(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_093) ENABLED START # noqa E509
        self.Int_RO_093 = random.randint(0, 100)
        return self.Int_RO_093
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_093

    def read_Int_RO_094(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_094) ENABLED START # noqa E509
        self.Int_RO_094 = random.randint(0, 100)
        return self.Int_RO_094
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_094

    def read_Int_RO_095(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_095) ENABLED START # noqa E509
        self.Int_RO_095 = random.randint(0, 100)
        return self.Int_RO_095
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_095

    def read_Int_RO_096(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_096) ENABLED START # noqa E509
        self.Int_RO_096 = random.randint(0, 100)
        return self.Int_RO_096
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_096

    def read_Int_RO_097(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_097) ENABLED START # noqa E509
        self.Int_RO_097 = random.randint(0, 100)
        return self.Int_RO_097
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_097

    def read_Int_RO_098(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_098) ENABLED START # noqa E509
        self.Int_RO_098 = random.randint(0, 100)
        return self.Int_RO_098
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_098

    def read_Int_RO_099(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_099) ENABLED START # noqa E509
        self.Int_RO_099 = random.randint(0, 100)
        return self.Int_RO_099
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_099

    def read_Int_RO_100(self):
        # PROTECTED REGION ID(TarantaTestDevice.Int_RO_100) ENABLED START # noqa E509
        self.Int_RO_100 = random.randint(0, 100)
        return self.Int_RO_100
        # PROTECTED REGION END #    //  TarantaTestDevice.Int_RO_100

    def read_DishState(self):
        # PROTECTED REGION ID(TarantaTestDevice.DishState_read) ENABLED START #
        if auto_dishState:
            self.DishState = random.randint(0, 10)
        return self.DishState
        # PROTECTED REGION END #    //  TarantaTestDevice.DishState_read

    def write_DishState(self, value):
        # PROTECTED REGION ID(TarantaTestDevice.DishState_write) ENABLED START # noqa E501
        self.DishState = value
        return self.DishState
        # PROTECTED REGION END #    //  TarantaTestDevice.DishState_write

    def read_routingTable(self):
        # PROTECTED REGION ID(TarantaTestDevice.routingTable_read) ENABLED START # noqa E501
        self.__routingTable = (
            """{ "routes": [ { "src": { "channel": """
            + str(random.randint(0, 100))
            + """ }
               , "dst": { "port": """
            + str(random.randint(0, 20))
            + """ } }
               , { "src": { "channel": """
            + str(random.randint(100, 500))
            + """ },
               "dst": { "port": """
            + str(random.randint(0, 30))
            + """ } } ] }"""
        )
        return self.__routingTable
        # PROTECTED REGION END #    //  TarantaTestDevice.routingTable_read

    def read_CspObsState(self):
        # PROTECTED REGION ID(TarantaTestDevice.CspObsState_read)
        # ENABLED START #
        if auto_obsState:
            self.CspObsState = random.randint(0, 6)
        return self.CspObsState
        # PROTECTED REGION END #
        # //  TarantaTestDevice.CspObsState_read

    def write_CspObsState(self, value):
        # PROTECTED REGION ID(TarantaTestDevice.CspObsState_write)
        # ENABLED START #
        pass
        # PROTECTED REGION END #
        # //  TarantaTestDevice.CspObsState_write

    def read_CbfObsState(self):
        # PROTECTED REGION ID(TarantaTestDevice.CbfObsState_read) ENABLED START # noqa E501
        if auto_obsState:
            self.CbfObsState = random.randint(0, 6)
        return self.CbfObsState
        # PROTECTED REGION END #    //  TarantaTestDevice.CbfObsState_read

    def write_CbfObsState(self, value):
        # PROTECTED REGION ID(TarantaTestDevice.CbfObsState_write) ENABLED START # noqa E501
        pass
        # PROTECTED REGION END #    //  TarantaTestDevice.CbfObsState_write

    def read_stringRW(self):
        # PROTECTED REGION ID(TarantaTestDevice.stringRW_read) ENABLED START # noqa E501
        return self.__stringRW
        # PROTECTED REGION END #    //  TarantaTestDevice.stringRW_read

    def write_stringRW(self, value):
        # PROTECTED REGION ID(TarantaTestDevice.stringRW_write) ENABLED START # noqa E501
        self.__stringRW = value
        # PROTECTED REGION END #    //  TarantaTestDevice.stringRW_write

    def read_stringR(self):
        # PROTECTED REGION ID(TarantaTestDevice.stringR_read) ENABLED START # noqa E501
        return self.__stringR
        # PROTECTED REGION END #    //  TarantaTestDevice.stringR_read

    def read_spectrum_att(self):
        # PROTECTED REGION ID(TarantaTestDevice.spectrum_att_read) ENABLED START # noqa E501
        a = np.array(random.random() * 100)

        for _ in range(1, 1024):
            a = np.append(a, random.random() * 100)

        self.spectrum_att = a
        return self.spectrum_att
        # PROTECTED REGION END #    //  TarantaTestDevice.spectrum_att_read

    # --------
    # Commands
    # --------

    @command(
        dtype_in="str",
        doc_in="JSON String describing one or more routing rules to add.",
        dtype_out="str",
    )
    @DebugIt()
    def AddRoutes(self, argin):
        # PROTECTED REGION ID(TarantaTestDevice.AddRoutes) ENABLED START #
        routes = json.loads(argin)["routes"]
        print(routes)
        return routes
        # PROTECTED REGION END #    //  TarantaTestDevice.AddRoutes

    @command(
        dtype_in="bool",
        doc_in="Get JSON",
        dtype_out="str",
        doc_out="Get JSON",
    )
    @DebugIt()
    def json(self, argin):
        # PROTECTED REGION ID(TarantaTestDevice.json) ENABLED START #
        jsonOut = {"foo": 19, "bar": {"baz": "Kimberly Robinson", "poo": 3.33}}
        logging.info(argin)
        print(json.dumps(jsonOut))
        return json.dumps(jsonOut)
        # PROTECTED REGION END #    //  TarantaTestDevice.json

    @command(
        dtype_in="bool",
        doc_in="Control led status",
        dtype_out="str",
        doc_out="Get server response",
    )
    @DebugIt()
    def led(self, argin):
        # PROTECTED REGION ID(TarantaTestDevice.led) ENABLED START #
        raise NotImplementedError()
        # PROTECTED REGION END #    //  TarantaTestDevice.led

    @command(
        dtype_in="bool",
        doc_in="Control ON/OFF state",
        dtype_out="str",
        doc_out="Get server response",
    )
    @DebugIt()
    def OnOff(self, argin):
        # PROTECTED REGION ID(TarantaTestDevice.ON_OFF) ENABLED START #
        if argin:
            self.set_state(DevState.ON)
        else:
            self.set_state(DevState.OFF)
        return str(argin)
        # PROTECTED REGION END #    //  TarantaTestDevice.ON_OFF

    @command(
        dtype_in="int16",
        doc_in="Control device state",
        dtype_out="str",
        doc_out="Get server response",
    )
    @DebugIt()
    def setDeviceState(self, argin):
        # PROTECTED REGION ID(TarantaTestDevice.deviceState) ENABLED START #
        self.set_state(DevState(argin))
        return str(argin)
        # PROTECTED REGION END #    //  TarantaTestDevice.deviceState

    @command(
        dtype_in="float",
        doc_in="Ramp target current",
        dtype_out="float",
        doc_out="target_current\nFalse otherwise",
    )
    @DebugIt()
    def ramp(self, argin):
        # PROTECTED REGION ID(TarantaTestDevice.ramp) ENABLED START #
        self.set_current(argin)
        return argin
        # PROTECTED REGION END #    //  TarantaTestDevice.ramp

    @command(
        dtype_in="bool",
        doc_in="Boolean type",
        dtype_out="str",
        doc_out="Return the type of input Arg",
    )
    @DebugIt()
    def testBoolean(self, argin):
        # PROTECTED REGION ID(TarantaTestDevice.testBoolean) ENABLED START #
        return str(argin)
        # PROTECTED REGION END #    //  TarantaTestDevice.testBoolean

    @command(
        dtype_in="int16",
        doc_in="Integer Type",
        dtype_out="str",
        doc_out="Return the type of input Arg",
    )
    @DebugIt()
    def testInt(self, argin):
        # PROTECTED REGION ID(TarantaTestDevice.testInt) ENABLED START #
        return str(type(argin)) + str(argin)
        # PROTECTED REGION END #    //  TarantaTestDevice.testInt

    @command(
        dtype_in="float",
        doc_in="Float Type",
        dtype_out="str",
        doc_out="Return the type of input Arg",
    )
    @DebugIt()
    def testFloat(self, argin):
        # PROTECTED REGION ID(TarantaTestDevice.testFloat) ENABLED START # noqa E501
        return str(type(argin)) + str(argin)
        # PROTECTED REGION END #    //  TarantaTestDevice.testFloat

    @command(
        dtype_in="str",
        doc_in="String Type",
        dtype_out="str",
        doc_out="Return the type of input Arg",
    )
    @DebugIt()
    def testStr(self, argin):
        # PROTECTED REGION ID(TarantaTestDevice.testStr) ENABLED START # noqa E501
        return str(type(argin)) + str(argin)
        # PROTECTED REGION END #    //  TarantaTestDevice.testStr

    @command(
        dtype_in="DevEnum",
        doc_in="Enum Type",
        dtype_out="str",
        doc_out="Return the type of input Arg",
    )
    @DebugIt()
    def testDevEnum(self, argin):
        # PROTECTED REGION ID(TarantaTestDevice.testDevEnum) ENABLED START # noqa E501
        return str(type(argin)) + str(argin)
        # PROTECTED REGION END #    //  TarantaTestDevice.testDevEnum

    @command(
        dtype_in=("char",),
        doc_in="VarCharArray Type",
        dtype_out="str",
        doc_out="Return the type of input Arg",
    )
    @DebugIt()
    def testDevVarCharArray(self, argin):
        # PROTECTED REGION ID(TarantaTestDevice.testDevVarCharArray) ENABLED START # noqa E501
        return str(type(argin)) + str(argin)
        # PROTECTED REGION END #    //  TarantaTestDevice.testDevVarCharArray

    @command(
        dtype_in=("int16",),
        doc_in="DevVarShortArray type",
        dtype_out="str",
        doc_out="Return the type of input Arg",
    )
    @DebugIt()
    def testDevVarShortArray(self, argin):
        # PROTECTED REGION ID(TarantaTestDevice.testDevVarShortArray) ENABLED START # noqa E501
        return str(type(argin)) + str(argin)
        # PROTECTED REGION END #    //  TarantaTestDevice.testDevVarShortArray

    @command(
        dtype_in=("int",),
        doc_in="DevVarLongArray type",
        dtype_out="str",
        doc_out="Return the type of input Arg",
    )
    @DebugIt()
    def testDevVarLongArray(self, argin):
        # PROTECTED REGION ID(TarantaTestDevice.testDevVarLongArray) ENABLED START # noqa E501
        return str(type(argin)) + str(argin)
        # PROTECTED REGION END #    //  TarantaTestDevice.testDevVarLongArray

    @command(
        dtype_in=("str",),
        doc_in="DevVarStringArray",
        dtype_out="str",
        doc_out="Return the type of input Arg",
    )
    @DebugIt()
    def testDevVarStringArray(self, argin):
        # PROTECTED REGION ID(TarantaTestDevice.testDevVarStringArray) ENABLED START # noqa E501
        return str(type(argin)) + str(argin)
        # PROTECTED REGION END #    //  TarantaTestDevice.testDevVarStringArray


# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(TarantaTestDevice.main) ENABLED START #
    return run((TarantaTestDevice,), args=args, **kwargs)
    # PROTECTED REGION END #    //  TarantaTestDevice.main


if __name__ == "__main__":
    main()
