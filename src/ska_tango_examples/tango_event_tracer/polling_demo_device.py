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

    # a subscribable attribute
    subscrib_attr = attribute(
        name="subscrib_attr",
        label="Subscribable Attribute",
        access=AttrWriteType.READ_WRITE,
        dtype="DevLong",
    )

    # still a subscribable attribute (but obtained by polling)
    pollable_attr = attribute(
        name="pollable_attr",
        label="Pollable Attribute",
        dtype="DevLong",
        access=AttrWriteType.READ_WRITE,
        # NOTE: polling period param is not necessary if you set
        # in `init_device` method that the attribute fires change
        # events (`self.set_change_event("pollable_attr", True, False)`)
        # and then you fire them manually
        # (`self.push_change_event("pollable_attr", self._pollable_attr)`)
        polling_period=100,
        # this tells what is a change (minimum amount to
        # trigger it). It is necessary to enable polling
        # and to trigger the change event
        # (if you are using polling...)
        abs_change=1,
    )

    # an attribute that is not subscribable because it is neither
    # marked as "event firing" nor as "pollable"
    not_subscrib_attr = attribute(
        name="not_subscrib_attr",
        label="Not Subscribable Attribute",
        access=AttrWriteType.READ_WRITE,
        dtype="DevLong",
    )

    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        Device.init_device(self)

        self.write_not_subscrib_attr(0)
        self.write_pollable_attr(0)
        self.write_subscrib_attr(0)

        self.set_state(DevState.ON)
        self.set_status("Device initialized")

        # enable subscribing to the subscribable attribute
        self.set_change_event("subscrib_attr", True, False)

    # ----------
    # Attributes
    # ----------

    def read_pollable_attr(self):
        return self._pollable_attr

    def write_pollable_attr(self, value):
        self._pollable_attr = value

    def read_not_subscrib_attr(self):
        return self._not_subscrib_attr

    def write_not_subscrib_attr(self, value):
        self._not_subscrib_attr = value

    def read_subscrib_attr(self):
        return self._pollable_attr

    def write_subscrib_attr(self, value):
        self._pollable_attr = value

        # manually fire the change event for the subscribable attribute
        self.push_change_event("subscrib_attr", self._pollable_attr)

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
        self.write_not_subscrib_attr(self.read_not_subscrib_attr() + 1)

    @command()
    @DebugIt()
    def increment_subscrib(self):
        self.write_subscrib_attr(self.read_subscrib_attr() + 1)

    @command()
    @DebugIt()
    def reset(self):
        self.write_pollable_attr(0)
        self.write_not_subscrib_attr(0)
        self.write_subscrib_attr(0)


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
