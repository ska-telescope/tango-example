import tango


class DevFactory:
    _test_context = None

    def get_device(self, fqnm):
        if DevFactory._test_context is None:
            return tango.DeviceProxy(fqnm)
        else:
            return DevFactory._test_context.get_device(fqnm)
