# -*- coding: utf-8 -*-
#
# This file is part of the EventReceiver project
#
# Matteo Di Carlo
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" EventReceiver

EventReceiver Training Example
"""

# PyTango imports
import tango
from ska_tango_base import SKABaseDevice

# Additional import
# PROTECTED REGION ID(EventReceiver.additionnal_import) ENABLED START #
import logging
from tango.server import DeviceMeta, attribute, run

from ska_tango_examples.DevFactory import DevFactory

# PROTECTED REGION END #    //  EventReceiver.additionnal_import

__all__ = ["EventReceiver", "main"]


class EventReceiver(SKABaseDevice):
    """
    EventReceiver Training Example
    """

    __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(EventReceiver.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  EventReceiver.class_variable

    # ----------
    # Attributes
    # ----------

    EventReceived = attribute(
        dtype="bool",
    )

    TestSpectrumType = attribute(
        dtype=("uint16",),
        max_dim_x=200,
    )

    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        super().init_device()
        # PROTECTED REGION ID(EventReceiver.init_device) ENABLED START #
        self.logger = logging.getLogger(__name__)
        self._dev_factory = DevFactory()
        self.dev = None
        self.attr_EventReceived = False
        # PROTECTED REGION END #    //  EventReceiver.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(EventReceiver.always_executed_hook)
        # ENABLED START #
        try:
            if self.dev is None:
                self.logger.info("Connect to motor device")
                self.dev = self._dev_factory.get_device("test/motor/1")
                self.attr_EventReceived = False
                self.logger.info("subscribe_event on PerformanceValue")
                self.dev.subscribe_event(
                    "PerformanceValue",
                    tango.EventType.CHANGE_EVENT,
                    self.HandleEvent,
                    stateless=True,
                )
        except Exception as ex:
            self.logger.info("Unexpected error: %s", str(ex))
        # PROTECTED REGION END #
        # //  EventReceiver.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(EventReceiver.delete_device) ENABLED START #
        pass
        # PROTECTED REGION END #    //  EventReceiver.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_EventReceived(self):
        # PROTECTED REGION ID(EventReceiver.EventReceived_read) ENABLED START #
        try:
            return self.attr_EventReceived
        except Exception as ex:
            self.logger.info(
                "Unexpected error on (self.attr_EventReceived = False): %s",
                str(ex),
            )
        # PROTECTED REGION END #    //  EventReceiver.EventReceived_read

    def read_TestSpectrumType(self):
        # PROTECTED REGION ID(EventReceiver.TestSpectrumType_read) ENABLED START # noqa: E501
        self.TestSpectrumType = [1, 2, 3]
        return self.TestSpectrumType
        # PROTECTED REGION END #    //  EventReceiver.TestSpectrumType_read

    # --------
    # Commands
    # --------

    def HandleEvent(self, args):
        try:
            self.logger.info(
                "Event arrived on PerformanceValue value= %s",
                str(self.dev.PerformanceValue),
            )
            self.logger.info("args = %s", str(args))
            self.attr_EventReceived = True
        except Exception as ex:
            self.logger.info(
                "Unexpected error on (self.attr_EventReceived = False): %s",
                str(ex),
            )


# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(EventReceiver.main) ENABLED START #
    # debugpy.listen(5678)
    return run((EventReceiver,), args=args, **kwargs)
    # PROTECTED REGION END #    //  EventReceiver.main


if __name__ == "__main__":
    main()
