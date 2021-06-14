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
from ska_tango_examples.tabata.AsyncTabata import AsyncTabata, Running_state

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
                {"name": "test/tabata/1", "properties": {"sleep_time": "0.1"}},
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
    dev_states = []
    run_states = []
    start_time = time.time()
    while not tabatasCounter.value <= 0 or proxy.State() == DevState.ON:
        dev_state = proxy.state()
        run_state = proxy.running_state
        logging.info("Device state %s", dev_state)
        logging.info("Running state %s", run_state)
        if dev_state not in dev_states:
            dev_states.append(dev_state)
        if run_state not in run_states:
            run_states.append(run_state)
        elapsed_time = time.time() - start_time
        if elapsed_time > TIMEOUT:
            pytest.fail("Timeout occurred while executing the test")
        # to avoid the segmentation fault in simulation mode,
        # tests must run in less than 10ss
        # https://gitlab.com/tango-controls/cppTango/-/issues/843
        if DevFactory._test_context is not None:
            time.sleep(0.1)
        else:
            time.sleep(1)
    assert proxy.state() == DevState.OFF
    assert DevState.ON in dev_states
    assert Running_state.PREPARE in run_states
    assert Running_state.WORK in run_states
    assert Running_state.REST in run_states


def test_sync_tabata(tango_context):
    logging.info("%s", tango_context)
    dev_factory = DevFactory()
    proxy = dev_factory.get_device("test/tabata/1")
    setup_tabata(proxy)
    proxy.ResetCounters()
    proxy.Start()
    with pytest.raises(Exception):
        proxy.Start()
    assert proxy.State() == DevState.ON
    wait_for_events(proxy)
    assert proxy.State() == DevState.OFF


@pytest.mark.post_deployment
def test_async_tabata_command_inout_asynch(tango_context):
    logging.info("%s", tango_context)
    dev_factory = DevFactory()
    proxy = dev_factory.get_device("test/asynctabata/1")
    proxy.set_timeout_millis(3000)
    setup_tabata(proxy)

    cmd_id = proxy.command_inout_asynch("ResetCounters")
    cmd_res = proxy.command_inout_reply(cmd_id, timeout=3000)
    logging.info("%s", cmd_res)

    proxy.command_inout_asynch("Run")
    wait_for_events(proxy)

    assert proxy.State() == DevState.OFF


@pytest.mark.post_deployment
def test_async_tabata_futures(tango_context):
    logging.info("%s", tango_context)
    dev_factory = DevFactory()
    proxy = dev_factory.get_device(
        "test/asynctabata/1", tango.GreenMode.Futures
    )
    proxy.set_timeout_millis(30000)
    setup_tabata(proxy)

    proxy.ResetCounters(wait=True)

    res = proxy.Run(wait=False, timeout=None)
    logging.info("%s", res)

    wait_for_events(proxy)

    assert proxy.State() == DevState.OFF
