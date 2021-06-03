import tango


class DevFactory:
    def get_prepare_counter(self):
        import logging

        logging.info("stica")
        return tango.DeviceProxy("test/counter/prepare")

    def get_work_counter(self):
        return tango.DeviceProxy("test/counter/work")

    def get_rest_counter(self):
        return tango.DeviceProxy("test/counter/rest")

    def get_cycles_counter(self):
        return tango.DeviceProxy("test/counter/cycles")

    def get_tabatas_counter(self):
        return tango.DeviceProxy("test/counter/tabatas")
