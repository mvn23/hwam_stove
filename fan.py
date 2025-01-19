"""
Hwam stove fan entity.

For more details about this platform, please refer to the documentation at
https://github.com/mvn23/hwam_stove
"""

from dataclasses import dataclass
import logging

from homeassistant.components.fan import (
    FanEntity,
    FanEntityDescription,
    FanEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

import pystove

from . import DATA_HWAM_STOVE, DATA_STOVES
from .const import StoveDeviceIdentifier
from .entity import HWAMStoveEntity, HWAMStoveEntityDescription

_LOGGER = logging.getLogger(__name__)


@dataclass(frozen=True, kw_only=True)
class HWAMStoveFanEntityDescription(
    FanEntityDescription,
    HWAMStoveEntityDescription,
):
    """Describes a hwam_stove fan entity."""


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
            translation_key="fan_entity",
            device_identifier=StoveDeviceIdentifier.STOVE,
            icon="mdi:fire",
        ),
    )
    async_add_entities([stove])


class StoveBurnLevel(HWAMStoveEntity, FanEntity):
    """Representation of a fan."""

    entity_description: HWAMStoveFanEntityDescription
    _attr_speed_count = 5
    _attr_supported_features = FanEntityFeature.SET_SPEED

    @callback
    def _handle_coordinator_update(self):
        """Receive updates."""
        self._attr_percentage = self.coordinator.data[pystove.DATA_BURN_LEVEL] * 20
        self._attr_is_on = self.coordinator.data[pystove.DATA_PHASE] != pystove.PHASE[5]
        self.async_write_ha_state()

    async def async_set_percentage(self, percentage: int) -> None:
        """Set the speed of the fan.

        This method must be run in the event loop and returns a coroutine.
        """
        self._attr_percentage = int(percentage / 20)
        await self.coordinator.stove.set_burn_level(self._attr_percentage)

    async def async_turn_on(self, speed: str = None, **kwargs):
        """Turn on the fan.

        This method must be run in the event loop and returns a coroutine.
        """
        if not self._state:
            await self.coordinator.stove.start()

    async def async_turn_off(self, **kwargs):
        """Disable turn off."""
        pass    

    @property
    def is_on(self):
        """Return true if the entity is on."""
        return self._attr_is_on
