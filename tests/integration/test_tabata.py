# -*- coding: utf-8 -*-
"""
Some simple unit tests of the Tabata device, exercising the device from
the same host as the tests by using a DeviceTestContext.
"""
import logging
import time

import pytest
import tango
from tango import DevState

from ska_tango_examples.counter.Counter import Counter
from ska_tango_examples.DevFactory import DevFactory
from ska_tango_examples.tabata.RunningState import RunningState
from ska_tango_examples.tabata.Tabata import Tabata

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
                    "properties": {"sleep_time": 0.01},
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
        if dev_state not in dev_states:
            logging.info("Device: %s %s", dev_state, run_state)
            dev_states.append(dev_state)
        if run_state not in run_states:
            logging.info("Device: %s %s", dev_state, run_state)
            run_states.append(run_state)
        elapsed_time = time.time() - start_time
        if elapsed_time > TIMEOUT:
            pytest.fail("Timeout occurred while executing the test")
        # to avoid the segmentation fault in simulation mode,
        # tests must run in less than 10ss
        # https://gitlab.com/tango-controls/cppTango/-/issues/843
        time.sleep(0.01)
    assert proxy.state() == DevState.OFF
    assert DevState.ON in dev_states
    assert RunningState.PREPARE in run_states
    assert RunningState.WORK in run_states
    assert RunningState.REST in run_states


@pytest.mark.post_deployment
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
    # proxy.set_timeout_millis(30000)
    setup_tabata(proxy)

    proxy.ResetCounters(wait=True)

    res = proxy.Run(wait=False, timeout=None)
    logging.info("%s", res)

    wait_for_events(proxy)

    assert proxy.State() == DevState.OFF
