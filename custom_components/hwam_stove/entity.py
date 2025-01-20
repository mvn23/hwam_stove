"""Common HWAM Stove entity properties."""

from homeassistant.const import CONF_ID
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from pystove import Stove

from .const import DOMAIN, StoveDeviceIdentifier
from .coordinator import StoveCoordinator


class HWAMStoveEntityDescription(EntityDescription):
    """Describe common hwam_stove entity properties."""

    device_identifier: StoveDeviceIdentifier


class HWAMStoveCoordinatorEntity(CoordinatorEntity[StoveCoordinator]):
    """Represent a hwam_stove coordinator entity."""

    _attr_has_entity_name = True
    entity_description: HWAMStoveEntityDescription
    stove: Stove

    def __init__(
        self,
        stove_coordinator: StoveCoordinator,
        entity_description: HWAMStoveEntityDescription,
    ) -> None:
        """Initialize the entity."""
        super().__init__(stove_coordinator)
        hub_id = stove_coordinator.config_entry.data[CONF_ID]
        self._attr_unique_id = f"{hub_id}-{entity_description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={
                (
                    DOMAIN,
                    f"{hub_id}-{entity_description.device_identifier}",
                )
            }
        )
        self.coordinator = stove_coordinator
        self.entity_description = entity_description
        self.stove = stove_coordinator.stove
