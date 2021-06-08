import tango


class DevFactory:
    _test_context = None
    __instance = None

    def __new__(cls):
        if DevFactory.__instance is None:
            DevFactory.__instance = object.__new__(cls)
            DevFactory.__instance._dev_proxys = {}
        return DevFactory.__instance

    def get_device(self, fqnm):
        if DevFactory._test_context is None:
            if fqnm not in self._dev_proxys:
                self._dev_proxys[fqnm] = tango.DeviceProxy(fqnm)
                return tango.DeviceProxy(fqnm)
            return self._dev_proxys[fqnm]
        else:
            return DevFactory._test_context.get_device(fqnm)
