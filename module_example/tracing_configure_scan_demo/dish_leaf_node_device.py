from tango.server import command, run, device_property
from tango import DeviceProxy
from tracing import apm
from ska.base import SKABaseDevice


class DishLeafNode(SKABaseDevice):

    dish_master_name = device_property(
        dtype="str", default_value="mid_d0000/elt/master"
    )

    def init_device(self):
        super().init_device()
        self.dish_master_dp = DeviceProxy(self.dish_master_name)

    @command(dtype_in="str")
    @apm
    def ConfigureScan(self, argin):
        # with capture_span("ConfigureScan of DSH Master"):
        self.dish_master_dp.ConfigureScan(argin)

        self.logger.info("{} ConfigureScan command successful!".format(self.get_name()))


if __name__ == "__main__":
    run([DishLeafNode])
