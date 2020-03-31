from tango import Database, DbDevInfo, DeviceProxy

from tango.server import attribute, command, Device, run

from tracing import apm


class SubarrayNode(Device):
    def init_device(self):
        super().init_device()

    @command
    @apm
    def ConfigureScan(self):
        csp_subarray_ln_dp = DeviceProxy("ska_mid/tm_leaf_node/csp_subarray01")
        sdp_subarray_ln_dp = DeviceProxy("ska_mid/tm_leaf_node/sdp_subarray01")
        dsh_ln_dp1 = DeviceProxy("ska_mid/tm_leaf_node/d0001")
        dsh_ln_dp2 = DeviceProxy("ska_mid/tm_leaf_node/d0002")
        csp_subarray_ln_dp.ConfigureScan()
        sdp_subarray_ln_dp.ConfigureScan()
        dsh_ln_dp1.ConfigureScan()
        dsh_ln_dp2.ConfigureScan()


class SubarraySdpLeafNode(Device):
    def init_device(self):
        super().init_device()

    @command
    @apm
    def ConfigureScan(self):
        sdp_subarray_dp = DeviceProxy("mid_sdp/elt/subarray_1")
        sdp_subarray_dp.ConfigureScan()


class SubarrayCspLeafNode(Device):
    def init_device(self):
        super().init_device()

    @command
    @apm
    def ConfigureScan(self):
        csp_subarray_dp = DeviceProxy("mid_csp/elt/subarray_1")
        csp_subarray_dp.ConfigureScan()


class DishLeafNode(Device):
    def init_device(self):
        super().init_device()

    @command
    @apm
    def ConfigureScan(self):
        dsh_master_dp1 = DeviceProxy("mid_d0001/elt/master")
        dsh_master_dp2 = DeviceProxy("mid_d0002/elt/master")
        dsh_master_dp1.ConfigureScan()
        dsh_master_dp2.ConfigureScan()


class DishMaster(Device):
    def init_device(self):
        super().init_device()

    @command
    @apm
    def ConfigureScan(self):
        print("ConfigureScan command successful!")


class SdpSubarray(Device):
    def init_device(self):
        super().init_device()

    @command
    @apm
    def ConfigureScan(self):
        print("ConfigureScan command successful!")


class CspSubarray(Device):
    def init_device(self):
        super().init_device()

    @command
    @apm
    def ConfigureScan(self):
        print("ConfigureScan command successful!")


class CbfSubarray(Device):
    def init_device(self):
        super().init_device()

    @command
    @apm
    def ConfigureScan(self):
        print("ConfigureScan command successful!")


if __name__ == "__main__":
    run([SubarrayNode, SubarraySdpLeafNode, SdpSubarray])

