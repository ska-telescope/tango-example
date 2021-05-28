import json

from ska.log_transactions import transaction
from ska_tango_base import SKABaseDevice
from tango import DeviceProxy
from tango.server import command, run


class LogTestUpStream(SKABaseDevice):
    def init_device(self):
        super().init_device()
        self.child_device = DeviceProxy("log/test/downstream")

    @command(dtype_in="str")
    def CallWithContext(self, argin):
        argin_json = json.loads(argin)
        self.logger.info("Logger %s", self.logger)
        with transaction(
            "CallWithContext", argin_json, logger=self.logger
        ) as transaction_id:
            self.logger.info("CallWithContext in context")
            argin_json["transaction_id"] = transaction_id
            argin = json.dumps(argin_json)
            self.child_device.Scan(argin)
        self.logger.info("CallWithContext out of context")

        with transaction("CallWithContext", argin_json) as transaction_id:
            self.logger.info("CallWithContext in context no logger")
            argin_json["transaction_id"] = transaction_id
            argin = json.dumps(argin_json)
            self.child_device.Scan(argin)
        self.logger.info("CallWithContext out of context no logger")

    @command(dtype_in="str")
    def CallWithOutContext(self, argin):
        self.child_device.Scan(argin)

    @command(dtype_in="str")
    def CallRaisesException(self, argin):
        argin_json = json.loads(argin)
        self.logger.info("Logger %s", self.logger)
        with transaction(
            "CallRaisesException", argin_json, logger=self.logger
        ):
            self.logger.info("CallRaisesException in context")
            raise RuntimeError("An exception has occured")


def main(args=None, **kwargs):
    return run((LogTestUpStream,), args=args, **kwargs)


if __name__ == "__main__":
    main()
