"""
Support for HWAM Stove time entities.

For more details about this platform, please refer to the documentation at
https://github.com/mvn23/hwam_stove
"""

from collections.abc import Awaitable
from dataclasses import dataclass
from datetime import time
import logging
from typing import Any, Callable

from homeassistant.components.time import TimeEntity, TimeEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ID, EntityCategory
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from pystove import pystove

from .const import DATA_STOVES, DOMAIN, StoveDeviceIdentifier
from .coordinator import StoveCoordinator
from .entity import HWAMStoveCoordinatorEntity, HWAMStoveEntityDescription


@dataclass(frozen=True, kw_only=True)
class HWAMStoveTimeEntityDescription(
    TimeEntityDescription,
    HWAMStoveEntityDescription,
):
    """Describes a hwam_stove time entity."""

    set_func: Callable[[StoveCoordinator, time], Awaitable[Any]]


TIME_DESCRIPTIONS = [
    HWAMStoveTimeEntityDescription(
        key=pystove.DATA_NIGHT_BEGIN_TIME,
        translation_key="night_begin_time",
        device_identifier=StoveDeviceIdentifier.STOVE,
        set_func=lambda hub, time: hub.stove.set_night_lowering_hours(
            end=hub.data.get(pystove.DATA_NIGHT_END_TIME),
            start=time,
        ),
    ),
    HWAMStoveTimeEntityDescription(
        key=pystove.DATA_NIGHT_END_TIME,
        translation_key="night_end_time",
        device_identifier=StoveDeviceIdentifier.STOVE,
        set_func=lambda hub, time: hub.stove.set_night_lowering_hours(
            end=time,
            start=hub.data.get(pystove.DATA_NIGHT_BEGIN_TIME),
        ),
    ),
]

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the HWAM Stove time entities."""
    stove_device = hass.data[DOMAIN][DATA_STOVES][config_entry.data[CONF_ID]]
    async_add_entities(
        HwamStoveTime(
            stove_device,
            description,
        )
        for description in TIME_DESCRIPTIONS
    )


class HwamStoveTime(HWAMStoveCoordinatorEntity, TimeEntity):
    """Representation of a HWAM Stove time entity."""

    entity_category = EntityCategory.CONFIG
    entity_description: HWAMStoveTimeEntityDescription
    _attr_native_value: time | None = None

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle status updates from the component."""
        self._attr_native_value = self.coordinator.data[self.entity_description.key]
        self.async_write_ha_state()

    async def async_set_value(self, value: time) -> None:
        """Update the time value on the stove."""
        await self.entity_description.set_func(self.coordinator, value)
