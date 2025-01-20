"""Common HWAM Stove entity properties."""

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_ID
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import Entity, EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from pystove import Stove

from .const import DOMAIN, StoveDeviceIdentifier
from .coordinator import StoveCoordinator


class HWAMStoveEntityDescription(EntityDescription):
    """Describe common hwam_stove entity properties."""

    device_identifier: StoveDeviceIdentifier


class HWAMStoveBaseEntity(Entity):
    """Represent a hwam_stove base entity."""

    _attr_has_entity_name = True
    entity_description: HWAMStoveEntityDescription
    stove: Stove

    def __init__(
        self,
        stove,
        config_entry: ConfigEntry,
        entity_description: HWAMStoveEntityDescription,
    ) -> None:
        """Initialize the entity."""
        hub_id = config_entry.data[CONF_ID]
        self._attr_unique_id = f"{hub_id}-{entity_description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={
                (
                    DOMAIN,
                    f"{hub_id}-{entity_description.device_identifier}",
                )
            }
        )
        self.entity_description = entity_description
        self.stove = stove


class HWAMStoveCoordinatorEntity(
    HWAMStoveBaseEntity, CoordinatorEntity[StoveCoordinator]
):
    """Represent a hwam_stove coordinator entity."""

    def __init__(
        self,
        stove_coordinator: StoveCoordinator,
        entity_description: HWAMStoveEntityDescription,
    ) -> None:
        """Initialize the entity."""
        CoordinatorEntity.__init__(self, stove_coordinator)
        HWAMStoveBaseEntity.__init__(
            self,
            stove_coordinator.stove,
            stove_coordinator.config_entry,
            entity_description,
        )
