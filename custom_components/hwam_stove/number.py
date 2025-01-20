"""
Support for HWAM Stove number entities.

For more details about this platform, please refer to the documentation at
https://github.com/mvn23/hwam_stove
"""

from collections.abc import Awaitable
from dataclasses import dataclass
import logging
from typing import Any, Callable

from homeassistant.components.number import NumberEntity, NumberEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ID
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from pystove import pystove

from .const import DATA_STOVES, DOMAIN, StoveDeviceIdentifier
from .entity import HWAMStoveCoordinatorEntity, HWAMStoveEntityDescription


@dataclass(frozen=True, kw_only=True)
class HWAMStoveNumberEntityDescription(
    NumberEntityDescription,
    HWAMStoveEntityDescription,
):
    """Describes a hwam_stove number entity."""

    set_func: Callable[[pystove.Stove, float], Awaitable[bool]]
    state_func: Callable[[Any], float] = float


NUMBER_DESCRIPTIONS = [
    HWAMStoveNumberEntityDescription(
        key=pystove.DATA_BURN_LEVEL,
        translation_key="burn_level",
        device_identifier=StoveDeviceIdentifier.STOVE,
        set_func=lambda stove, value: stove.set_burn_level(int(value)),
        native_max_value=5,
        native_min_value=0,
        native_step=1,
        icon="mdi:fire",
    ),
]

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the HWAM Stove number entities."""
    stove_hub = hass.data[DOMAIN][DATA_STOVES][config_entry.data[CONF_ID]]
    async_add_entities(
        HwamStoveNumber(
            stove_hub,
            entity_description,
        )
        for entity_description in NUMBER_DESCRIPTIONS
    )


class HwamStoveNumber(HWAMStoveCoordinatorEntity, NumberEntity):
    """Representation of a HWAM Stove number entity."""

    entity_description: HWAMStoveNumberEntityDescription

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle status updates from the component."""
        self._attr_native_value = self.entity_description.state_func(
            self.coordinator.data[self.entity_description.key]
        )
        self.async_write_ha_state()

    async def async_set_native_value(self, value: float) -> None:
        """Set the value on the stove."""
        success = await self.entity_description.set_func(self.stove, value)
        if success:
            self._attr_native_value = value
            self.async_write_ha_state()
