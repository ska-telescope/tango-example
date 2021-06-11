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

    def __init__(self):
        self.dev_proxys = {}
        self.logger = logging.getLogger(__name__)

    def get_device(self, fqnm, green_mode=tango.GreenMode.Synchronous):
        """
        Create (if not done before) a DeviceProxy for the Device fqnm

        :param fqnm: Fully qualified name for a device
        :param green_mode: tango.GreenMode

        :return: DeviceProxy
        """
        if DevFactory._test_context is None:
            if fqnm not in self.dev_proxys:
                self.logger.info("Creating Proxy for %s", fqnm)
                self.dev_proxys[fqnm] = tango.DeviceProxy(
                    fqnm, green_mode=green_mode
                )
            return self.dev_proxys[fqnm]
        else:
            return DevFactory._test_context.get_device(fqnm)
