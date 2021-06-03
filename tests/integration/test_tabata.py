# -*- coding: utf-8 -*-
"""
Some simple unit tests of the Tabata device, exercising the device from
the same host as the tests by using a DeviceTestContext.
"""
import logging
from unittest.mock import patch
from tango import DevState
from tango.test_context import MultiDeviceTestContext

import ska_tango_examples.tabata.DevFactory
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


@patch.object(
    ska_tango_examples.tabata.DevFactory.DevFactory, "get_prepare_counter"
)
@patch.object(
    ska_tango_examples.tabata.DevFactory.DevFactory, "get_work_counter"
)
@patch.object(
    ska_tango_examples.tabata.DevFactory.DevFactory, "get_rest_counter"
)
@patch.object(
    ska_tango_examples.tabata.DevFactory.DevFactory, "get_cycles_counter"
)
@patch.object(
    ska_tango_examples.tabata.DevFactory.DevFactory, "get_tabatas_counter"
)
def test_tabata(
    get_prepare_counter,
    get_work_counter,
    get_rest_counter,
    get_cycles_counter,
    get_tabatas_counter,
):
    with MultiDeviceTestContext(devices_info, process=False) as context:
        get_prepare_counter.return_value = context.get_device(
            "test/counter/prepare"
        )
        get_work_counter.return_value = context.get_device("test/counter/work")
        get_rest_counter.return_value = context.get_device("test/counter/rest")
        get_cycles_counter.return_value = context.get_device(
            "test/counter/cycles"
        )
        get_tabatas_counter.return_value = context.get_device(
            "test/counter/tabatas"
        )
        import debugpy; debugpy.debug_this_thread()
        proxy = context.get_device("test/tabata/1")
        assert proxy.prepare == 10
        assert proxy.work == 20
        assert proxy.rest == 10
        assert proxy.cycles == 8
        assert proxy.tabatas == 1
        proxy.ResetCounters()
        get_prepare_counter.assert_called()
        get_work_counter.assert_called()
        get_rest_counter.assert_called()
        get_cycles_counter.assert_called()
        get_tabatas_counter.assert_called()
        proxy.Start()
        assert proxy.State() == DevState.ON
        proxy.Step()
        logging.info(
            "%s %s %s %s %s",
            context.get_device("test/counter/prepare").value,
            context.get_device("test/counter/work").value,
            context.get_device("test/counter/rest").value,
            context.get_device("test/counter/cycles").value,
            context.get_device("test/counter/tabatas").value,
        )
        assert proxy.State() == DevState.ON
        proxy.Stop()
        assert proxy.State() == DevState.OFF
        proxy.ResetCounters()
        assert proxy.State() == DevState.OFF


def test_set_attr():
    with MultiDeviceTestContext(devices_info, process=False) as context:
        proxy = context.get_device("test/tabata/1")
        proxy.prepare = 5
        try:
            proxy.prepare = -10
        except Exception as ex:
            logging.error(str(ex))
        proxy.work = 40
        try:
            proxy.work = -10
        except Exception as ex:
            logging.error(str(ex))
        proxy.rest = 15
        try:
            proxy.rest = 30
        except Exception as ex:
            logging.error(str(ex))
        proxy.cycles = 16
        try:
            proxy.cycles = 2
        except Exception as ex:
            logging.error(str(ex))
        proxy.tabatas = 2
        try:
            proxy.rest = -1
        except Exception as ex:
            logging.error(str(ex))
        assert proxy.prepare == 5
        assert proxy.work == 40
        assert proxy.rest == 15
        assert proxy.cycles == 16
        assert proxy.tabatas == 2
