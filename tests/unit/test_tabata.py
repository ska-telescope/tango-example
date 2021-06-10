# -*- coding: utf-8 -*-
"""
Some simple unit tests of the Tabata device, exercising the device from
the same host as the tests by using a DeviceTestContext.
"""
import logging
import tango
import pytest

from ska_tango_examples.DevFactory import DevFactory
from ska_tango_examples.tabata.AsyncTabata import AsyncTabata
from ska_tango_examples.tabata.Tabata import Tabata


@pytest.fixture()
def devices_to_load():
    return (
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
        proxy.work = -10
        proxy.rest = -30
        proxy.cycles = -2
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


@pytest.mark.xfail
def test_async_set_attr(tango_context):
    try:
        tango.set_green_mode(tango.GreenMode.Futures)
        logging.info("%s", tango_context)
        dev_factory = DevFactory()
        proxy = dev_factory.get_device("test/asynctabata/1")
        check_set_attr(proxy)
    finally:
        tango.set_green_mode(tango.GreenMode.Synchronous)
