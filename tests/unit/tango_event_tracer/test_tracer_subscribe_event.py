"""Tests for ::class::`TangoEventTracer` to ensure events are captured.

This second set of tests focuses on ensuring that ::class::`TangoEventTracer`
can subscribe to Tango events and capture them correctly. This is done by 
deploying a Tango device in a separate thread and then subscribing to its
events. The tests then check that the events are captured correctly.

Those tests are complementary to the ones in 
::file::`test_tango_event_tracer.py`, which cover the basic methods of the
`TangoEventTracer` class in isolation.
"""

import logging

import pytest

from ska_tango_examples.counter.Counter import Counter
from ska_tango_examples.DevFactory import DevFactory
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


def test_tabata_set_valutes_to_attributes(tango_context):
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

