"""
Support for Hwam SmartControl stoves.

For more details about this component, please refer to the documentation at
https://github.com/mvn23/hwam_stove
"""

from datetime import date, datetime, timedelta
from enum import StrEnum
import logging

from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.const import (
    ATTR_DATE,
    ATTR_TIME,
    CONF_HOST,
    CONF_ID,
    CONF_MONITORED_VARIABLES,
    CONF_NAME,
    EVENT_HOMEASSISTANT_STOP,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers import (
    config_validation as cv,
    device_registry as dr,
    issue_registry as ir,
)
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.helpers.event import async_track_time_interval
from homeassistant.helpers.typing import ConfigType
import voluptuous as vol

from pystove import pystove

DOMAIN = "hwam_stove"

ATTR_START_TIME = "start_time"
ATTR_END_TIME = "end_time"
ATTR_STOVE_NAME = "stove_name"

DATA_HWAM_STOVE = "hwam_stove"
DATA_STOVES = "stoves"

SERVICE_DISABLE_NIGHT_LOWERING = "disable_night_lowering"
SERVICE_ENABLE_NIGHT_LOWERING = "enable_night_lowering"
SERVICE_DISABLE_REMOTE_REFILL_ALARM = "disable_remote_refill_alarm"
SERVICE_ENABLE_REMOTE_REFILL_ALARM = "enable_remote_refill_alarm"
SERVICE_SET_CLOCK = "set_clock"
SERVICE_SET_NIGHT_LOWERING_HOURS = "set_night_lowering_hours"

CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            {
                cv.string: vol.Schema(
                    {
                        vol.Required(CONF_HOST): cv.string,
                        vol.Optional(CONF_NAME): cv.string,
                        vol.Optional(CONF_MONITORED_VARIABLES, default=[]): vol.All(
                            cv.ensure_list, [cv.string]
                        ),
                    }
                ),
            },
            cv.ensure_list,
        ),
    },
    extra=vol.ALLOW_EXTRA,
)

PLATFORMS = [
    "binary_sensor",
    "fan",
    "sensor",
]

_LOGGER = logging.getLogger(__name__)


class StoveDeviceIdentifier(StrEnum):
    """Device identification strings."""

    REMOTE = "remote"
    STOVE = "stove"


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up the HWAM Stove component from a config entry."""
    if DATA_HWAM_STOVE not in hass.data:
        hass.data[DATA_HWAM_STOVE] = {DATA_STOVES: {}}

    stove_hub = await StoveDevice.create(hass, config_entry)
    hass.data[DATA_HWAM_STOVE][DATA_STOVES][config_entry.data[CONF_NAME]] = stove_hub

    await hass.config_entries.async_forward_entry_setups(config_entry, PLATFORMS)

    register_services(hass)
    return True


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the HWAM Stove component."""
    if DOMAIN in config:
        ir.async_create_issue(
            hass,
            DOMAIN,
            "deprecated_import_from_configuration_yaml",
            is_fixable=False,
            is_persistent=False,
            severity=ir.IssueSeverity.WARNING,
            translation_key="deprecated_import_from_configuration_yaml",
        )
    if not hass.config_entries.async_entries(DOMAIN) and DOMAIN in config:
        conf = config[DOMAIN]
        for device_id, device_config in conf.items():
            device_config[CONF_NAME] = device_id

            hass.async_create_task(
                hass.config_entries.flow.async_init(
                    DOMAIN, context={"source": SOURCE_IMPORT}, data=device_config
                )
            )
    return True


