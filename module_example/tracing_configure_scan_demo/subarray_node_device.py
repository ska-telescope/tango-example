from tango.server import command, run
from tango import DeviceProxy, Group, DeviceData, DevString
from tracing import apm
from ska.base import SKABaseDevice


class SubarrayNode(SKABaseDevice):
    def init_device(self):
        super().init_device()
        self.csp_subarray_ln_dp = DeviceProxy("ska_mid/tm_leaf_node/csp_subarray01")
        self.sdp_subarray_ln_dp = DeviceProxy("ska_mid/tm_leaf_node/sdp_subarray01")
        self.dish_leaf_nodes = Group("dish leaf nodes")
        self.dish_leaf_nodes.add("ska_mid/tm_leaf_node/d0001")
        self.dish_leaf_nodes.add("ska_mid/tm_leaf_node/d0002")

    @command(dtype_in="str")
    @apm
    def ConfigureScan(self, argin):
        self.csp_subarray_ln_dp.ConfigureScan(argin)
        self.sdp_subarray_ln_dp.ConfigureScan(argin)
        cmd_data = DeviceData()
        cmd_data.insert(DevString, argin)
        self.dish_leaf_nodes.command_inout("ConfigureScan", cmd_data)

        self.logger.info("{} ConfigureScan command successful!".format(self.get_name()))


if __name__ == "__main__":
    run([SubarrayNode])
