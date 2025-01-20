"""
Hwam stove fan entity.

For more details about this platform, please refer to the documentation at
https://github.com/mvn23/hwam_stove
"""

from dataclasses import dataclass
import logging
from typing import Any, Optional

from homeassistant.components.fan import (
    FanEntity,
    FanEntityDescription,
    FanEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ID
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from pystove import pystove

from .const import DATA_STOVES, DOMAIN, StoveDeviceIdentifier
from .entity import HWAMStoveCoordinatorEntity, HWAMStoveEntityDescription

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
    stove_hub = hass.data[DOMAIN][DATA_STOVES][config_entry.data[CONF_ID]]
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


class StoveBurnLevel(HWAMStoveCoordinatorEntity, FanEntity):
    """Representation of a fan."""

    entity_description: HWAMStoveFanEntityDescription
    _attr_speed_count = 5
    _attr_supported_features = FanEntityFeature.TURN_ON | FanEntityFeature.SET_SPEED

    @callback
    def _handle_coordinator_update(self) -> None:
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

    async def async_turn_on(
        self,
        percentage: Optional[int] = None,
        preset_mode: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Turn on the fan.

        This method must be run in the event loop and returns a coroutine.
        """
        if not self._attr_is_on:
            await self.coordinator.stove.start()

    @property
    def is_on(self) -> bool | None:
        """Return true if the entity is on."""
        return self._attr_is_on
