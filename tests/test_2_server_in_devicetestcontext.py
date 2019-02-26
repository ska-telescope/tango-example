# -*- coding: utf-8 -*-
"""
Some simple unit tests of the PowerSupply device, exercising the device from
the same host as the tests by using a DeviceTestContext.
"""
from tango import DevState
from tango.test_utils import DeviceTestContext

from NewMotor.NewMotor import NewMotor


def test_init():
    """Test device goes into STANDBY when initialised"""
    with DeviceTestContext(NewMotor, process=True) as proxy:
        proxy.Init()
        assert proxy.state() == DevState.UNKNOWN


def test_start():
    """Test device goes into STANDBY when initialised"""
    with DeviceTestContext(NewMotor, process=True) as proxy:
        proxy.Start()
        assert proxy.state() == DevState.RUNNING
