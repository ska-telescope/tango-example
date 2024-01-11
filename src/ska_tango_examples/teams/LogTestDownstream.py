from ska_tango_base import SKABaseDevice
from tango.server import command, run

from ska_tango_examples.teams.GenericComponentManager import (
    GenericComponentManager,
)


class LogTestDownStream(SKABaseDevice):
    @command(dtype_in="str")
    def Scan(self, argin):
        self.logger.info("Scan %s", argin)

    def create_component_manager(self: SKABaseDevice):
        return GenericComponentManager(self.logger)


def main(args=None, **kwargs):
    return run((LogTestDownStream,), args=args, **kwargs)


if __name__ == "__main__":
    main()
