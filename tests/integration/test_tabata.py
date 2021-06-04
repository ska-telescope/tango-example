# -*- coding: utf-8 -*-
"""
Some simple unit tests of the Tabata device, exercising the device from
the same host as the tests by using a DeviceTestContext.
"""
import logging
import time
import pytest
from tango import DevState
from tango.test_context import MultiDeviceTestContext

from ska_tango_examples.tabata.DevFactory import DevFactory
from ska_tango_examples.counter.PushCounter import PushCounter
from ska_tango_examples.tabata.Tabata import Tabata

devices_info = (
    {
        "class": PushCounter,
        "devices": [
            {"name": "test/counter/prepare"},
            {"name": "test/counter/work"},
            {"name": "test/counter/rest"},
            {"name": "test/counter/cycles"},
            {"name": "test/counter/tabatas"},
        ],
    },
    {
        "class": Tabata,
        "devices": [
            {
                "name": "test/tabata/1",
            },
        ],
    },
)


def test_tabata():
    with MultiDeviceTestContext(devices_info, process=False) as context:
        DevFactory._test_context = context
        dev_factory = DevFactory()
        proxy = context.get_device("test/tabata/1")
        assert proxy.prepare == 10
        assert proxy.work == 20
        assert proxy.rest == 10
        assert proxy.cycles == 8
        assert proxy.tabatas == 1
        proxy.prepare = 1
        proxy.work = 1
        proxy.rest = 1
        proxy.cycles = 1
        proxy.tabatas = 1
        proxy.ResetCounters()
        proxy.Start()
        assert proxy.State() == DevState.ON
        while not dev_factory.get_tabatas_counter().value == 0:
            time.sleep(1)
        logging.info(
            "%s %s %s %s %s",
            dev_factory.get_prepare_counter().value,
            dev_factory.get_work_counter().value,
            dev_factory.get_rest_counter().value,
            dev_factory.get_cycles_counter().value,
            dev_factory.get_tabatas_counter().value,
        )
        assert proxy.State() == DevState.OFF


def test_set_attr():
    with MultiDeviceTestContext(devices_info, process=False) as context:
        proxy = context.get_device("test/tabata/1")
        proxy.prepare = 5
        proxy.work = 40
        proxy.rest = 15
        proxy.cycles = 16
        proxy.tabatas = 2
        with pytest.raises(Exception):
            proxy.prepare = -10
            proxy.work = -10
            proxy.rest = -30
            proxy.cycles = -2
            proxy.tabatas = -2

        assert proxy.prepare == 5
        assert proxy.work == 40
        assert proxy.rest == 15
        assert proxy.cycles == 16
        assert proxy.tabatas == 2
