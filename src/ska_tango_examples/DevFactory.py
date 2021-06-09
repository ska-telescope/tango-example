import logging
import tango


class DevFactory:
    """
    This class is an easy attempt to develop the concept developed by MCCS team 
    in the repository https://gitlab.com/ska-telescope/ska-low-mccs/

    It is a singleton class and a factory which provide the ability for other 
    devices to create an object of type DeviceProxy.

    When testing the static variable _test_context is an instance of 
    the TANGO class MultiDeviceTestContext.

    More information on tango testing can be found at the following link:
    https://pytango.readthedocs.io/en/stable/testing.html

    """

    _test_context = None
    __instance = None

    def __new__(cls):
        if DevFactory.__instance is None:
            DevFactory.__instance = object.__new__(cls)
            DevFactory.__instance._dev_proxys = {}
        return DevFactory.__instance

    
    def get_device(self, fqnm):
        """
        Create (if not done before) a DeviceProxy for the Device fqnm

        :param fqnm: Fully qualified name for a device

        :return: DeviceProxy
        """
        if DevFactory._test_context is None:
            if fqnm not in self._dev_proxys:
                logging.info("Creating Proxy for %s", fqnm)
                self._dev_proxys[fqnm] = tango.DeviceProxy(fqnm)
            return self._dev_proxys[fqnm]
        else:
            return DevFactory._test_context.get_device(fqnm)

    def get_dev_from_property(self, dev, prop):
        """
        Create (if not done before) a DeviceProxy for the Device with
        name present in a device propery named prop

        :param dev: a tango server Device object
        :param prop: string representing the name of the property

        :return: DeviceProxy
        """
        db = tango.Database()
        try:
            return self.get_device(
                db.get_device_property(dev.get_name(), prop)[prop][0]
            )
        except Exception as ex:
            logging.error("%s", ex)
            raise ex
