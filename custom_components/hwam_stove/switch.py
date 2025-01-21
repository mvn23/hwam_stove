"""
Support for HWAM Stove switches.

For more details about this platform, please refer to the documentation at
https://github.com/mvn23/hwam_stove
"""

from collections.abc import Awaitable
from dataclasses import dataclass
import logging
from typing import Any, Callable

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ID, EntityCategory
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from pystove import pystove

from .const import DATA_STOVES, DOMAIN, StoveDeviceIdentifier
from .coordinator import StoveCoordinator
from .entity import HWAMStoveCoordinatorEntity, HWAMStoveEntityDescription


@dataclass(frozen=True, kw_only=True)
class HWAMStoveSwitchEntityDescription(
    SwitchEntityDescription,
    HWAMStoveEntityDescription,
):
    """Describes a hwam_stove switch entity."""

    state_func: Callable[[Any], bool] = bool
    turn_off_func: Callable[[StoveCoordinator], Awaitable[bool]]
    turn_on_func: Callable[[StoveCoordinator], Awaitable[bool]]


SWITCH_DESCRIPTIONS = [
    HWAMStoveSwitchEntityDescription(
        key=pystove.DATA_NIGHT_LOWERING,
        translation_key="night_lowering",
        device_identifier=StoveDeviceIdentifier.STOVE,
        state_func=lambda x: bool(x != pystove.NIGHT_LOWERING_STATES[0]),
        turn_off_func=lambda hub: hub.stove.set_night_lowering(False),
        turn_on_func=lambda hub: hub.stove.set_night_lowering(True),
        icon="mdi:theme-light-dark",
    ),
    HWAMStoveSwitchEntityDescription(
        key=pystove.DATA_REMOTE_REFILL_ALARM,
        translation_key="remote_refill_alarm",
        device_identifier=StoveDeviceIdentifier.REMOTE,
        turn_off_func=lambda hub: hub.stove.set_remote_refill_alarm(False),
        turn_on_func=lambda hub: hub.stove.set_remote_refill_alarm(True),
        icon="mdi:bell-cog",
    ),
]

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the HWAM Stove binary sensors."""
    stove_hub = hass.data[DOMAIN][DATA_STOVES][config_entry.data[CONF_ID]]
    async_add_entities(
        HwamStoveBinarySensor(
            stove_hub,
            entity_description,
        )
        for entity_description in SWITCH_DESCRIPTIONS
    )


class HwamStoveBinarySensor(HWAMStoveCoordinatorEntity, SwitchEntity):
    """Representation of a HWAM Stove switch."""

    entity_category = EntityCategory.CONFIG
    entity_description: HWAMStoveSwitchEntityDescription

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle status updates from the component."""
        self._attr_is_on = self.entity_description.state_func(
            self.coordinator.data[self.entity_description.key]
        )
        self.async_write_ha_state()

    async def async_turn_off(self, **kwargs) -> None:
        """Turn off the switch."""
        success = await self.entity_description.turn_off_func(self.coordinator)
        if success:
            self._attr_is_on = False
            self.async_schedule_update_ha_state()

    async def async_turn_on(self, **kwargs) -> None:
        """Turn on the switch."""
        success = await self.entity_description.turn_on_func(self.coordinator)
        if success:
            self._attr_is_on = True
            self.async_schedule_update_ha_state()
