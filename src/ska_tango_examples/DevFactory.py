import logging

import tango


class DevFactory:
    """
    This class is an easy attempt to develop the concept developed by MCCS team
    in the repository https://gitlab.com/ska-telescope/ska-low-mccs/

    It is a factory class which provide the ability to create an object of
    type DeviceProxy.

    When testing the static variable _test_context is an instance of
    the TANGO class MultiDeviceTestContext.

    More information on tango testing can be found at the following link:
    https://pytango.readthedocs.io/en/stable/testing.html

    """

    _test_context = None

    def __init__(self, green_mode=tango.GreenMode.Synchronous):
        self.dev_proxys = {}
        self.logger = logging.getLogger(__name__)
        self.default_green_mode = green_mode

    def get_device(self, dev_name, green_mode=None):
        """
        Create (if not done before) a DeviceProxy for the Device fqnm

        :param dev_name: Device name
        :param green_mode: tango.GreenMode (synchronous by default)

        :return: DeviceProxy
        """
        if green_mode is None:
            green_mode = self.default_green_mode

        if DevFactory._test_context is None:
            if dev_name not in self.dev_proxys:
                self.logger.info("Creating Proxy for %s", dev_name)
                self.dev_proxys[dev_name] = tango.DeviceProxy(
                    dev_name, green_mode=green_mode
                )
            return self.dev_proxys[dev_name]
        else:
            return DevFactory._test_context.get_device(dev_name)
