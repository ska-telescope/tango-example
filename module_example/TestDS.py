from tango import Database, DbDevInfo, DeviceProxy

from tango.server import attribute, command, Device, run

from tracing import apm


class SubarrayNode(Device):
    def init_device(self):
        super().init_device()

    @command
    @apm
    def ConfigureScan(self):
        dp = DeviceProxy("ska_mid/tm_leaf_node/sdp_subarray01")
        dp.ConfigureScan()


class SubarraySdpLeafNode(Device):
    def init_device(self):
        super().init_device()

    @command
    @apm
    def ConfigureScan(self):
        dp = DeviceProxy("mid_sdp/elt/subarray_1")
        dp.ConfigureScan()


class SdpSubarray(Device):
    def init_device(self):
        super().init_device()

    @command
    @apm
    def ConfigureScan(self):
        print("ConfigureScan command successful!")


if __name__ == "__main__":
    run([SubarrayNode, SubarraySdpLeafNode, SdpSubarray])

