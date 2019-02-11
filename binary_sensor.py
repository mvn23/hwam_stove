"""
Support for HWAM Stove binary sensors.

For more details about this platform, please refer to the documentation at
http://home-assistant.io/components/binary_sensor.hwam_stove/
"""
import logging

from homeassistant.components.binary_sensor import (ENTITY_ID_FORMAT,
                                                    BinarySensorDevice)
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from homeassistant.helpers.entity import async_generate_entity_id

from custom_components.hwam_stove import DATA_HWAM_STOVE, DATA_PYSTOVE

DEPENDENCIES = ['hwam_stove']

_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(hass, config, async_add_entities,
                               discovery_info=None):
    """Set up the HWAM Stove sensors."""
    if discovery_info is None:
        return
    pystove = hass.data[DATA_HWAM_STOVE][DATA_PYSTOVE]
    sensor_info = {
        # {name: [device_class, friendly_name format]}
        pystove.DATA_REFILL_ALARM: [None, "Refill Alarm {}"],
    }
    stove_device = discovery_info[0]
    sensor_list = discovery_info[1]
    sensors = []
    for var in sensor_list:
        device_class = sensor_info[var][0]
        name_format = sensor_info[var][1]
        entity_id = async_generate_entity_id(
            ENTITY_ID_FORMAT, name_format.format(stove_device.name),
            hass=hass)
        sensors.append(
            HwamStoveBinarySensor(entity_id, stove_device, var, device_class,
                                  name_format))
    async_add_entities(sensors)


class HwamStoveBinarySensor(BinarySensorDevice):
    """Represent an OpenTherm Gateway binary sensor."""

    def __init__(self, entity_id, stove_device, var, device_class,
                 name_format):
        """Initialize the binary sensor."""
        self._stove_device = stove_device
        self.entity_id = entity_id
        self._var = var
        self._state = None
        self._device_class = device_class
        self._name_format = name_format
        self._friendly_name = name_format.format(stove_device.stove.name)

    async def async_added_to_hass(self):
        """Subscribe to updates from the component."""
        _LOGGER.debug("Added HWAM Stove binary sensor %s", self.entity_id)
        async_dispatcher_connect(self.hass, self._stove_device.signal,
                                 self.receive_report)

    async def receive_report(self, status):
        """Handle status updates from the component."""
        self._state = bool(status.get(self._var))
        self.async_schedule_update_ha_state()

    @property
    def name(self):
        """Return the friendly name."""
        return self._friendly_name

    @property
    def is_on(self):
        """Return true if the binary sensor is on."""
        return self._state

    @property
    def device_class(self):
        """Return the class of this device."""
        return self._device_class

    @property
    def should_poll(self):
        """Return False because entity pushes its state."""
        return False
