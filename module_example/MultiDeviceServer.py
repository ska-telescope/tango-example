import json

from ska.logging import transaction
from ska.base import SKABaseDevice

from tango import DeviceProxy, Group, DeviceData, DevString
from tango.server import command, run, device_property


class UpStream(SKABaseDevice):
    def init_device(self):
        super().init_device()
        self.child_device = DeviceProxy("ska_mid/downstream/1")

    @command(dtype_in="str")
    def CallWithContextAndLogger(self, argin):
        self.logger.info("CallWithContextAndLogger")
        argin_json = json.loads(argin)
        with transaction(
            "CallWithContext", argin_json, logger=self.logger
        ) as transaction_id:
            argin_json["transaction_id"] = transaction_id
            argin = json.dumps(argin_json)
            self.child_device.Scan(argin)

    @command(dtype_in="str")
    def CallWithContextNoLogger(self, argin):
        self.logger.info("CallWithContextNoLogger")
        argin_json = json.loads(argin)
        with transaction("CallWithContext", argin_json) as transaction_id:
            argin_json["transaction_id"] = transaction_id
            argin = json.dumps(argin_json)
            self.child_device.Scan(argin)

    @command(dtype_in="str")
    def CallWithOutContext(self, argin):
        self.logger.info("CallWithOutContext")
        self.child_device.Scan(argin)


class DownStream(SKABaseDevice):
    def init_device(self):
        super().init_device()

    @command(dtype_in="str")
    def Scan(self, argin):
        self.logger.info("Scan")


class SubarrayNode(SKABaseDevice):
    def init_device(self):
        super().init_device()
        self.csp_subarray_ln_dp = DeviceProxy("ska_mid/tm_leaf_node/csp_subarray02")
        self.sdp_subarray_ln_dp = DeviceProxy("ska_mid/tm_leaf_node/sdp_subarray02")
        self.dish_leaf_nodes = Group("dish leaf nodes")
        self.dish_leaf_nodes.add("ska_mid/tm_leaf_node/d0011")
        self.dish_leaf_nodes.add("ska_mid/tm_leaf_node/d0012")

    @command(dtype_in="str")
    def ConfigureScan(self, argin):
        argin_json = json.loads(argin)
        with transaction(
            "ConfigureScan", argin_json, logger=self.logger
        ) as transaction_id:
            argin_json["transaction_id"] = transaction_id
            argin = json.dumps(argin_json)
            self.csp_subarray_ln_dp.ConfigureScan(argin)
            self.sdp_subarray_ln_dp.ConfigureScan(argin)

            cmd_data = DeviceData()
            cmd_data.insert(DevString, argin)
            self.dish_leaf_nodes.command_inout("ConfigureScan", cmd_data)
            self.logger.info("ConfigureScan in transaction with logger")

        self.logger.info("ConfigureScan out transaction with logger")


class SubarraySdpLeafNode(SKABaseDevice):
    def init_device(self):
        super().init_device()
        self.sdp_subarray_dp = DeviceProxy("mid_sdp/elt/subarray_2")

    @command(dtype_in="str")
    def ConfigureScan(self, argin):
        argin_json = json.loads(argin)
        with transaction("ConfigureScan", argin_json) as transaction_id:
            argin_json["transaction_id"] = transaction_id
            argin = json.dumps(argin_json)
            self.sdp_subarray_dp.ConfigureScan(argin)
            self.logger.info("ConfigureScan no logger in context")
        self.logger.info("ConfigureScan no logger out context")


class SubarrayCspLeafNode(SKABaseDevice):
    def init_device(self):
        super().init_device()
        self.csp_subarray_dp = DeviceProxy("mid_csp/elt/subarray_2")

    @command(dtype_in="str")
    def ConfigureScan(self, argin):
        argin_json = json.loads(argin)
        with transaction(
            "ConfigureScan", argin_json, logger=self.logger
        ) as transaction_id:
            argin_json["transaction_id"] = transaction_id
            argin = json.dumps(argin_json)
            self.csp_subarray_dp.ConfigureScan(argin)
            self.logger.info(
                "{} ConfigureScan command successful!".format(self.get_name())
            )


