"""Common HWAM Stove entity properties."""

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity import EntityDescription
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, StoveDeviceIdentifier
from .coordinator import StoveCoordinator


class HWAMStoveEntityDescription(EntityDescription):
    """Describe common hwam_stove entity properties."""

    device_identifier: StoveDeviceIdentifier


class HWAMStoveCoordinatorEntity(CoordinatorEntity[StoveCoordinator]):
    """Represent a hwam_stove entity."""

    _attr_has_entity_name = True
    entity_description: HWAMStoveEntityDescription

    def __init__(
        self,
        stove_coordinator: StoveCoordinator,
        entity_description: HWAMStoveEntityDescription,
    ) -> None:
        super().__init__(stove_coordinator)
        self._attr_unique_id = f"{stove_coordinator.hub_id}-{entity_description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={
                (
                    DOMAIN,
                    f"{stove_coordinator.hub_id}-{entity_description.device_identifier}",
                )
            }
        )
        self.coordinator = stove_coordinator
        self.entity_description = entity_description
