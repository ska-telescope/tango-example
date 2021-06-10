# -*- coding: utf-8 -*-
"""
Some simple unit tests of the Tabata device, exercising the device from
the same host as the tests by using a DeviceTestContext.
"""
import logging
import time
import tango
import pytest
from tango import DevState

from ska_tango_examples.DevFactory import DevFactory
from ska_tango_examples.counter.Counter import Counter
from ska_tango_examples.tabata.Tabata import Tabata
from ska_tango_examples.tabata.AsyncTabata import AsyncTabata

TIMEOUT = 60


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
        {
            "class": AsyncTabata,
            "devices": [
                {
                    "name": "test/asynctabata/1",
                },
            ],
        },
    )


def setup_tabata(proxy):
    proxy.prepare = 5
    proxy.work = 5
    proxy.rest = 5
    proxy.cycles = 1
    proxy.tabatas = 1


def wait_for_events(proxy):
    dev_factory = DevFactory()
    tabatasCounter = dev_factory.get_device("test/counter/tabatas")
    start_time = time.time()
    while not tabatasCounter.value <= 0 and proxy.State() == DevState.ON:
        logging.info("Device state %s", proxy.state())
        logging.info("Running state %s", proxy.running_state)
        elapsed_time = time.time() - start_time
        if elapsed_time > TIMEOUT:
            pytest.fail("Timeout occurred while executing the test")
        time.sleep(1)


def test_sync_tabata(tango_context):
    logging.info("%s", tango_context)
    dev_factory = DevFactory()
    proxy = dev_factory.get_device("test/tabata/1")
    setup_tabata(proxy)
    proxy.ResetCounters()
    proxy.Start()
    assert proxy.State() == DevState.ON
    wait_for_events(proxy)
    assert proxy.State() == DevState.OFF


@pytest.mark.xfail
def test_async_tabata_command_inout_asynch(tango_context):
    try:
        tango.set_green_mode(tango.GreenMode.Futures)
        logging.info("%s", tango_context)
        dev_factory = DevFactory()
        proxy = dev_factory.get_device("test/asynctabata/1")
        proxy.set_timeout_millis(30000)
        setup_tabata(proxy)

        id = proxy.command_inout_asynch("ResetCounters")
        cmd_res = proxy.command_inout_reply(id, timeout=30000)
        logging.info("%s", cmd_res)

        id = proxy.command_inout_asynch("Run")
        wait_for_events(proxy)

        assert proxy.State() == DevState.OFF
    finally:
        tango.set_green_mode(tango.GreenMode.Synchronous)


@pytest.mark.xfail
def test_async_tabata_futures(tango_context):
    try:
        tango.set_green_mode(tango.GreenMode.Futures)
        logging.info("%s", tango_context)
        dev_factory = DevFactory()
        proxy = dev_factory.get_device("test/asynctabata/1")
        proxy.set_timeout_millis(30000)
        setup_tabata(proxy)

        proxy.ResetCounters(wait=True)

        res = proxy.Run(wait=False, timeout=None)
        logging.info("%s", res)

        wait_for_events(proxy)

        assert proxy.State() == DevState.OFF
    finally:
        tango.set_green_mode(tango.GreenMode.Synchronous)
