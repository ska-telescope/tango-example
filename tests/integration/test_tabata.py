# -*- coding: utf-8 -*-
"""
Some simple unit tests of the Tabata device, exercising the device from
the same host as the tests by using a DeviceTestContext.
"""
import logging
import time
import pytest
from tango import DevState

from ska_tango_examples.DevFactory import DevFactory
from ska_tango_examples.counter.Counter import Counter
from ska_tango_examples.tabata.Tabata import Tabata


@pytest.fixture()
def devices_to_load():
    return (
        {
            "class": Counter,
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


def test_tabata(tango_context):
    logging.info("%s", tango_context)
    dev_factory = DevFactory()
    proxy = dev_factory.get_device("test/tabata/1")
    proxy.prepare = 5
    proxy.work = 5
    proxy.rest = 5
    proxy.cycles = 1
    proxy.tabatas = 1
    proxy.ResetCounters()
    proxy.Start()
    assert proxy.State() == DevState.ON
    tabatasCounter = dev_factory.get_device("test/counter/tabatas")
    while not tabatasCounter.value == 0:
        logging.info("Device state %s", proxy.state())
        logging.info("Running state %s", proxy.running_state)
        time.sleep(1)

    assert proxy.State() == DevState.OFF


def test_set_attr(tango_context):
    logging.info("%s", tango_context)
    dev_factory = DevFactory()
    proxy = dev_factory.get_device("test/tabata/1")
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
