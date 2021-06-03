import json

from ska_ser_log_transactions import transaction
from ska_tango_base import SKABaseDevice
from tango import DeviceData, DeviceProxy, DevString, Group
from tango.server import command, run


class TopLevel(SKABaseDevice):
    def init_device(self):
        super().init_device()
        self.mid_level_nodes = Group("Mid level nodes")
        self.mid_level_nodes.add("test/mid_level/1")
        self.mid_level_nodes.add("test/mid_level/2")
        self.mid_level_nodes.add("test/mid_level/3")
        self.mid_level_nodes.add("test/mid_level/4")

    @command(dtype_in="str")
    def CallWithLogger(self, argin):
        self.logger.info("CallWithLogger, top_level")
        argin_json = json.loads(argin)
        with transaction(
            "CallWithLogger, top_level", argin_json, logger=self.logger
        ) as transaction_id:
            self.logger.info("CallWithLogger, top_level")
            argin_json["transaction_id"] = transaction_id
            cmd_data = DeviceData()
            cmd_data.insert(DevString, json.dumps(argin_json))
            self.mid_level_nodes.command_inout("CallWithLogger", cmd_data)

    @command(dtype_in="str")
    def CallWithoutLogger(self, argin):
        self.logger.info("CallWithoutLogger, top_level")
        argin_json = json.loads(argin)
        with transaction(
            "CallWithoutLogger, top_level", argin_json
        ) as transaction_id:
            self.logger.info("CallWithoutLogger, top_level")
            argin_json["transaction_id"] = transaction_id
            cmd_data = DeviceData()
            cmd_data.insert(DevString, json.dumps(argin_json))
            self.mid_level_nodes.command_inout("CallWithoutLogger", cmd_data)

    @command(dtype_in="str")
    def NoTransaction(self, argin):
        self.logger.info("NoTransaction, top_level")
        argin_json = json.loads(argin)
        cmd_data = DeviceData()
        cmd_data.insert(DevString, json.dumps(argin_json))
        self.mid_level_nodes.command_inout("NoTransaction", cmd_data)


class MidLevel1(SKABaseDevice):
    def init_device(self):
        super().init_device()
        self.low_level_device = DeviceProxy("test/low_level/1")

    @command(dtype_in="str")
    def CallWithLogger(self, argin):
        self.logger.info("CallWithLogger, mid 1")
        argin_json = json.loads(argin)
        with transaction(
            "CallWithLogger, mid 1", argin_json, logger=self.logger
        ) as transaction_id:
            self.logger.info("CallWithLogger, mid 1")
            argin_json["transaction_id"] = transaction_id
            self.low_level_device.CallWithLogger(json.dumps(argin_json))

    @command(dtype_in="str")
    def CallWithoutLogger(self, argin):
        self.logger.info("CallWithoutLogger, mid 1")
        argin_json = json.loads(argin)
        with transaction(
            "CallWithoutLogger, mid 1", argin_json
        ) as transaction_id:
            self.logger.info("CallWithoutLogger, mid 1")
            argin_json["transaction_id"] = transaction_id
            self.low_level_device.CallWithoutLogger(json.dumps(argin_json))

    @command(dtype_in="str")
    def NoTransaction(self, argin):
        self.logger.info("NoTransaction, mid 1")
        argin_json = json.loads(argin)
        self.low_level_device.NoTransaction(json.dumps(argin_json))


class MidLevel2(SKABaseDevice):
    def init_device(self):
        super().init_device()
        self.low_level_device = DeviceProxy("test/low_level/1")

    @command(dtype_in="str")
    def CallWithLogger(self, argin):
        self.logger.info("CallWithLogger, mid 2")
        argin_json = json.loads(argin)
        with transaction(
            "CallWithLogger, mid 2", argin_json, logger=self.logger
        ) as transaction_id:
            self.logger.info("CallWithLogger, mid 2")
            argin_json["transaction_id"] = transaction_id
            self.low_level_device.CallWithLogger(json.dumps(argin_json))

    @command(dtype_in="str")
    def CallWithoutLogger(self, argin):
        self.logger.info("CallWithoutLogger, mid 2")
        argin_json = json.loads(argin)
        with transaction(
            "CallWithoutLogger, mid 2", argin_json
        ) as transaction_id:
            self.logger.info("CallWithoutLogger, mid 2")
            argin_json["transaction_id"] = transaction_id
            self.low_level_device.CallWithoutLogger(json.dumps(argin_json))

    @command(dtype_in="str")
    def NoTransaction(self, argin):
        self.logger.info("NoTransaction, mid 2")
        argin_json = json.loads(argin)
        self.low_level_device.NoTransaction(json.dumps(argin_json))