def register_services(hass):
    """Register HWAM Stove services."""

    service_set_night_lowering_hours_schema = vol.Schema(
        {
            vol.Required(ATTR_STOVE_NAME): vol.All(
                cv.string, vol.In(hass.data[DATA_HWAM_STOVE][DATA_STOVES])
            ),
            vol.Optional(ATTR_START_TIME): cv.time,
            vol.Optional(ATTR_END_TIME): cv.time,
        },
        cv.has_at_least_one_key(ATTR_START_TIME, ATTR_END_TIME),
    )
    service_set_clock_schema = vol.Schema(
        {
            vol.Required(ATTR_STOVE_NAME): vol.All(
                cv.string, vol.In(hass.data[DATA_HWAM_STOVE][DATA_STOVES])
            ),
            vol.Optional(ATTR_DATE, default=date.today()): cv.date,
            vol.Optional(ATTR_TIME, default=datetime.now().time()): cv.time,
        }
    )
    service_basic_schema = vol.Schema(
        {
            vol.Required(ATTR_STOVE_NAME): vol.All(
                cv.string, vol.In(hass.data[DATA_HWAM_STOVE][DATA_STOVES])
            ),
        }
    )

    async def set_night_lowering_hours(call):
        """Set night lowering hours on the stove."""
        stove_name = call.data[ATTR_STOVE_NAME]
        stove_device = hass.data[DATA_HWAM_STOVE][DATA_STOVES].get(stove_name)
        if stove_device is None:
            return
        attr_start = call.data.get(ATTR_START_TIME)
        attr_end = call.data.get(ATTR_END_TIME)
        await stove_device.stove.set_night_lowering_hours(attr_start, attr_end)

    hass.services.async_register(
        DOMAIN,
        SERVICE_SET_NIGHT_LOWERING_HOURS,
        set_night_lowering_hours,
        service_set_night_lowering_hours_schema,
    )

    async def enable_night_lowering(call):
        """Enable night lowering."""
        stove_name = call.data[ATTR_STOVE_NAME]
        stove_device = hass.data[DATA_HWAM_STOVE][DATA_STOVES].get(stove_name)
        if stove_device is None:
            return
        await stove_device.stove.set_night_lowering(True)

    hass.services.async_register(
        DOMAIN,
        SERVICE_ENABLE_NIGHT_LOWERING,
        enable_night_lowering,
        service_basic_schema,
    )

    async def disable_night_lowering(call):
        """Disable night lowering."""
        stove_name = call.data[ATTR_STOVE_NAME]
        stove_device = hass.data[DATA_HWAM_STOVE][DATA_STOVES].get(stove_name)
        if stove_device is None:
            return
        await stove_device.stove.set_night_lowering(False)

    hass.services.async_register(
        DOMAIN,
        SERVICE_DISABLE_NIGHT_LOWERING,
        disable_night_lowering,
        service_basic_schema,
    )

    async def enable_remote_refill_alarm(call):
        """Enable remote refill alarm."""
        stove_name = call.data[ATTR_STOVE_NAME]
        stove_device = hass.data[DATA_HWAM_STOVE][DATA_STOVES].get(stove_name)
        if stove_device is None:
            return
        await stove_device.stove.set_remote_refill_alarm(True)

    hass.services.async_register(
        DOMAIN,
        SERVICE_ENABLE_REMOTE_REFILL_ALARM,
        enable_remote_refill_alarm,
        service_basic_schema,
    )

    async def disable_remote_refill_alarm(call):
        """Disable remote refill alarm."""
        stove_name = call.data[ATTR_STOVE_NAME]
        stove_device = hass.data[DATA_HWAM_STOVE][DATA_STOVES].get(stove_name)
        if stove_device is None:
            return
        await stove_device.stove.set_remote_refill_alarm(False)

    hass.services.async_register(
        DOMAIN,
        SERVICE_DISABLE_REMOTE_REFILL_ALARM,
        disable_remote_refill_alarm,
        service_basic_schema,
    )

    async def set_device_clock(call):
        """Set the clock on the stove."""
        stove_name = call.data[ATTR_STOVE_NAME]
        stove_device = hass.data[DATA_HWAM_STOVE][DATA_STOVES].get(stove_name)
        if stove_device is None:
            return
        attr_date = call.data[ATTR_DATE]
        attr_time = call.data[ATTR_TIME]
        await stove_device.stove.set_time(datetime.combine(attr_date, attr_time))

    hass.services.async_register(
        DOMAIN, SERVICE_SET_CLOCK, set_device_clock, service_set_clock_schema
    )


class StoveDevice:
    """Abstract description of a stove component."""

    @classmethod
    async def create(cls, hass, config_entry):
        """Create a stove component."""
        self = cls()
        self.config_entry_id = config_entry.entry_id
        self.device_entry = None
        self.hass = hass
        self.name = config_entry.data[CONF_NAME]
        self.signal = f"hwam_stove_update_{config_entry.data[CONF_HOST]}"
        self.hub_id = config_entry.data[CONF_ID]
        self.stove = await pystove.Stove.create(
            config_entry.data[CONF_HOST], skip_ident=True
        )

        async def cleanup(event):
            """Clean up stove object."""
            await self.stove.destroy()

        hass.bus.async_listen(EVENT_HOMEASSISTANT_STOP, cleanup)
        hass.async_create_task(self.init_stove())
        return self

    async def init_stove(self):
        """Run ident routine and schedule updates."""
        await self.stove._identify()

        dev_reg = dr.async_get(self.hass)
        self.stove_device_entry = dev_reg.async_get_or_create(
            config_entry_id=self.config_entry_id,
            identifiers={(DOMAIN, f"{self.hub_id}-{StoveDeviceIdentifier.STOVE}")},
            manufacturer="HWAM",
            model=f"{self.stove.series}",
            translation_key="hwam_stove_device",
        )
        self.remote_device_entry = dev_reg.async_get_or_create(
            config_entry_id=self.config_entry_id,
            identifiers={(DOMAIN, f"{self.hub_id}-{StoveDeviceIdentifier.REMOTE}")},
            manufacturer="HWAM",
            translation_key="hwam_remote_device",
        )

        self.hass.loop.create_task(self.update())
        async_track_time_interval(self.hass, self.update, timedelta(seconds=10))

    async def update(self, *_):
        """Update and dispatch stove info."""
        data = await self.stove.get_data()
        if data is None:
            _LOGGER.error("Got empty response, skipping dispatch.")
            return
        async_dispatcher_send(self.hass, self.signal, data)

        dev_reg = dr.async_get(self.hass)
        dev_reg.async_update_device(
            self.stove_device_entry.id,
            sw_version=data.get(pystove.DATA_FIRMWARE_VERSION),
        )
        dev_reg.async_update_device(
            self.remote_device_entry.id,
            sw_version=data.get(pystove.DATA_REMOTE_VERSION),
        )
