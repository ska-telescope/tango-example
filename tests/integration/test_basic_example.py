# -*- coding: utf-8 -*-
"""
Some simple unit tests of the Tabata device, exercising the device from
the same host as the tests by using a DeviceTestContext.
"""
import json
import logging
import time

import pytest

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

    # ps1 should have defaults, ps2 device overrides
    ps1_properties = json.loads(power_supply_1.get_properties())
    ps2_properties = json.loads(power_supply_2.get_properties())

    # check class property has the value set via Helm, not its default_value
    assert ps1_properties["telmodel_source"] == "ska-tango-examples"
    assert ps2_properties["telmodel_source"] == "ska-tango-examples"

    # ps1 should have poll_rate's default_value, ps2 set via Helm values
    assert ps1_properties["poll_rate"] == 1.0
    assert ps2_properties["poll_rate"] == 2.5


@pytest.mark.post_deployment
def test_attribute_properties(tango_context):
    logging.info("%s", tango_context)
    dev_factory = DevFactory()
    power_supply_1 = dev_factory.get_device("test/powersupply/1")
    power_supply_2 = dev_factory.get_device("test/powersupply/2")

    assert power_supply_1.get_attribute_config("current").max_alarm == "9.5"
    assert power_supply_2.get_attribute_config("current").max_alarm == "9.0"

    assert power_supply_1.get_attribute_config("current").description == (
        "a templated attribute property: ska-tango-examples"
    )
    assert power_supply_2.get_attribute_config("current").description == (
        "the power supply current"
    )
