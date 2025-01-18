"""
Support for HWAM Stove sensors.

For more details about this platform, please refer to the documentation at
https://github.com/mvn23/hwam_stove
"""

from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

from homeassistant.components.sensor import (
    ENTITY_ID_FORMAT,
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import async_generate_entity_id
from homeassistant.helpers.entity_platform import AddEntitiesCallback

import pystove

from . import CONF_NAME, DATA_HWAM_STOVE, DATA_STOVES
from .entity import HWAMStoveEntity, HWAMStoveEntityDescription


@dataclass(frozen=True, kw_only=True)
class HWAMStoveSensorEntityDescription(
    SensorEntityDescription,
    HWAMStoveEntityDescription,
):
    """Describes a hwam_stove sensor entity."""


SENSOR_DESCRIPTIONS = [
    HWAMStoveSensorEntityDescription(
        key=pystove.DATA_ALGORITHM,
        name_format="Algorithm {}",
    ),
    HWAMStoveSensorEntityDescription(
        key=pystove.DATA_BURN_LEVEL,
        name_format="Burn Level {}",
    ),
    HWAMStoveSensorEntityDescription(
        key=pystove.DATA_MAINTENANCE_ALARMS,
        name_format="Maintenance Alarms {}",
    ),
    HWAMStoveSensorEntityDescription(
        key=pystove.DATA_MESSAGE_ID,
        name_format="Message ID {}",
    ),
    HWAMStoveSensorEntityDescription(
        key=pystove.DATA_NEW_FIREWOOD_ESTIMATE,
        name_format="New Firewood Estimate {}",
    ),
    HWAMStoveSensorEntityDescription(
        key=pystove.DATA_NIGHT_BEGIN_TIME,
        name_format="Night Begin Time {}",
    ),
    HWAMStoveSensorEntityDescription(
        key=pystove.DATA_NIGHT_END_TIME,
        name_format="Night End Time {}",
    ),
    HWAMStoveSensorEntityDescription(
        key=pystove.DATA_NIGHT_LOWERING,
        name_format="Night Lowering {}",
    ),
    HWAMStoveSensorEntityDescription(
        key=pystove.DATA_OPERATION_MODE,
        name_format="Operation Mode {}",
    ),
    HWAMStoveSensorEntityDescription(
        key=pystove.DATA_OXYGEN_LEVEL,
        native_unit_of_measurement=PERCENTAGE,
        name_format="Oxygen Level {}",
    ),
    HWAMStoveSensorEntityDescription(
        key=pystove.DATA_PHASE,
        name_format="Phase {}",
    ),
    HWAMStoveSensorEntityDescription(
        key=pystove.DATA_REMOTE_VERSION,
        name_format="Remote Version {}",
    ),
    HWAMStoveSensorEntityDescription(
        key=pystove.DATA_ROOM_TEMPERATURE,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        name_format="Room Temperature {}",
    ),
    HWAMStoveSensorEntityDescription(
        key=pystove.DATA_SAFETY_ALARMS,
        name_format="Safety Alarms {}",
    ),
    HWAMStoveSensorEntityDescription(
        key=pystove.DATA_STOVE_TEMPERATURE,
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        name_format="Stove Temperature {}",
    ),
    HWAMStoveSensorEntityDescription(
        key=pystove.DATA_TIME_SINCE_REMOTE_MSG,
        name_format="Time Since Remote Message {}",
    ),
    HWAMStoveSensorEntityDescription(
        key=pystove.DATA_DATE_TIME,
        name_format="Date and time {}",
    ),
    HWAMStoveSensorEntityDescription(
        key=pystove.DATA_TIME_TO_NEW_FIREWOOD,
        name_format="Time To New Firewood {}",
    ),
    HWAMStoveSensorEntityDescription(
        key=pystove.DATA_VALVE1_POSITION,
        name_format="Valve 1 Position {}",
    ),
    HWAMStoveSensorEntityDescription(
        key=pystove.DATA_VALVE2_POSITION,
        name_format="Valve 2 Position {}",
    ),
    HWAMStoveSensorEntityDescription(
        key=pystove.DATA_VALVE3_POSITION,
        name_format="Valve 3 Position {}",
    ),
    HWAMStoveSensorEntityDescription(
        key=pystove.DATA_FIRMWARE_VERSION,
        name_format="Firmware Version {}",
    ),
]

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the HWAM Stove sensors."""

    stove_name = config_entry.data[CONF_NAME]
    stove_device = hass.data[DATA_HWAM_STOVE][DATA_STOVES][stove_name]
    async_add_entities(
        HwamStoveSensor(
            stove_device,
            description,
            async_generate_entity_id(
                ENTITY_ID_FORMAT, f"{description.key}_{stove_device.name}", hass=hass
            ),
        )
        for description in SENSOR_DESCRIPTIONS
    )


class HwamStoveSensor(HWAMStoveEntity, SensorEntity):
    """Representation of a HWAM Stove sensor."""

    def __init__(self, stove_device, entity_description, entity_id):
        """Initialize the sensor."""
        super().__init__(stove_device, entity_description)
        self.entity_id = entity_id
        self._var = entity_description.key
        self._value = None
        self._device_class = entity_description.device_class
        self._unit = entity_description.native_unit_of_measurement
        self._name_format = entity_description.name_format

    async def receive_report(self, status):
        """Handle status updates from the component."""
        value = status.get(self._var)
        if status.get(pystove.DATA_PHASE) != pystove.PHASE[4] and self._var in [
            pystove.DATA_NEW_FIREWOOD_ESTIMATE,
            pystove.DATA_TIME_TO_NEW_FIREWOOD,
        ]:
            value = "Wait for Glow phase..."
        elif isinstance(value, datetime):
            value = value.strftime("%-d %b, %-H:%M")
        elif isinstance(value, timedelta):
            value = f"{value}"
        self._value = value
        self.async_schedule_update_ha_state()

    @property
    def device_class(self):
        """Return the device class."""
        return self._device_class

    @property
    def native_value(self):
        """Return the state of the device."""
        return self._value

    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement."""
        return self._unit
