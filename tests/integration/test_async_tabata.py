# -*- coding: utf-8 -*-
"""
Some simple unit tests of the Tabata device, exercising the device from
the same host as the tests by using a DeviceTestContext.
"""
import logging
import time
import pytest
from tango import DevState
import tango
from ska_tango_examples.DevFactory import DevFactory
from ska_tango_examples.counter.Counter import Counter
from ska_tango_examples.tabata.AsyncTabata import AsyncTabata


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
            "class": AsyncTabata,
            "devices": [
                {
                    "name": "test/asynctabata/1",
                },
            ],
        },
    )


def test_asynctabata_command_inout_asynch(tango_context):
    try:
        tango.set_green_mode(tango.GreenMode.Futures)
        logging.info("%s", tango_context)
        dev_factory = DevFactory()
        proxy = dev_factory.get_device("test/asynctabata/1")
        proxy.set_timeout_millis(30000)
        proxy.prepare = 5
        proxy.work = 5
        proxy.rest = 5
        proxy.cycles = 1
        proxy.tabatas = 1

        tabatasCounter = dev_factory.get_device("test/counter/tabatas")

        id = proxy.command_inout_asynch("ResetCounters")
        cmd_res = proxy.command_inout_reply(id, timeout=30000)
        logging.info("%s", cmd_res)

        assert tabatasCounter.value == proxy.tabatas

        id = proxy.command_inout_asynch("Run")
        # cmd_res = proxy.command_inout_reply(id, timeout=30000)
        # logging.info("%s", cmd_res)

        start_time = time.time()
        elapsed_time = 0

        while not tabatasCounter.value == 0 and elapsed_time < 30:
            logging.info("Device state %s", proxy.state())
            logging.info("Running state %s", proxy.running_state)
            elapsed_time = time.time() - start_time
            time.sleep(1)

        if elapsed_time > 30:
            pytest.fail("Timeout occurred while executing the test")

        assert proxy.State() == DevState.OFF
    finally:
        tango.set_green_mode(tango.GreenMode.Synchronous)


def test_asynctabata_futures(tango_context):
    try:
        tango.set_green_mode(tango.GreenMode.Futures)
        logging.info("%s", tango_context)
        dev_factory = DevFactory()
        proxy = dev_factory.get_device("test/asynctabata/1")
        proxy.set_timeout_millis(30000)
        proxy.prepare = 5
        proxy.work = 5
        proxy.rest = 5
        proxy.cycles = 1
        proxy.tabatas = 1
        proxy.ResetCounters(wait=True)

        tabatasCounter = dev_factory.get_device("test/counter/tabatas")
        assert tabatasCounter.value == proxy.tabatas

        res = proxy.Run(wait=False, timeout=None)
        while not res.done():

            time.sleep(1)

        start_time = time.time()
        elapsed_time = 0
        while not tabatasCounter.value == 0 and elapsed_time < 30:
            try:
                logging.info("Device state %s", proxy.state())
            except Exception as ex:
                logging.error("Called state() but %s", ex)

            try:
                logging.info("Running state %s", proxy.running_state)
            except Exception as ex:
                logging.error(
                    "Get running_state attribute but %s",
                    ex,
                )

            elapsed_time = time.time() - start_time
            time.sleep(1)

        if elapsed_time > 30:
            pytest.fail("Timeout occurred while executing the test")

        assert proxy.State() == DevState.OFF
    finally:
        tango.set_green_mode(tango.GreenMode.Synchronous)


def test_set_attr(tango_context):
    try:
        tango.set_green_mode(tango.GreenMode.Futures)
        logging.info("%s", tango_context)
        dev_factory = DevFactory()
        proxy = dev_factory.get_device("test/asynctabata/1")
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
    finally:
        tango.set_green_mode(tango.GreenMode.Synchronous)
