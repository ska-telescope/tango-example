import tango


class DevFactory:
    _test_context = None

    def get_device(self, fqnm):
        if DevFactory._test_context is None:
            return tango.DeviceProxy(fqnm)
        else:
            return DevFactory._test_context.get_device(fqnm)

    def get_prepare_counter(self):
        fqnm = "test/counter/prepare"
        return self.get_device(fqnm)

    def get_work_counter(self):
        fqnm = "test/counter/work"
        return self.get_device(fqnm)

    def get_rest_counter(self):
        fqnm = "test/counter/rest"
        return self.get_device(fqnm)

    def get_cycles_counter(self):
        fqnm = "test/counter/cycles"
        return self.get_device(fqnm)

    def get_tabatas_counter(self):
        fqnm = "test/counter/tabatas"
        return self.get_device(fqnm)
