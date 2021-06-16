import enum


class RunningState(enum.IntEnum):
    """Python enumerated type for Running_state attribute."""

    PREPARE = 0
    WORK = 1
    REST = 2
