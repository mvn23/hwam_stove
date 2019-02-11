"""
Support for Hwam SmartControl stoves.

For more details about this component, please refer to the documentation at
http://home-assistant.io/components/hwam_stove/
"""
import logging
from datetime import datetime

import homeassistant.helpers.config_validation as cv
import voluptuous as vol

from homeassistant.components.binary_sensor import DOMAIN as COMP_BINARY_SENSOR
from homeassistant.components.sensor import DOMAIN as COMP_SENSOR
from homeassistant.const import (CONF_HOST, CONF_MONITORED_VARIABLES,
                                 CONF_NAME, EVENT_HOMEASSISTANT_STOP)
from homeassistant.helpers.discovery import async_load_platform
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import async_track_utc_time_change

DOMAIN = 'hwam_stove'

DATA_HWAM_STOVE = 'hwam_stove'
DATA_PYSTOVE = 'pystove'
DATA_STOVES = 'stoves'

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        cv.string: vol.Schema({
            vol.Required(CONF_HOST): cv.string,
            vol.Optional(CONF_NAME): cv.string,
            vol.Optional(CONF_MONITORED_VARIABLES, default=[]): vol.All(
                cv.ensure_list, [cv.string]),
        }),
    }, cv.ensure_list),
}, extra=vol.ALLOW_EXTRA)

# REQUIREMENTS = ['pystove']

_LOGGER = logging.getLogger(__name__)


async def async_setup(hass, config):
    """Set up the HWAM Stove component."""
    from .pystove import pystove
    hass.data[DATA_HWAM_STOVE] = {
        DATA_STOVES: {},
        DATA_PYSTOVE: pystove,
    }
    conf = config[DOMAIN]
    for name, cfg in conf.items():
        stove_device = await StoveDevice.create(hass, name, cfg[CONF_HOST])
        hass.data[DATA_HWAM_STOVE][DATA_STOVES][name] = stove_device
        hass.async_create_task(async_load_platform(
            hass, 'fan', DOMAIN, stove_device, config))
        monitored_vars = cfg.get(CONF_MONITORED_VARIABLES)
        if monitored_vars:
            hass.async_create_task(setup_monitored_vars(
                hass, config, stove_device, monitored_vars))
    return True


async def setup_monitored_vars(hass, config, stove_device, monitored_vars):
    """Add monitored_vars as sensors and binary sensors."""
    pystove = hass.data[DATA_HWAM_STOVE][DATA_PYSTOVE]
    sensor_type_map = {
        COMP_BINARY_SENSOR: [
            pystove.DATA_REFILL_ALARM,
            pystove.DATA_REMOTE_REFILL_ALARM,
            pystove.DATA_UPDATING,
        ],
        COMP_SENSOR: [
            pystove.DATA_ALGORITHM,
            pystove.DATA_BURN_LEVEL,
            pystove.DATA_MAINTENANCE_ALARMS,
            pystove.DATA_MESSAGE_ID,
            pystove.DATA_NEW_FIREWOOD_ESTIMATE,
            pystove.DATA_NIGHT_BEGIN_TIME,
            pystove.DATA_NIGHT_END_TIME,
            pystove.DATA_NIGHT_LOWERING,
            pystove.DATA_OPERATION_MODE,
            pystove.DATA_OXYGEN_LEVEL,
            pystove.DATA_PHASE,
            pystove.DATA_ROOM_TEMPERATURE,
            pystove.DATA_SAFETY_ALARMS,
            pystove.DATA_STOVE_TEMPERATURE,
            pystove.DATA_TIME_SINCE_REMOTE_MSG,
            pystove.DATA_DATE_TIME,
            pystove.DATA_TIME_TO_NEW_FIREWOOD,
            pystove.DATA_VALVE1_POSITION,
            pystove.DATA_VALVE2_POSITION,
            pystove.DATA_VALVE3_POSITION,
            pystove.DATA_FIRMWARE_VERSION,
        ]
    }
    binary_sensors = []
    sensors = []
    for var in monitored_vars:
        if var in sensor_type_map[COMP_SENSOR]:
            sensors.append(var)
        elif var in sensor_type_map[COMP_BINARY_SENSOR]:
            binary_sensors.append(var)
        else:
            _LOGGER.error("Monitored variable not supported: %s", var)
    if binary_sensors:
        hass.async_create_task(async_load_platform(
            hass, COMP_BINARY_SENSOR, DOMAIN, [stove_device, binary_sensors],
            config))
    if sensors:
        hass.async_create_task(async_load_platform(
            hass, COMP_SENSOR, DOMAIN, [stove_device, sensors], config))


class StoveDevice:
    """Abstract description of a stove component."""

    @classmethod
    async def create(cls, hass, name, stove_host):
        """Create a stove component."""
        pystove = hass.data[DATA_HWAM_STOVE][DATA_PYSTOVE]
        self = cls()
        self.name = name
        self.host = stove_host
        self.hass = hass
        self.signal = 'hwam_stove_update_{}'.format(self.host)
        self.stove = await pystove.Stove.create(stove_host, skip_ident=True)

        async def cleanup(event):
            """Clean up stove object."""
            await self.stove.destroy()
        hass.bus.async_listen(EVENT_HOMEASSISTANT_STOP, cleanup)
        hass.async_create_task(self.init_stove())
        return self

    async def init_stove(self):
        """Run ident routine and schedule updates."""
        await self.stove._identify()
        now = datetime.now()
        async_track_utc_time_change(self.hass, self.update,
                                    second=range(now.second % 10, 60, 10))

    async def update(self, *_):
        """Update and dispatch stove info."""
        data = await self.stove.get_data()
        async_dispatcher_send(self.hass, self.signal, data)
