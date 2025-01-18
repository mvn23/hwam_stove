"""Common HWAM Stove entity properties."""

from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import Entity, EntityDescription

from . import DOMAIN, StoveDevice, StoveDeviceIdentifier


class HWAMStoveEntityDescription(EntityDescription):
    """Describe common hwam_stove entity properties."""

    name_format: str
    device_identifier: StoveDeviceIdentifier


class HWAMStoveEntity(Entity):
    """Represent a hwam_stove entity."""

    _attr_should_poll = False
    entity_description: HWAMStoveEntityDescription

    def __init__(
        self,
        stove_device: StoveDevice,
        entity_description: HWAMStoveEntityDescription,
    ) -> None:
        self._attr_unique_id = f"{stove_device.hub_id}-{entity_description.key}"
        self._attr_device_info = DeviceInfo(
            identifiers={
                (
                    DOMAIN,
                    f"{stove_device.hub_id}-{entity_description.device_identifier}"
                )
            }
        )
        self._stove_device = stove_device
        self.entity_description = entity_description

    async def async_added_to_hass(self):
        """Subscribe to updates."""
        self.async_on_remove(
            async_dispatcher_connect(
                self.hass, self._stove_device.signal, self.receive_report
            )
        )

    async def receive_report(self, data):
        """Receive updates from the component."""
        # Must be implemented at the platform level.
        raise NotImplementedError

    @property
    def name(self) -> str:
        """Set the friendly name."""
        return self.entity_description.name_format.format(self._stove_device.stove.name)
