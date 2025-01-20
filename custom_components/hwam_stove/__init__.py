"""
Support for Hwam SmartControl stoves.

For more details about this component, please refer to the documentation at
https://github.com/mvn23/hwam_stove
"""

from datetime import date, datetime
import logging

from homeassistant.config_entries import SOURCE_IMPORT, ConfigEntry
from homeassistant.const import (
    ATTR_DATE,
    ATTR_TIME,
    CONF_HOST,
    CONF_MONITORED_VARIABLES,
    CONF_NAME,
    Platform,
)
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv, issue_registry as ir
from homeassistant.helpers.typing import ConfigType
import voluptuous as vol

from .const import DATA_STOVES, DOMAIN
from .coordinator import StoveCoordinator

ATTR_START_TIME = "start_time"
ATTR_END_TIME = "end_time"
ATTR_STOVE_NAME = "stove_name"

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
        ),
    },
    extra=vol.ALLOW_EXTRA,
)

PLATFORMS = [
    Platform.BINARY_SENSOR,
    Platform.FAN,
    Platform.SENSOR,
    Platform.SWITCH,
]

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up the HWAM Stove component from a config entry."""
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {DATA_STOVES: {}}

    stove_hub = StoveCoordinator(hass, config_entry)
    hass.data[DOMAIN][DATA_STOVES][config_entry.data[CONF_NAME]] = stove_hub

    await stove_hub.async_config_entry_first_refresh()

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


def register_services(hass: HomeAssistant) -> None:
    """Register HWAM Stove services."""

    service_set_night_lowering_hours_schema = vol.All(
        vol.Schema(
            {
                vol.Required(ATTR_STOVE_NAME): vol.All(
                    cv.string, vol.In(hass.data[DOMAIN][DATA_STOVES])
                ),
                vol.Optional(ATTR_START_TIME): cv.time,
                vol.Optional(ATTR_END_TIME): cv.time,
            },
        ),
        cv.has_at_least_one_key(ATTR_START_TIME, ATTR_END_TIME),
    )
    service_set_clock_schema = vol.Schema(
        {
            vol.Required(ATTR_STOVE_NAME): vol.All(
                cv.string, vol.In(hass.data[DOMAIN][DATA_STOVES])
            ),
            vol.Optional(ATTR_DATE, default=date.today()): cv.date,
            vol.Optional(ATTR_TIME, default=datetime.now().time()): cv.time,
        }
    )

    async def set_night_lowering_hours(call: ServiceCall) -> None:
        """Set night lowering hours on the stove."""
        stove_name = call.data[ATTR_STOVE_NAME]
        stove_device = hass.data[DOMAIN][DATA_STOVES].get(stove_name)
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

    async def set_device_clock(call: ServiceCall) -> None:
        """Set the clock on the stove."""
        stove_name = call.data[ATTR_STOVE_NAME]
        stove_device = hass.data[DOMAIN][DATA_STOVES].get(stove_name)
        if stove_device is None:
            return
        attr_date = call.data[ATTR_DATE]
        attr_time = call.data[ATTR_TIME]
        await stove_device.stove.set_time(datetime.combine(attr_date, attr_time))

    hass.services.async_register(
        DOMAIN, SERVICE_SET_CLOCK, set_device_clock, service_set_clock_schema
    )
