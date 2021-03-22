import json

from ska_tango_base import SKABaseDevice

from tango.server import command, run


class LogTestDownStream(SKABaseDevice):
    def init_device(self):
        super().init_device()

    @command(dtype_in="str")
    def Scan(self, argin):
        self.logger.info(f"Scan {argin}")


def main(args=None, **kwargs):
    return run((LogTestDownStream,), args=args, **kwargs)


if __name__ == "__main__":
    main()