class MidLevel3(SKABaseDevice):
    def init_device(self):
        super().init_device()
        self.low_level_device = DeviceProxy("test/low_level/1")

    @command(dtype_in="str")
    def CallWithLogger(self, argin):
        self.logger.info("CallWithLogger, mid 3")
        argin_json = json.loads(argin)
        with transaction(
            "CallWithLogger, mid 3", argin_json, logger=self.logger
        ) as transaction_id:
            self.logger.info("CallWithLogger, mid 3")
            argin_json["transaction_id"] = transaction_id
            self.low_level_device.CallWithLogger(json.dumps(argin_json))

    @command(dtype_in="str")
    def CallWithoutLogger(self, argin):
        self.logger.info("CallWithoutLogger, mid 3")
        argin_json = json.loads(argin)
        with transaction(
            "CallWithoutLogger, mid 3", argin_json
        ) as transaction_id:
            self.logger.info("CallWithoutLogger, mid 3")
            argin_json["transaction_id"] = transaction_id
            self.low_level_device.CallWithoutLogger(json.dumps(argin_json))

    @command(dtype_in="str")
    def NoTransaction(self, argin):
        self.logger.info("NoTransaction, mid 3")
        argin_json = json.loads(argin)
        self.low_level_device.NoTransaction(json.dumps(argin_json))


class MidLevel4(SKABaseDevice):
    def init_device(self):
        super().init_device()
        self.low_level_device = DeviceProxy("test/low_level/1")

    @command(dtype_in="str")
    def CallWithLogger(self, argin):
        self.logger.info("CallWithLogger, mid 4")
        argin_json = json.loads(argin)
        with transaction(
            "CallWithLogger, mid 4", argin_json, logger=self.logger
        ) as transaction_id:
            self.logger.info("CallWithLogger, mid 4")
            argin_json["transaction_id"] = transaction_id
            self.low_level_device.CallWithLogger(json.dumps(argin_json))

    @command(dtype_in="str")
    def CallWithoutLogger(self, argin):
        self.logger.info("CallWithoutLogger, mid 4")
        argin_json = json.loads(argin)
        with transaction(
            "CallWithoutLogger, mid 4", argin_json
        ) as transaction_id:
            self.logger.info("CallWithoutLogger, mid 4")
            argin_json["transaction_id"] = transaction_id
            self.low_level_device.CallWithoutLogger(json.dumps(argin_json))

    @command(dtype_in="str")
    def NoTransaction(self, argin):
        self.logger.info("NoTransaction, mid 4")
        argin_json = json.loads(argin)
        self.low_level_device.NoTransaction(json.dumps(argin_json))


class LowLevel(SKABaseDevice):
    @command(dtype_in="str")
    def CallWithLogger(self, argin):
        self.logger.info("CallWithLogger, low_level")
        argin_json = json.loads(argin)
        with transaction(
            "CallWithLogger, low_level", argin_json, logger=self.logger
        ):
            self.logger.info("CallWithLogger, low_level")

    @command(dtype_in="str")
    def CallWithoutLogger(self, argin):
        self.logger.info("CallWithoutLogger, low_level")
        argin_json = json.loads(argin)
        with transaction("CallWithoutLogger, low_level", argin_json):
            self.logger.info("CallWithoutLogger, low_level")

    @command(dtype_in="str")
    def NoTransaction(self, argin):
        self.logger.info("NoTransaction, low_level %s", argin)


if __name__ == "__main__":
    run(
        [
            TopLevel,
            MidLevel1,
            MidLevel2,
            MidLevel3,
            MidLevel4,
            LowLevel,
        ]
    )
