# -*- coding: utf-8 -*-
"""
Some simple unit tests of the Tabata device, exercising the device from
the same host as the tests by using a DeviceTestContext.
"""
import logging
import tango
import time
from tango import DevState


def test_tabata():
    proxy = tango.DeviceProxy("test/tabata/1")
    assert proxy.prepare == 10
    assert proxy.work == 20
    assert proxy.rest == 10
    assert proxy.cycles == 8
    assert proxy.tabatas == 1
    proxy.ResetCounters()
    proxy.Start()
    assert proxy.State() == DevState.ON
    time.sleep(25)
    logging.info(
        "%s %s %s %s %s",
        tango.DeviceProxy("test/counter/prepare").value,
        tango.DeviceProxy("test/counter/work").value,
        tango.DeviceProxy("test/counter/rest").value,
        tango.DeviceProxy("test/counter/cycles").value,
        tango.DeviceProxy("test/counter/tabatas").value,
    )
    assert proxy.State() == DevState.ON
    proxy.Stop()
    assert proxy.State() == DevState.OFF
    proxy.ResetCounters()
    assert proxy.State() == DevState.OFF
