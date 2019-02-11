"""
Support for Hwam SmartControl stoves.

For more details about this component, please refer to the documentation at
http://home-assistant.io/components/hwam_stove/
"""
import asyncio
import logging
from datetime import datetime, date

import voluptuous as vol

from homeassistant.const import (
    ATTR_DATE, ATTR_ID, ATTR_TEMPERATURE, ATTR_TIME, CONF_HOST,
    CONF_MONITORED_VARIABLES, CONF_NAME, EVENT_HOMEASSISTANT_STOP,
    PRECISION_HALVES, PRECISION_TENTHS, PRECISION_WHOLE)
from homeassistant.helpers.discovery import async_load_platform
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import async_track_utc_time_change

import homeassistant.helpers.config_validation as cv

DOMAIN = 'hwam_stove'

DATA_HWAM_STOVE = 'hwam_stove'
DATA_LATEST_STATUS = 'latest_status'

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
    """Set up the OpenTherm Gateway component."""
    conf = config[DOMAIN]
    hass.data[DATA_HWAM_STOVE] = {}
    for name, cfg in conf.items():
        stove = await StoveDevice.create(hass, name, cfg[CONF_HOST])
        hass.data[DATA_HWAM_STOVE][name] = stove
        hass.async_create_task(async_load_platform(
            hass, 'fan', DOMAIN, stove, config))
    return True


class StoveDevice:
    """Abstract description of a stove component."""

    @classmethod
    async def create(cls, hass, name, stove_host):
        """Create a stove component."""
        from .pystove import Stove
        self = cls()
        self.name = name
        self.host = stove_host
        self.hass = hass
        self.signal = 'hwam_stove_update_{}'.format(self.host)
        self.stove = await Stove.create(stove_host, skip_ident=True)

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
