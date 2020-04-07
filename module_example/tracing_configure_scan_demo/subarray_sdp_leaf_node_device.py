from tango.server import command, run
from tango import DeviceProxy
from tracing import apm
from ska.base import SKABaseDevice


class SubarraySdpLeafNode(SKABaseDevice):
    def init_device(self):
        super().init_device()
        self.sdp_subarray_dp = DeviceProxy("mid_sdp/elt/subarray_1")

    @command(dtype_in="str")
    @apm
    def ConfigureScan(self, argin):
        self.sdp_subarray_dp.ConfigureScan(argin)

        self.logger.info("{} ConfigureScan command successful!".format(self.get_name()))


if __name__ == "__main__":
    run([SubarraySdpLeafNode])
