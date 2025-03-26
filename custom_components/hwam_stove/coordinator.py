"""HWAM Stove Update Coordinator."""

from datetime import timedelta
import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_NAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from pystove import pystove

from .const import DOMAIN, StoveDeviceIdentifier

_LOGGER = logging.getLogger(__name__)


class StoveCoordinator(DataUpdateCoordinator):
    """Abstract description of a stove coordinator."""

    config_entry: ConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        stove: pystove.Stove,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"HWAM Stove {config_entry.data[CONF_NAME]}",
            update_interval=timedelta(seconds=10),
            always_update=False,
        )
        self.hass = hass
        self.name = config_entry.data[CONF_NAME]
        self.stove = stove

        dev_reg = dr.async_get(hass)
        self.stove_device_entry = dev_reg.async_get_or_create(
            config_entry_id=config_entry.entry_id,
            identifiers={
                (DOMAIN, f"{config_entry.entry_id}-{StoveDeviceIdentifier.STOVE}")
            },
            manufacturer="HWAM",
            translation_key="hwam_stove_device",
        )
        self.remote_device_entry = dev_reg.async_get_or_create(
            config_entry_id=config_entry.entry_id,
            identifiers={
                (DOMAIN, f"{config_entry.entry_id}-{StoveDeviceIdentifier.REMOTE}")
            },
            manufacturer="HWAM",
            translation_key="hwam_remote_device",
        )

    async def _async_update_data(self) -> dict[str, Any]:
        """Update stove info."""
        data = await self.stove.get_data()
        if data is None:
            raise UpdateFailed("Got empty response")

        self.update_interval = timedelta(
            seconds=10 if data[pystove.DATA_PHASE] != pystove.PHASE[5] else 60
        )

        dev_reg = dr.async_get(self.hass)
        dev_reg.async_update_device(
            self.stove_device_entry.id,
            model=self.stove.series,
            sw_version=data.get(pystove.DATA_FIRMWARE_VERSION),
        )
        dev_reg.async_update_device(
            self.remote_device_entry.id,
            sw_version=data.get(pystove.DATA_REMOTE_VERSION),
        )
        return data
