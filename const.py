"""Constants for hwam_stove."""

from enum import StrEnum

DOMAIN = "hwam_stove"


class StoveDeviceIdentifier(StrEnum):
    """Device identification strings."""

    REMOTE = "remote"
    STOVE = "stove"
