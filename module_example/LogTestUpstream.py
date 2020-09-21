import json

from ska.logging import transaction
from ska.base import SKABaseDevice

from tango import DeviceProxy
from tango.server import command, run


class LogTestUpStream(SKABaseDevice):
    def init_device(self):
        super().init_device()
        self.child_device = DeviceProxy("log/test/downstream")

    @command(dtype_in="str")
    def CallWithContext(self, argin):
        argin_json = json.loads(argin)
        with transaction("CallWithContext", argin_json, logger=self.logger) as transaction_id:
            self.logger.info("CallWithContext in context")
            argin_json["transaction_id"] = transaction_id
            argin = json.dumps(argin_json)
            self.child_device.Scan(argin)
        self.logger.info("CallWithContext out of context")

    @command(dtype_in="str")
    def CallWithOutContext(self, argin):
        self.child_device.Scan(argin)


def main(args=None, **kwargs):
    return run((LogTestUpStream,), args=args, **kwargs)


if __name__ == "__main__":
    main()
