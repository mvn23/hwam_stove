"""
Support for HWAM Stove buttons.

For more details about this platform, please refer to the documentation at
https://github.com/mvn23/hwam_stove
"""

from collections.abc import Awaitable
from dataclasses import dataclass
import logging
from typing import Any, Callable

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ID
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from pystove import pystove

from .const import DATA_STOVES, DOMAIN, StoveDeviceIdentifier
from .entity import HWAMStoveBaseEntity, HWAMStoveEntityDescription


@dataclass(frozen=True, kw_only=True)
class HWAMStoveButtonEntityDescription(
    ButtonEntityDescription,
    HWAMStoveEntityDescription,
):
    """Describes a hwam_stove button entity."""

    press_func: Callable[[pystove.Stove], Awaitable[Any]]


BUTTON_DESCRIPTIONS = [
    HWAMStoveButtonEntityDescription(
        key="start",
        translation_key="start",
        device_identifier=StoveDeviceIdentifier.STOVE,
        press_func=lambda stove: stove.start(),
    ),
    HWAMStoveButtonEntityDescription(
        key="sync_clock",
        translation_key="sync_clock",
        device_identifier=StoveDeviceIdentifier.STOVE,
        press_func=lambda stove: stove.set_time(),
    ),
]

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the HWAM Stove buttons."""
    stove_hub = hass.data[DOMAIN][DATA_STOVES][config_entry.data[CONF_ID]]
    async_add_entities(
        HwamStoveButton(
            stove_hub.stove,
            config_entry,
            entity_description,
        )
        for entity_description in BUTTON_DESCRIPTIONS
    )


class HwamStoveButton(HWAMStoveBaseEntity, ButtonEntity):
    """Representation of a HWAM Stove button."""

    entity_description: HWAMStoveButtonEntityDescription

    async def async_press(self) -> None:
        """Perform the button action."""
        await self.entity_description.press_func(self.stove)