class DishLeafNode(SKABaseDevice):

    dish_master_name = device_property(
        dtype="str", default_value="mid_d0011/elt/master"
    )

    def init_device(self):
        super().init_device()
        self.dish_master_dp = DeviceProxy(self.dish_master_name)

    @command(dtype_in="str")
    def ConfigureScan(self, argin):
        argin_json = json.loads(argin)
        with transaction(
            "ConfigureScan", argin_json, logger=self.logger
        ) as transaction_id:
            argin_json["transaction_id"] = transaction_id
            argin = json.dumps(argin_json)
            self.dish_master_dp.ConfigureScan(argin)
            self.logger.info(
                "{} ConfigureScan command successful!".format(self.get_name())
            )

    @command(dtype_in=int)
    def EndScan(self, argin):
        self.dish_master_dp.EndScan(argin)
        self.logger.info("{} EndScan command successful!".format(self.get_name()))
        with transaction("EndScan", {}) as transaction_id:
            self.logger.info("EndScan no logger in context")
        self.logger.info("EndScan no logger out context")


class DishMaster(SKABaseDevice):
    def init_device(self):
        super().init_device()

    @command(dtype_in="str")
    def ConfigureScan(self, argin):
        argin_json = json.loads(argin)
        with transaction(
            "ConfigureScan", argin_json, logger=self.logger
        ) as transaction_id:
            argin_json["transaction_id"] = transaction_id
            argin = json.dumps(argin_json)
            self.logger.info(
                "{} ConfigureScan command successful!".format(self.get_name())
            )

    @command(dtype_in=int)
    def EndScan(self, argin):
        self.logger.info("{} EndScan command with {}".format(self.get_name(), argin))

        with transaction("EndScan", {}, logger=self.logger) as transaction_id:
            self.logger.info("EndScan Expect a different transaction ID in context")
        self.logger.info("EndScan out context")


class SdpSubarray(SKABaseDevice):
    def init_device(self):
        super().init_device()

    @command(dtype_in="str")
    def ConfigureScan(self, argin):
        argin_json = json.loads(argin)
        with transaction(
            "ConfigureScan", argin_json, logger=self.logger
        ) as transaction_id:
            argin_json["transaction_id"] = transaction_id
            argin = json.dumps(argin_json)
            self.logger.info(
                "{} ConfigureScan command successful!".format(self.get_name())
            )


class CspSubarray(SKABaseDevice):
    def init_device(self):
        super().init_device()
        self.cbf_subarray_dp = DeviceProxy("mid_cbf/elt/subarray_2")

    @command(dtype_in="str")
    def ConfigureScan(self, argin):
        argin_json = json.loads(argin)
        with transaction(
            "ConfigureScan", argin_json, logger=self.logger
        ) as transaction_id:
            argin_json["transaction_id"] = transaction_id
            argin = json.dumps(argin_json)
            self.cbf_subarray_dp.ConfigureScan(argin)
            self.logger.info(
                "{} ConfigureScan command successful!".format(self.get_name())
            )


class CbfSubarray(SKABaseDevice):
    def init_device(self):
        super().init_device()

    @command(dtype_in="str")
    def ConfigureScan(self, argin):
        argin_json = json.loads(argin)
        with transaction(
            "ConfigureScan", argin_json, logger=self.logger
        ) as transaction_id:
            argin_json["transaction_id"] = transaction_id
            argin = json.dumps(argin_json)
            self.logger.info(
                "{} ConfigureScan command successful!".format(self.get_name())
            )


if __name__ == "__main__":
    run(
        [
            UpStream,
            DownStream,
            SubarrayNode,
            SubarraySdpLeafNode,
            SubarrayCspLeafNode,
            DishLeafNode,
            DishMaster,
            SdpSubarray,
            CspSubarray,
            CbfSubarray,
        ]
    )
