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
import random
import threading
import time
from datetime import datetime, timedelta

import numpy as np
import tango
from tango import AttrWriteType, DebugIt, DevFailed, DevState
from tango.server import Device, DeviceMeta, attribute, command, run

auto_dishState = True
auto_obsState = True

__all__ = ["TarantaTestDevice", "main"]


class TarantaTestDevice(Device):
    """TarantaTestDevice Tango Device Server"""

    __metaclass__ = DeviceMeta

    # Define Int_RO attribute names
    INT_RO_ATTRIBUTES = ["Int_RO_{:03d}".format(i) for i in range(1, 101)]

    # ----------
    # Attributes
    # ----------

    RandomAttr = attribute(
        dtype="double",
    )

    # DishState
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

    processorInfo = attribute(
        dtype="str",
        label="Processor INFO",
        doc="JSON String encoding the processor info and temperature",
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

    assigned_receptor = attribute(
        dtype=("int",),
        max_dim_x=16,
    )

    EventsSpeed = attribute(
        dtype="float",
        access=AttrWriteType.READ_WRITE,
        unit="ms",
        doc="Controls the time interval (in milliseconds) at which events are sent",
    )

    # New attributes
    Health = attribute(
        dtype="DevEnum",
        access=AttrWriteType.READ_WRITE,
        enum_labels=["OK", "DEGRADED", "FAILED", "UNKNOWN"],
    )

    AdminMode = attribute(
        dtype="DevEnum",
        access=AttrWriteType.READ_WRITE,
        enum_labels=["ONLINE", "OFFLINE"],
    )

    Serial = attribute(
        dtype="str",
    )

    Temperature = attribute(
        dtype="float",
        unit="°C",
    )

    Power = attribute(
        dtype="float",
        unit="W",
    )

    Firmware = attribute(
        dtype="str",
    )

    Subarrays = attribute(
        dtype=("int",),
        max_dim_x=10,
    )

    Beams = attribute(
        dtype=("int",),
        max_dim_x=10,
    )

    Delays = attribute(
        dtype=("float",),
        unit="ms",
        max_dim_x=10,
    )

    LastUpdate = attribute(
        dtype="str",
    )

    ValidUntil = attribute(
        dtype="str",
    )

    TimeUp = attribute(
        dtype="int",
        unit="s",
    )

    FromSPS = attribute(
        dtype="str",
    )

    FromPTP = attribute(
        dtype="str",
    )

    StatsMode = attribute(
        dtype="str",
    )

    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        super().init_device()

        # Initialize values for attributes
        self._int_ro_values = {name: "" for name in self.INT_RO_ATTRIBUTES}

        # Add dynamic attributes
        for attr_name in self.INT_RO_ATTRIBUTES:
            attr = tango.Attr(
                attr_name, tango.DevString, tango.AttrWriteType.READ
            )
            self.add_attribute(attr, self.read_int_ro_attribute)

        # Set change events for Int_RO attributes
        for attr_name in self.INT_RO_ATTRIBUTES:
            self.set_change_event(attr_name, True, False)

        # Set change events for other attributes
        self.set_change_event("RandomAttr", True, False)
        self.set_change_event("DishState", True, False)
        self.set_change_event("Subarrays", True, False)
        self.set_change_event("Beams", True, False)
        self.set_change_event("CspObsState", True, False)
        self.set_change_event("CbfObsState", True, False)
        self.set_change_event("spectrum_att", True, False)
        self.set_change_event("assigned_receptor", True, False)
        self.set_change_event("Health", True, False)
        self.set_change_event("EventsSpeed", True, False)

        # Initialize attributes
        self.__stringRW = "stringRW"
        self.__stringR = "stringR"
        self.__processorInfo = (
            '{ "name": "Configuration Processor '
            + str(random.randint(1, 16))
            + '", "temperature": '
            + str(random.random() * 100)
            + ', "SerialNumber": "S/N:'
            + "{:016d}".format(random.randint(0, 10**16 - 1))
            + '" }'
        )

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
        self.set_state(DevState.STANDBY)

        # Initialize new attributes
        self.__admin_mode = 0  # 'ONLINE'
        self.__serial = "XFL1RCFEG244"
        self.__firmware = "vis:0.0.8"
        self.__delays = [15.0, 20.0]
        self.__start_time = time.time()
        self.__time_up = 0
        self.__subarrays = [1, 2, 3]
        self.__beams = [3, 8]
        self.__stats_mode = json.dumps(
            {
                "ready": False,
                "firmware": "vis:0.0.9",
                "fw_version": "vis:0.0.8",
            }
        )

        self._dish_state_value = 0
        self._random_attr_value = 0.0
        self._csp_obs_state_value = 0
        self._cbf_obs_state_value = 0
        self._spectrum_att_value = np.zeros(1024)
        self._assigned_receptor_value = np.zeros(16, dtype=np.uint16)
        self._events_speed = 1000.0  # default value in milliseconds

        self._health_state = 0  # 'OK'

        # Locks for thread safety
        self._events_speed_lock = threading.Lock()
        self._health_lock = threading.Lock()

        # Start thread to collect updates
        self._stop_update_event_thread = False
        self._update_event_thread = threading.Thread(
            target=self._collect_updates
        )
        self._update_event_thread.daemon = True
        self._update_event_thread.start()

    def delete_device(self):
        self._stop_update_event_thread = True
        if self._update_event_thread.is_alive():
            self._update_event_thread.join()
        super().delete_device()

    # ------------------
    # Attributes methods
    # ------------------

    # RandomAttr
    def read_RandomAttr(self):
        return self._random_attr_value

    # DishState
    def read_DishState(self):
        return self._dish_state_value

    def write_DishState(self, value):
        self._dish_state_value = value

    # processorInfo
    def read_processorInfo(self):
        return self.__processorInfo

    # routingTable
    def read_routingTable(self):
        return self.__routingTable

    # CspObsState
    def read_CspObsState(self):
        return self._csp_obs_state_value

    def write_CspObsState(self, value):
        self._csp_obs_state_value = value

    # CbfObsState
    def read_CbfObsState(self):
        return self._cbf_obs_state_value

    def write_CbfObsState(self, value):
        self._cbf_obs_state_value = value

    # stringRW
    def read_stringRW(self):
        return self.__stringRW

    def write_stringRW(self, value):
        self.__stringRW = value

    # stringR
    def read_stringR(self):
        return self.__stringR

    # spectrum_att
    def read_spectrum_att(self):
        return self._spectrum_att_value

    # assigned_receptor
    def read_assigned_receptor(self):
        return self._assigned_receptor_value

    # EventsSpeed
    def read_EventsSpeed(self):
        with self._events_speed_lock:
            return self._events_speed

    def write_EventsSpeed(self, value):
        with self._events_speed_lock:
            self._events_speed = value

    # Health
    def read_Health(self):
        with self._health_lock:
            return self._health_state

    def write_Health(self, value):
        with self._health_lock:
            self._health_state = value

    # New attribute methods

    def read_AdminMode(self):
        return self.__admin_mode

    def write_AdminMode(self, value):
        self.__admin_mode = value

    def read_Serial(self):
        return self.__serial

    def read_Temperature(self):
        self.__temperature = random.uniform(30, 70)
        return self.__temperature

    def read_Power(self):
        self.__power = random.uniform(10, 100)
        return self.__power

    def read_Firmware(self):
        return self.__firmware

    def read_Subarrays(self):
        return self.__subarrays

    def read_Beams(self):
        return self.__beams

    def read_Delays(self):
        return self.__delays

    def read_LastUpdate(self):
        self.__last_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return self.__last_update

    def read_ValidUntil(self):
        valid_until = datetime.now() + timedelta(minutes=5)
        self.__valid_until = valid_until.strftime("%Y-%m-%d %H:%M:%S")
        return self.__valid_until

    def read_TimeUp(self):
        self.__time_up = int(time.time() - self.__start_time)
        return self.__time_up

    def read_FromSPS(self):
        from_sps = datetime.now() + timedelta(minutes=2)
        self.__from_sps = from_sps.strftime("%Y-%m-%d %H:%M:%S")
        return self.__from_sps

    def read_FromPTP(self):
        from_ptp = datetime.now() + timedelta(minutes=2)
        self.__from_ptp = from_ptp.strftime("%Y-%m-%d %H:%M:%S")
        return self.__from_ptp

    def read_StatsMode(self):
        return self.__stats_mode

    # Dynamic attribute read method
    def read_int_ro_attribute(self, attr):
        attr_name = attr.get_name()
        value = self._int_ro_values.get(attr_name, "")
        attr.set_value(value)

    # Update events for attributes
    def _collect_updates(self):
        while not self._stop_update_event_thread:
            try:
                # Update Subarrays
                self.__subarrays = random.sample(
                    range(1, 10), random.randint(1, 3)
                )
                self.push_change_event("Subarrays", self.__subarrays)
                time.sleep(0.01)

                # Update Beams
                self.__beams = random.sample(
                    range(1, 10), random.randint(1, 5)
                )
                self.push_change_event("Beams", self.__beams)
                time.sleep(0.01)

                # Update RandomAttr
                self._random_attr_value = random.random() * 100
                self.push_change_event("RandomAttr", self._random_attr_value)
                time.sleep(0.01)

                # Update Int_RO_* attributes
                for attr_name in self.INT_RO_ATTRIBUTES:
                    value = (
                        str(random.randint(0, 100))
                        + " @"
                        + str(datetime.now())
                    )
                    self._int_ro_values[attr_name] = value
                    self.push_change_event(attr_name, value)
                    time.sleep(
                        0.001
                    )  # Short sleep to avoid overwhelming the system

                # Update DishState
                if auto_dishState:
                    self._dish_state_value = random.randint(0, 6)
                    self.push_change_event("DishState", self._dish_state_value)
                    time.sleep(0.01)

                # Update CspObsState
                if auto_obsState:
                    self._csp_obs_state_value = random.randint(0, 10)
                    self.push_change_event(
                        "CspObsState", self._csp_obs_state_value
                    )
                    time.sleep(0.01)

                # Update CbfObsState
                if auto_obsState:
                    self._cbf_obs_state_value = random.randint(0, 10)
                    self.push_change_event(
                        "CbfObsState", self._cbf_obs_state_value
                    )
                    time.sleep(0.01)

                # Update spectrum_att
                self._spectrum_att_value = np.random.rand(1024) * 100
                self.push_change_event(
                    "spectrum_att", self._spectrum_att_value
                )
                time.sleep(0.01)

                # Update assigned_receptor
                num_elements = random.randint(1, 16)
                values = random.sample(range(1, 17), num_elements)
                values.sort()
                self._assigned_receptor_value = np.array(
                    values, dtype=np.uint16
                )
                self.push_change_event(
                    "assigned_receptor", self._assigned_receptor_value
                )
                time.sleep(0.01)

                # Update Health
                with self._health_lock:
                    self._health_state = random.randint(
                        0, 3
                    )  # Randomly choose between 0, 1, and 3
                    self.push_change_event("Health", self._health_state)
                time.sleep(0.01)

                # Sleep for the specified events speed
                with self._events_speed_lock:
                    sleep_time = self._events_speed / 1000.0
                time.sleep(sleep_time)
            except DevFailed as e:
                self.error_stream("Error in _collect_updates: {}".format(e))
                time.sleep(1)  # Sleep briefly before retrying
            except Exception as e:
                self.error_stream(
                    "Unexpected error in _collect_updates: {}".format(e)
                )
                time.sleep(1)  # Sleep briefly before retrying

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
        routes = json.loads(argin)["routes"]
        print(routes)
        return json.dumps(routes)

    @command(
        dtype_in="bool",
        doc_in="Get JSON",
        dtype_out="str",
        doc_out="Get JSON",
    )
    @DebugIt()
    def json(self, argin):
        jsonOut = {"foo": 19, "bar": {"baz": "Kimberly Robinson", "poo": 3.33}}
        logging.info(argin)
        print(json.dumps(jsonOut))
        return json.dumps(jsonOut)

    @command(
        dtype_in="bool",
        doc_in="Control led status",
        dtype_out="str",
        doc_out="Get server response",
    )
    @DebugIt()
    def led(self, argin):
        raise NotImplementedError()

    @command(
        dtype_in="bool",
        doc_in="Control ON/OFF state",
        dtype_out="str",
        doc_out="Get server response",
    )
    @DebugIt()
    def OnOff(self, argin):
        if argin:
            self.set_state(DevState.ON)
        else:
            self.set_state(DevState.OFF)
        return str(argin)

    @command(
        dtype_in="int16",
        doc_in="Control device state",
        dtype_out="str",
        doc_out="Get server response",
    )
    @DebugIt()
    def setDeviceState(self, argin):
        self.set_state(DevState(argin))
        return str(argin)

    @command(
        dtype_in="float",
        doc_in="Ramp target current",
        dtype_out="float",
        doc_out="target_current\nFalse otherwise",
    )
    @DebugIt()
    def ramp(self, argin):
        # Assuming set_current is defined elsewhere
        # self.set_current(argin)
        return argin

    @command(
        dtype_in="bool",
        doc_in="Boolean type",
        dtype_out="str",
        doc_out="Return the type of input Arg",
    )
    @DebugIt()
    def testBoolean(self, argin):
        return str(argin)

    @command(
        dtype_in="int16",
        doc_in="Integer Type",
        dtype_out="str",
        doc_out="Return the type of input Arg",
    )
    @DebugIt()
    def testInt(self, argin):
        return str(type(argin)) + str(argin)

    @command(
        dtype_in="float",
        doc_in="Float Type",
        dtype_out="str",
        doc_out="Return the type of input Arg",
    )
    @DebugIt()
    def testFloat(self, argin):
        return str(type(argin)) + str(argin)

    @command(
        dtype_in="str",
        doc_in="String Type",
        dtype_out="str",
        doc_out="Return the type of input Arg",
    )
    @DebugIt()
    def testStr(self, argin):
        return str(type(argin)) + str(argin)

    @command(
        dtype_in="DevEnum",
        doc_in="Enum Type",
        dtype_out="str",
        doc_out="Return the type of input Arg",
    )
    @DebugIt()
    def testDevEnum(self, argin):
        return str(type(argin)) + str(argin)

    @command(
        dtype_in=("char",),
        doc_in="VarCharArray Type",
        dtype_out="str",
        doc_out="Return the type of input Arg",
    )
    @DebugIt()
    def testDevVarCharArray(self, argin):
        return str(type(argin)) + str(argin)

    @command(
        dtype_in=("int16",),
        doc_in="DevVarShortArray type",
        dtype_out="str",
        doc_out="Return the type of input Arg",
    )
    @DebugIt()
    def testDevVarShortArray(self, argin):
        return str(type(argin)) + str(argin)

    @command(
        dtype_in=("int",),
        doc_in="DevVarLongArray type",
        dtype_out="str",
        doc_out="Return the type of input Arg",
    )
    @DebugIt()
    def testDevVarLongArray(self, argin):
        return str(type(argin)) + str(argin)

    @command(
        dtype_in=("str",),
        doc_in="DevVarStringArray",
        dtype_out="str",
        doc_out="Return the type of input Arg",
    )
    @DebugIt()
    def testDevVarStringArray(self, argin):
        return str(type(argin)) + str(argin)


# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    return run((TarantaTestDevice,), args=args, **kwargs)


if __name__ == "__main__":
    main()
