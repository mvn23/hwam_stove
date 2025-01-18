"""Common HWAM Stove entity properties."""

from homeassistant.helpers.entity import EntityDescription


class HWAMStoveEntityDescription(EntityDescription):
    """Describe common hwam_stove entity properties."""

    name_format: str
