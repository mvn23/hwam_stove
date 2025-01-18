"""
Support for HWAM Stove binary sensors.

For more details about this platform, please refer to the documentation at
https://github.com/mvn23/hwam_stove
"""

from dataclasses import dataclass
import logging

from homeassistant.components.binary_sensor import (
    ENTITY_ID_FORMAT,
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import async_generate_entity_id
from homeassistant.helpers.entity_platform import AddEntitiesCallback

import pystove

from . import CONF_NAME, DATA_HWAM_STOVE, DATA_STOVES
from .entity import HWAMStoveEntity, HWAMStoveEntityDescription


@dataclass(frozen=True, kw_only=True)
class HWAMStoveBinarySensorEntityDescription(
    BinarySensorEntityDescription,
    HWAMStoveEntityDescription,
):
    """Describes a hwam_stove binary_sensor entity."""


@dataclass(frozen=True, kw_only=True)
class HWAMStoveBinarySensorListEntityDescription(
    HWAMStoveBinarySensorEntityDescription,
):
    """Describes a hwam_stove binary_sensor entity
    where the state source is a list element."""

    value_source_key: str
    alarm_str: str | None

BINARY_SENSOR_DESCRIPTIONS = [
    HWAMStoveBinarySensorEntityDescription(
        key=pystove.DATA_REFILL_ALARM,
        name_format="Refill Alarm {}",
    ),
]

BINARY_SENSOR_LIST_DESCRIPTIONS = [
    # General (any) maintenance alarm
    HWAMStoveBinarySensorListEntityDescription(
        key=pystove.DATA_MAINTENANCE_ALARMS,
        value_source_key=pystove.DATA_MAINTENANCE_ALARMS,
        device_class=BinarySensorDeviceClass.PROBLEM,
        name_format="Maintenance Alarm {}",
        alarm_str=None
    ),
    # Stove Backup Battery Low
    HWAMStoveBinarySensorListEntityDescription(
        key=f"{pystove.DATA_MAINTENANCE_ALARMS}_backup_battery_low",
        value_source_key=pystove.DATA_MAINTENANCE_ALARMS,
        device_class=BinarySensorDeviceClass.BATTERY,
        name_format="Stove Backup Battery Low {}",
        alarm_str=pystove.MAINTENANCE_ALARMS[0],
    ),
    # O2 Sensor Fault
    HWAMStoveBinarySensorListEntityDescription(
        key=f"{pystove.DATA_MAINTENANCE_ALARMS}_o2_sensor_fault",
        value_source_key=pystove.DATA_MAINTENANCE_ALARMS,
        device_class=BinarySensorDeviceClass.PROBLEM,
        name_format="O2 Sensor Fault {}",
        alarm_str=pystove.MAINTENANCE_ALARMS[1],
    ),
    # O2 Sensor Offset
    HWAMStoveBinarySensorListEntityDescription(
        key=f"{pystove.DATA_MAINTENANCE_ALARMS}_o2_sensor_offset",
        value_source_key=pystove.DATA_MAINTENANCE_ALARMS,
        device_class=BinarySensorDeviceClass.PROBLEM,
        name_format="O2 Sensor Offset {}",
        alarm_str=pystove.MAINTENANCE_ALARMS[2],
    ),
    # Stove Temperature Sensor Fault
    HWAMStoveBinarySensorListEntityDescription(
        key=f"{pystove.DATA_MAINTENANCE_ALARMS}_stove_temp_sensor_fault",
        value_source_key=pystove.DATA_MAINTENANCE_ALARMS,
        device_class=BinarySensorDeviceClass.PROBLEM,
        name_format="Stove Temperature Sensor Fault {}",
        alarm_str=pystove.MAINTENANCE_ALARMS[3],
    ),
    # Room Temperature Sensor Fault
    HWAMStoveBinarySensorListEntityDescription(
        key=f"{pystove.DATA_MAINTENANCE_ALARMS}_room_temp_sensor_fault",
        value_source_key=pystove.DATA_MAINTENANCE_ALARMS,
        device_class=BinarySensorDeviceClass.PROBLEM,
        name_format="Room Temperature Sensor Fault {}",
        alarm_str=pystove.MAINTENANCE_ALARMS[4],
    ),
    # Communication Fault
    HWAMStoveBinarySensorListEntityDescription(
        key=f"{pystove.DATA_MAINTENANCE_ALARMS}_communication_fault",
        value_source_key=pystove.DATA_MAINTENANCE_ALARMS,
        device_class=BinarySensorDeviceClass.PROBLEM,
        name_format="Communication Fault {}",
        alarm_str=pystove.MAINTENANCE_ALARMS[5],
    ),
    # Room Temperature Sensor Battery Low
    HWAMStoveBinarySensorListEntityDescription(
        key=f"{pystove.DATA_MAINTENANCE_ALARMS}_room_temp_sensor_battery_low",
        value_source_key=pystove.DATA_MAINTENANCE_ALARMS,
        device_class=BinarySensorDeviceClass.PROBLEM,
        name_format="Room Temperature Sensor Battery Low {}",
        alarm_str=pystove.MAINTENANCE_ALARMS[6],
    ),
    # General (any) safety alarm
    HWAMStoveBinarySensorListEntityDescription(
        key=pystove.DATA_SAFETY_ALARMS,
        value_source_key=pystove.DATA_SAFETY_ALARMS,
        device_class=BinarySensorDeviceClass.SAFETY,
        name_format="Safety Alarm {}",
        alarm_str=None,
    ),
    # Valve Fault, same as [1] and [2].
    HWAMStoveBinarySensorListEntityDescription(
        key=f"{pystove.DATA_SAFETY_ALARMS}_valve_fault",
        value_source_key=pystove.DATA_SAFETY_ALARMS,
        device_class=BinarySensorDeviceClass.SAFETY,
        name_format="Valve Fault {}",
        alarm_str=pystove.SAFETY_ALARMS[0],
    ),
    # Bad Configuration
    HWAMStoveBinarySensorListEntityDescription(
        key=f"{pystove.DATA_SAFETY_ALARMS}_bad_configuration",
        value_source_key=pystove.DATA_SAFETY_ALARMS,
        device_class=BinarySensorDeviceClass.SAFETY,
        name_format="Bad Configuration {}",
        alarm_str=pystove.SAFETY_ALARMS[3],
    ),
    # Valve Disconnect, same as [5] and [6]
    HWAMStoveBinarySensorListEntityDescription(
        key=f"{pystove.DATA_SAFETY_ALARMS}_valve_disconnect",
        value_source_key=pystove.DATA_SAFETY_ALARMS,
        device_class=BinarySensorDeviceClass.SAFETY,
        name_format="Valve Disconnect {}",
        alarm_str=pystove.SAFETY_ALARMS[4],
    ),
    # Valve Calibration Error, same as [8] and [9]
    HWAMStoveBinarySensorListEntityDescription(
        key=f"{pystove.DATA_SAFETY_ALARMS}_valve_calibration_error",
        value_source_key=pystove.DATA_SAFETY_ALARMS,
        device_class=BinarySensorDeviceClass.SAFETY,
        name_format="Valve Calibration Error {}",
        alarm_str=pystove.SAFETY_ALARMS[7],
    ),
    # Overheating
    HWAMStoveBinarySensorListEntityDescription(
        key=f"{pystove.DATA_SAFETY_ALARMS}_stove_overheat",
        value_source_key=pystove.DATA_SAFETY_ALARMS,
        device_class=BinarySensorDeviceClass.SAFETY,
        name_format="Stove Overheat {}",
        alarm_str=pystove.SAFETY_ALARMS[10],
    ),
    # Door Open Too Long
    HWAMStoveBinarySensorListEntityDescription(
        key=f"{pystove.DATA_SAFETY_ALARMS}_door_open_too_long",
        value_source_key=pystove.DATA_SAFETY_ALARMS,
        device_class=BinarySensorDeviceClass.SAFETY,
        name_format="Door Open Too Long {}",
        alarm_str=pystove.SAFETY_ALARMS[11],
    ),
    # Manual Safety Alarm
    HWAMStoveBinarySensorListEntityDescription(
        key=f"{pystove.DATA_SAFETY_ALARMS}_manual_safety_alarm",
        value_source_key=pystove.DATA_SAFETY_ALARMS,
        device_class=BinarySensorDeviceClass.SAFETY,
        name_format="Manual Safety Alarm {}",
        alarm_str=pystove.SAFETY_ALARMS[12],
    ),
    # Stove Sensor Fault
    HWAMStoveBinarySensorListEntityDescription(
        key=f"{pystove.DATA_SAFETY_ALARMS}_stove_sensor_fault",
        value_source_key=pystove.DATA_SAFETY_ALARMS,
        device_class=BinarySensorDeviceClass.SAFETY,
        name_format="Stove Sensor Fault {}",
        alarm_str=pystove.SAFETY_ALARMS[13],
    ),
]

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the HWAM Stove binary sensors."""
    stove_name = config_entry.data[CONF_NAME]
    stove_hub = hass.data[DATA_HWAM_STOVE][DATA_STOVES][stove_name]
    binary_sensors = []
    for entity_description in BINARY_SENSOR_DESCRIPTIONS:
        binary_sensors.append(
            HwamStoveBinarySensor(
                stove_hub,
                entity_description,
                async_generate_entity_id(
                    ENTITY_ID_FORMAT,
                    f"{entity_description.key}_{stove_hub.name}",
                    hass=hass,
                )
            )
        )
    for description in BINARY_SENSOR_LIST_DESCRIPTIONS:
        if description.alarm_str is None:
            entity_id = async_generate_entity_id(
                ENTITY_ID_FORMAT,
                f"{description.key}_{stove_hub.name}",
                hass=hass,
            )
        else:
            entity_id = async_generate_entity_id(
                ENTITY_ID_FORMAT,
                f"{description.key}_{description.alarm_str}_{stove_hub.name}",
                hass=hass,
            )
        binary_sensors.append(
            HwamStoveAlarmSensor(stove_hub, description, entity_id)
        )
    async_add_entities(binary_sensors)


class HwamStoveBinarySensor(HWAMStoveEntity, BinarySensorEntity):
    """Representation of a HWAM Stove binary sensor."""

    def __init__(self, stove_device, entity_description, entity_id):
        """Initialize the binary sensor."""
        super().__init__(stove_device, entity_description)
        self.entity_id = entity_id
        self._var = entity_description.key
        self._state = None
        self._device_class = entity_description.device_class

    async def receive_report(self, status):
        """Handle status updates from the component."""
        self._state = bool(status.get(self._var))
        self.async_schedule_update_ha_state()

    @property
    def is_on(self):
        """Return true if the binary sensor is on."""
        return self._state

    @property
    def device_class(self):
        """Return the class of this device."""
        return self._device_class


class HwamStoveAlarmSensor(HwamStoveBinarySensor):
    """Representation of a HWAM Stove Alarm binary sensor."""

    def __init__(self, stove_device, entity_description, entity_id):
        super().__init__(stove_device, entity_description, entity_id)
        self._alarm_str = entity_description.alarm_str

    async def receive_report(self, status):
        """Handle status updates from the component."""
        if self._alarm_str:
            self._state = self._alarm_str in status.get(self._var, [])
        else:
            self._state = status.get(self._var, []) != []
        self.async_schedule_update_ha_state()
