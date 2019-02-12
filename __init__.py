"""
Support for Hwam SmartControl stoves.

For more details about this component, please refer to the documentation at
http://home-assistant.io/components/hwam_stove/
"""
import logging
from datetime import timedelta

import homeassistant.helpers.config_validation as cv
import voluptuous as vol

from homeassistant.components.binary_sensor import DOMAIN as COMP_BINARY_SENSOR
from homeassistant.components.fan import DOMAIN as COMP_FAN
from homeassistant.components.sensor import DOMAIN as COMP_SENSOR
from homeassistant.const import (CONF_HOST, CONF_MONITORED_VARIABLES,
                                 CONF_NAME, EVENT_HOMEASSISTANT_STOP)
from homeassistant.helpers.discovery import async_load_platform
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import async_track_time_interval

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
        stove_device = await StoveDevice.create(hass, name, cfg, config)
        hass.data[DATA_HWAM_STOVE][DATA_STOVES][name] = stove_device
    return True


class StoveDevice:
    """Abstract description of a stove component."""

    @classmethod
    async def create(cls, hass, name, stove_config, hass_config):
        """Create a stove component."""
        self = cls()
        self.pystove = hass.data[DATA_HWAM_STOVE][DATA_PYSTOVE]
        self.hass = hass
        self.name = name
        self.config = stove_config
        self.signal = 'hwam_stove_update_{}'.format(self.config[CONF_HOST])
        self.stove = await pystove.Stove.create(self.config[CONF_HOST],
                                                skip_ident=True)

        async def cleanup(event):
            """Clean up stove object."""
            await self.stove.destroy()
        hass.bus.async_listen(EVENT_HOMEASSISTANT_STOP, cleanup)
        hass.async_create_task(self.init_stove(hass_config))
        return self

    async def init_stove(self, hass_config):
        """Run ident routine and schedule updates."""
        await self.stove._identify()
        self.hass.async_create_task(async_load_platform(
            self.hass, COMP_FAN, DOMAIN, self, hass_config))
        monitored_vars = self.config.get(CONF_MONITORED_VARIABLES)
        if monitored_vars:
            self.hass.async_create_task(
                self.setup_monitored_vars(monitored_vars, hass_config))
        self.hass.async_create_task(self.update())
        async_track_time_interval(self.hass, self.update,
                                  timedelta(seconds=10))

    async def setup_monitored_vars(self, monitored_vars, hass_config):
        """Add monitored_vars as sensors and binary sensors."""
        pystove = self.pystove
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
                pystove.DATA_REMOTE_VERSION,
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
            self.hass.async_create_task(async_load_platform(
                self.hass, COMP_BINARY_SENSOR, DOMAIN, [self, binary_sensors],
                hass_config))
        if sensors:
            self.hass.async_create_task(async_load_platform(
                self.hass, COMP_SENSOR, DOMAIN, [self, sensors],
                hass_config))

    async def update(self, *_):
        """Update and dispatch stove info."""
        data = await self.stove.get_data()
        async_dispatcher_send(self.hass, self.signal, data)
