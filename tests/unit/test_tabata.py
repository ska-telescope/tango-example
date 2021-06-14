# -*- coding: utf-8 -*-
"""
Some simple unit tests of the Tabata device, exercising the device from
the same host as the tests by using a DeviceTestContext.
"""
import logging
import tango
import pytest
import time

from ska_tango_examples.DevFactory import DevFactory
from ska_tango_examples.counter.Counter import Counter
from ska_tango_examples.tabata.AsyncTabata import AsyncTabata
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
            "class": AsyncTabata,
            "devices": [
                {
                    "name": "test/asynctabata/1",
                },
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


def check_set_attr(proxy):
    proxy.prepare = 5
    proxy.work = 40
    proxy.rest = 15
    proxy.cycles = 16
    proxy.tabatas = 2
    with pytest.raises(Exception):
        proxy.prepare = -10
    with pytest.raises(Exception):
        proxy.work = -10
    with pytest.raises(Exception):
        proxy.rest = -30
    with pytest.raises(Exception):
        proxy.cycles = -2
    with pytest.raises(Exception):
        proxy.tabatas = -2

    assert proxy.prepare == 5
    assert proxy.work == 40
    assert proxy.rest == 15
    assert proxy.cycles == 16
    assert proxy.tabatas == 2


def test_set_attr(tango_context):
    logging.info("%s", tango_context)
    dev_factory = DevFactory()
    proxy = dev_factory.get_device("test/tabata/1")
    check_set_attr(proxy)


@pytest.mark.post_deployment
def test_async_set_attr(tango_context):
    logging.info("%s", tango_context)
    dev_factory = DevFactory()
    proxy = dev_factory.get_device(
        "test/asynctabata/1", tango.GreenMode.Futures
    )
    check_set_attr(proxy)


@pytest.mark.post_deployment
def test_fatabata(tango_context):
    logging.info("%s", tango_context)
    dev_factory = DevFactory()
    tabata = dev_factory.get_device("test/tabata/1")
    tabata.ResetCounters()
    time.sleep(
        3
    )  # it takes time to propagate; forwarded attributes are not recommended.
    fatabata = dev_factory.get_device("test/fatabata/1")
    prepare = dev_factory.get_device("test/counter/prepare")
    work = dev_factory.get_device("test/counter/work")
    rest = dev_factory.get_device("test/counter/rest")
    cycles = dev_factory.get_device("test/counter/cycles")
    tabatas = dev_factory.get_device("test/counter/tabatas")

    assert fatabata.prepare == prepare.value
    assert fatabata.work == work.value
    assert fatabata.rest == rest.value
    assert fatabata.cycle == cycles.value
    assert fatabata.tabata == tabatas.value
