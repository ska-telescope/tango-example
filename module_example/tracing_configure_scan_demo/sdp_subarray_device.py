from tango.server import command, run
from tracing import apm
from ska.base import SKABaseDevice


class SdpSubarray(SKABaseDevice):
    def init_device(self):
        super().init_device()

    @command(dtype_in="str")
    @apm
    def ConfigureScan(self, argin):
        self.logger.info("{} ConfigureScan command successful!".format(self.get_name()))


if __name__ == "__main__":
    run([SdpSubarray])
