"""
Hwam stove fan entity.

For more details about this platform, please refer to the documentation at
https://github.com/mvn23/hwam_stove
"""

from dataclasses import dataclass
import logging

from homeassistant.components.fan import (
    DOMAIN,
    FanEntity,
    FanEntityDescription,
    FanEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import slugify

import pystove

from . import CONF_NAME, DATA_HWAM_STOVE, DATA_STOVES
from .entity import HWAMStoveEntityDescription

_LOGGER = logging.getLogger(__name__)

@dataclass(frozen=True, kw_only=True)
class HWAMStoveFanEntityDescription(
    FanEntityDescription,
    HWAMStoveEntityDescription,
):
    """Describes a hwam_stove fan entity."""

FAN_DESCRIPTIONS = [
    HWAMStoveFanEntityDescription(
        key="fan_entity",
        name_format="Burn Level {}",
    )
]

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the HWAM Stove fan."""
    stove_name = config_entry.data[CONF_NAME]
    stove_hub = hass.data[DATA_HWAM_STOVE][DATA_STOVES][stove_name]
    stove = StoveBurnLevel(
        stove_hub,
        HWAMStoveFanEntityDescription(
            key="fan_entity",
            name_format="Burn Level {}",
        )
    )
    async_add_entities([stove])


class StoveBurnLevel(FanEntity):
    """Representation of a fan."""

    def __init__(self, stove_device, entity_description):
        self._burn_level = 0
        self._state = False
        self._stove_device = stove_device
        self._device_name = slugify(f"burn_level_{stove_device.name}")
        self.entity_id = f"{DOMAIN}.{self._device_name}"
        self.entity_description = entity_description
        self._icon = "mdi:fire"

    async def async_added_to_hass(self):
        """Subscribe to updates."""
        async_dispatcher_connect(
            self.hass, self._stove_device.signal, self.receive_report
        )

    async def receive_report(self, data):
        """Receive updates."""
        self._burn_level = data[pystove.DATA_BURN_LEVEL]
        self._state = data[pystove.DATA_PHASE] != pystove.PHASE[5]
        self.async_schedule_update_ha_state()

    async def async_set_percentage(self, percentage: int) -> None:
        """Set the speed of the fan.

        This method must be run in the event loop and returns a coroutine.
        """
        await self._stove_device.stove.set_burn_level(int(percentage / 20))

    async def async_turn_on(self, speed: str = None, **kwargs):
        """Turn on the fan.

        This method must be run in the event loop and returns a coroutine.
        """
        if not self._state:
            await self._stove_device.stove.start()

    async def async_turn_off(self, **kwargs):
        """Disable turn off."""
        pass

    @property
    def is_on(self):
        """Return true if the entity is on."""
        return self._state

    @property
    def percentage(self) -> int:
        """Return the current speed."""
        return self._burn_level * 20

    @property
    def speed_count(self) -> int:
        """Get the list of available speeds."""
        return 5

    @property
    def supported_features(self) -> int:
        """Flag supported features."""
        return FanEntityFeature.SET_SPEED

    @property
    def icon(self) -> str:
        """Set the icon."""
        return self._icon

    @property
    def name(self) -> str:
        """Set the friendly name."""
        return self.entity_description.name_format.format(self._stove_device.stove.name)

    @property
    def should_poll(self) -> str:
        """Return False because entity pushes its state."""
        return False
