# -*- coding: utf-8 -*-
"""
Some simple unit tests of the Tabata device, exercising the device from
the same host as the tests by using a DeviceTestContext.
"""
import logging
import time

import pytest
import tango

from ska_tango_examples.basic_example.EventReceiver import EventReceiver
from ska_tango_examples.basic_example.Motor import Motor
from ska_tango_examples.basic_example.powersupply import PowerSupply
from ska_tango_examples.DevFactory import DevFactory


@pytest.fixture()
def devices_to_load():
    return (
        {
            "class": EventReceiver,
            "devices": [{"name": "test/eventreceiver/1"}],
        },
        {
            "class": Motor,
            "devices": [
                {
                    "name": "test/motor/1",
                },
            ],
        },
        {
            "class": PowerSupply,
            "devices": [
                {
                    "name": "test/powersupply/1",
                },
            ],
        },
    )


def test_event_received(tango_context):
    logging.info("%s", tango_context)
    dev_factory = DevFactory()
    event_receiver = dev_factory.get_device("test/eventreceiver/1")
    for i in range(30):
        time.sleep(1)
        logging.info("waiting for event %s", i)
        if event_receiver.read_attribute("EventReceived").value:
            break

    assert event_receiver.read_attribute("EventReceived").value is True


def test_type_spectrum(tango_context):
    logging.info("%s", tango_context)
    dev_factory = DevFactory()
    event_receiver = dev_factory.get_device("test/eventreceiver/1")
    logging.info("%s", event_receiver.read_attribute("TestSpectrumType").value)
    assert not isinstance(
        event_receiver.read_attribute("TestSpectrumType").value, tuple
    )


@pytest.mark.post_deployment
def test_volume(tango_context):
    logging.info("%s", tango_context)
    dev_factory = DevFactory()
    power_supply = dev_factory.get_device("test/powersupply/1")
    assert power_supply.check_volume()


@pytest.mark.post_deployment
def test_properties(tango_context):
    logging.info("%s", tango_context)
    dev_factory = DevFactory()
    power_supply_1 = dev_factory.get_device("test/powersupply/1")
    power_supply_2 = dev_factory.get_device("test/powersupply/2")

    assert power_supply_1.get_attribute_config("current").max_alarm == "9.5"
    assert power_supply_2.get_attribute_config("current").max_alarm == "9.0"

    def prop_val(props: dict[str, tango.StdStringVector]):
        """Convert property value from StdStringVector to Python list."""
        [value] = props.values()
        return list(value)

    assert prop_val(power_supply_1.get_property("aClassProperty")) == ["67.4", "123"]
    assert prop_val(power_supply_2.get_property("aClassProperty")) == ["20.0", "200.0"]
