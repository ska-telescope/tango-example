from tango import Database, DbDevInfo, DeviceProxy, Group
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
        with capture_span("ConfigureScan of CSP Subarray Leaf Node"):
            self.csp_subarray_ln_dp.ConfigureScan(argin)

        with capture_span("ConfigureScan of SDP Subarray Leaf Node"):
            self.sdp_subarray_ln_dp.ConfigureScan(argin)

        with capture_span("ConfigureScan of DSH Subarray Leaf Node"):
            self.dish_leaf_nodes.command_inout("ConfigureScan", argin)

        self.logger.info("{} ConfigureScan command successful!".format(self.get_name()))


class SubarraySdpLeafNode(SKABaseDevice):
    def init_device(self):
        super().init_device()
        self.sdp_subarray_dp = DeviceProxy("mid_sdp/elt/subarray_1")

    @command(dtype_in='str')
    @apm
    def ConfigureScan(self, argin):
        with capture_span("ConfigureScan of SDP Subarray"):
            self.sdp_subarray_dp.ConfigureScan(argin)

        self.logger.info("{} ConfigureScan command successful!".format(self.get_name()))


class SubarrayCspLeafNode(SKABaseDevice):
    def init_device(self):
        super().init_device()
        self.csp_subarray_dp = DeviceProxy("mid_csp/elt/subarray_1")

    @command(dtype_in='str')
    @apm
    def ConfigureScan(self, argin):
        with capture_span("ConfigureScan of CSP Subarray"):
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
        with capture_span("ConfigureScan of DSH Master"):
            self.dish_master_dp.ConfigureScan(argin)

        self.logger.info("{} ConfigureScan command successful!".format(self.get_name()))


class DishMaster(SKABaseDevice):
    def init_device(self):
        super().init_device()

    @command(dtype_in='str')
    @apm
    def ConfigureScan(self, argin):
        self.logger.info("{} ConfigureScan command successful!".format(self.get_name()))


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
        with capture_span("ConfigureScan of CBF Subarray"):
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

