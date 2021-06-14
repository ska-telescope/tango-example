import enum


class Running_state(enum.IntEnum):
    """Python enumerated type for Running_state attribute."""

    PREPARE = 0
    WORK = 1
    REST = 2
