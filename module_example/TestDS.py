from tango import Database, DbDevInfo, DeviceProxy, Group, DeviceData, DevString
from tango.server import attribute, command, Device, run, device_property

from tracing import apm
from elasticapm import capture_span

from ska.base import SKABaseDevice


class SubarrayNode(SKABaseDevice):
    def init_device(self):
        super().init_device()
        self.csp_subarray_ln_dp = DeviceProxy("ska_mid/tm_leaf_node/csp_subarray01")
        self.sdp_subarray_ln_dp = DeviceProxy("ska_mid/tm_leaf_node/sdp_subarray01")
        self.dish_leaf_nodes = Group("dish leaf nodes")
        self.dish_leaf_nodes.add("ska_mid/tm_leaf_node/d0001")
        self.dish_leaf_nodes.add("ska_mid/tm_leaf_node/d0002")

    @command(dtype_in='str')
    @apm
    def ConfigureScan(self, argin):
        self.csp_subarray_ln_dp.ConfigureScan(argin)
        self.sdp_subarray_ln_dp.ConfigureScan(argin)

        cmd_data = DeviceData()
        cmd_data.insert(DevString, argin)
        self.dish_leaf_nodes.command_inout("ConfigureScan", cmd_data)

        self.logger.info("{} ConfigureScan command successful!".format(self.get_name()))


class SubarraySdpLeafNode(SKABaseDevice):
    def init_device(self):
        super().init_device()
        self.sdp_subarray_dp = DeviceProxy("mid_sdp/elt/subarray_1")

    @command(dtype_in='str')
    @apm
    def ConfigureScan(self, argin):
        self.sdp_subarray_dp.ConfigureScan(argin)
        self.logger.info("{} ConfigureScan command successful!".format(self.get_name()))


class SubarrayCspLeafNode(SKABaseDevice):
    def init_device(self):
        super().init_device()
        self.csp_subarray_dp = DeviceProxy("mid_csp/elt/subarray_1")

    @command(dtype_in='str')
    @apm
    def ConfigureScan(self, argin):
        self.csp_subarray_dp.ConfigureScan(argin)
        self.logger.info("{} ConfigureScan command successful!".format(self.get_name()))


class DishLeafNode(SKABaseDevice):

    dish_master_name = device_property(dtype="str", default_value="mid_d0000/elt/master")

    def init_device(self):
        super().init_device()
        self.dish_master_dp = DeviceProxy(self.dish_master_name)

    @command(dtype_in='str')
    @apm
    def ConfigureScan(self, argin):
        self.dish_master_dp.ConfigureScan(argin)
        self.logger.info("{} ConfigureScan command successful!".format(self.get_name()))

    @command(dtype_in=int)
    def EndScan(self, argin):
        self.dish_master_dp.EndScan(argin)
        self.logger.info("{} EndScan command successful!".format(self.get_name()))


class DishMaster(SKABaseDevice):
    def init_device(self):
        super().init_device()

    @command(dtype_in='str')
    @apm
    def ConfigureScan(self, argin):
        self.logger.info("{} ConfigureScan command successful!".format(self.get_name()))

    @command(dtype_in=int)
    def EndScan(self, argin):
        self.logger.info("{} EndScan command successful!".format(self.get_name()))


class SdpSubarray(SKABaseDevice):
    def init_device(self):
        super().init_device()

    @command(dtype_in='str')
    @apm
    def ConfigureScan(self, argin):
        self.logger.info("{} ConfigureScan command successful!".format(self.get_name()))


class CspSubarray(SKABaseDevice):
    def init_device(self):
        super().init_device()
        self.cbf_subarray_dp = DeviceProxy("mid_cbf/elt/subarray_1")

    @command(dtype_in='str')
    @apm
    def ConfigureScan(self, argin):
        self.cbf_subarray_dp.ConfigureScan(argin)
        self.logger.info("{} ConfigureScan command successful!".format(self.get_name()))


class CbfSubarray(SKABaseDevice):
    def init_device(self):
        super().init_device()

    @command(dtype_in='str')
    @apm
    def ConfigureScan(self, argin):
        self.logger.info("{} ConfigureScan command successful!".format(self.get_name()))


if __name__ == "__main__":
    run(
        [
            SubarrayNode,
            SubarraySdpLeafNode,
            SubarrayCspLeafNode,
            DishLeafNode,
            DishMaster,
            SdpSubarray,
            CspSubarray,
            CbfSubarray
        ])
