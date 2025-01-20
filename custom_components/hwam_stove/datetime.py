"""
Support for HWAM Stove datetime entities.

For more details about this platform, please refer to the documentation at
https://github.com/mvn23/hwam_stove
"""

from collections.abc import Awaitable
from dataclasses import dataclass
from datetime import datetime
import logging
from typing import Any, Callable

from homeassistant.components.datetime import DateTimeEntity, DateTimeEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ID
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util.dt import get_default_time_zone

from pystove import pystove

from .const import DATA_STOVES, DOMAIN, StoveDeviceIdentifier
from .coordinator import StoveCoordinator
from .entity import HWAMStoveCoordinatorEntity, HWAMStoveEntityDescription


@dataclass(frozen=True, kw_only=True)
class HWAMStoveDateTimeEntityDescription(
    DateTimeEntityDescription,
    HWAMStoveEntityDescription,
):
    """Describes a hwam_stove datetime entity."""

    set_func: Callable[[StoveCoordinator, datetime], Awaitable[Any]]


TIME_DESCRIPTIONS = [
    HWAMStoveDateTimeEntityDescription(
        key=pystove.DATA_DATE_TIME,
        translation_key="date_and_time",
        device_identifier=StoveDeviceIdentifier.STOVE,
        set_func=lambda hub, date_time: hub.stove.set_time(date_time),
    ),
]

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the HWAM Stove datetime entities."""
    stove_device = hass.data[DOMAIN][DATA_STOVES][config_entry.data[CONF_ID]]
    async_add_entities(
        HwamStoveTime(
            stove_device,
            description,
        )
        for description in TIME_DESCRIPTIONS
    )


class HwamStoveTime(HWAMStoveCoordinatorEntity, DateTimeEntity):
    """Representation of a HWAM Stove datetime entity."""

    entity_description: HWAMStoveDateTimeEntityDescription
    _attr_native_value: datetime | None = None

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle status updates from the component."""
        naive_dt: datetime = self.coordinator.data[self.entity_description.key]
        self._attr_native_value = datetime.combine(
            naive_dt.date(), naive_dt.time(), get_default_time_zone()
        )
        self.async_write_ha_state()

    async def async_set_value(self, value: datetime) -> None:
        """Update the time value on the stove."""
        await self.entity_description.set_func(self.coordinator, value)
