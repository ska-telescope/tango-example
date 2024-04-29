"""A Demo Device to demonstrate Tango event mechanism and polling."""

from tango import AttrWriteType, DebugIt, DevState
from tango.server import Device, attribute, command, run


class PollingDemoDevice(Device):
    """A Demo Device to demonstrate Tango event mechanism and polling.

    It is made up of two attributes, one of which is pollable and the
    other is not. Both attributes are initialized with a value of 0,
    can be incremented with a command and can be reset.
    """

    # ----------
    # Attributes
    # ----------

    pollable_attr = attribute(
        name="pollable_attr",
        label="Pollable Attribute",
        dtype="DevLong",
        access=AttrWriteType.READ_WRITE,
        # NOTE: period param is not necessary if the client
        # specifies the polling period when subscribing to the attribute
        # polling_period=100,
        # this tells what is a change (minimum amount to
        # trigger it). It is necessary to enable polling
        # and to trigger the change event
        abs_change=1,
    )

    not_pollable_attr = attribute(
        name="not_pollable_attr",
        label="Not Pollable Attribute",
        access=AttrWriteType.READ_WRITE,
        dtype="DevLong",
    )

    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        Device.init_device(self)
        self._pollable_attr = 0
        self._not_pollable_attr = 0
        self.set_state(DevState.ON)
        self.set_status("Device initialized")

    # ----------
    # Attributes
    # ----------

    def read_pollable_attr(self):
        return self._pollable_attr

    def write_pollable_attr(self, value):
        self._pollable_attr = value

    def read_not_pollable_attr(self):
        return self._not_pollable_attr

    def write_not_pollable_attr(self, value):
        self._not_pollable_attr = value

    # ----------
    # Commands
    # ----------

    @command()
    @DebugIt()
    def increment_pollable(self):
        self.write_pollable_attr(self.read_pollable_attr() + 1)

    @command()
    @DebugIt()
    def increment_not_pollable(self):
        self.write_not_pollable_attr(self.read_not_pollable_attr() + 1)

    @command()
    @DebugIt()
    def reset(self):
        self.write_pollable_attr(0)
        self.write_not_pollable_attr(0)


# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    """Main function of the Counter module."""
    # PROTECTED REGION ID(Counter.main) ENABLED START #
    return run((PollingDemoDevice,), args=args, **kwargs)
    # PROTECTED REGION END #    //  Counter.main


if __name__ == "__main__":
    main()
