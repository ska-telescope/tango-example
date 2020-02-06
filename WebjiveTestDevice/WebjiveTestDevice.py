# -*- coding: utf-8 -*-
#
# This file is part of the WebjiveTestDevice project
#
#
#
# Distributed under the terms of the GPL license.
# See LICENSE.txt for more info.

""" WebjiveTestDevice

"""

# PyTango imports
import PyTango
from PyTango import DebugIt
from PyTango.server import run
from PyTango.server import Device, DeviceMeta
from PyTango.server import attribute, command
from PyTango import AttrQuality, DispLevel, DevState
from PyTango import AttrWriteType, PipeWriteType
# Additional import
# PROTECTED REGION ID(WebjiveTestDevice.additionnal_import) ENABLED START #
import random
import numpy as np
# PROTECTED REGION END #    //  WebjiveTestDevice.additionnal_import

__all__ = ["WebjiveTestDevice", "main"]


class WebjiveTestDevice(Device):
    """
    """
    __metaclass__ = DeviceMeta
    # PROTECTED REGION ID(WebjiveTestDevice.class_variable) ENABLED START #
    # PROTECTED REGION END #    //  WebjiveTestDevice.class_variable

    # ----------
    # Attributes
    # ----------

    randomattr = attribute(
        dtype='double',
    )

    randomattr2 = attribute(
        dtype='double',
    )

    randomattr3 = attribute(
        dtype='double',
    )

    dishstate = attribute(
        dtype='DevEnum',
        access=AttrWriteType.WRITE,
        enum_labels=["Standby", "Ready", "Slew", "Track", "Scan", "Stow", "Error", ],
    )

    spectrum_att = attribute(
        dtype=('double',),
        max_dim_x=2048,
    )

    # ---------------
    # General methods
    # ---------------

    def init_device(self):
        Device.init_device(self)
        self.set_change_event("randomattr", True, False)
        self.set_change_event("randomattr2", True, False)
        self.set_change_event("randomattr3", True, False)
        self.set_change_event("dishstate", True, False)
        # PROTECTED REGION ID(WebjiveTestDevice.init_device) ENABLED START #
        # PROTECTED REGION END #    //  WebjiveTestDevice.init_device

    def always_executed_hook(self):
        # PROTECTED REGION ID(WebjiveTestDevice.always_executed_hook) ENABLED START #
        pass
        # PROTECTED REGION END #    //  WebjiveTestDevice.always_executed_hook

    def delete_device(self):
        # PROTECTED REGION ID(WebjiveTestDevice.delete_device) ENABLED START #
        pass
        # PROTECTED REGION END #    //  WebjiveTestDevice.delete_device

    # ------------------
    # Attributes methods
    # ------------------

    def read_randomattr(self):
        # PROTECTED REGION ID(WebjiveTestDevice.randomattr_read) ENABLED START #
        self.randomattr = random.random() * 100
        return self.randomattr
        # PROTECTED REGION END #    //  WebjiveTestDevice.randomattr_read

    def read_randomattr2(self):
        # PROTECTED REGION ID(WebjiveTestDevice.randomattr2_read) ENABLED START #
        self.randomattr2 = random.random() * 100
        return self.randomattr2
        # PROTECTED REGION END #    //  WebjiveTestDevice.randomattr2_read

    def read_randomattr3(self):
        # PROTECTED REGION ID(WebjiveTestDevice.randomattr3_read) ENABLED START #
        self.randomattr3 = random.random() * 100
        return self.randomattr3
        # PROTECTED REGION END #    //  WebjiveTestDevice.randomattr3_read

    def write_dishstate(self, value):
        # PROTECTED REGION ID(WebjiveTestDevice.dishstate_write) ENABLED START #
        pass
        # PROTECTED REGION END #    //  WebjiveTestDevice.dishstate_write

    def read_spectrum_att(self):
        # PROTECTED REGION ID(WebjiveTestDevice.spectrum_att_read) ENABLED START #
        a = np.array(random.random() * 100)

        for count in range(1, 1024):
            a = np.append(a, random.random() * 100)

        self.spectrum_att = a
        return self.spectrum_att
        # PROTECTED REGION END #    //  WebjiveTestDevice.spectrum_att_read


    # --------
    # Commands
    # --------

# ----------
# Run server
# ----------


def main(args=None, **kwargs):
    # PROTECTED REGION ID(WebjiveTestDevice.main) ENABLED START #
    return run((WebjiveTestDevice,), args=args, **kwargs)
    # PROTECTED REGION END #    //  WebjiveTestDevice.main

if __name__ == '__main__':
    main()
