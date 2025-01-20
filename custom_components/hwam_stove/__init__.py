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
    CONF_ID,
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

ATTR_STOVE_ID = "stove_id"

SERVICE_SET_CLOCK = "set_clock"

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
    Platform.TIME,
]

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, config_entry: ConfigEntry) -> bool:
    """Set up the HWAM Stove component from a config entry."""
    if DOMAIN not in hass.data:
        hass.data[DOMAIN] = {DATA_STOVES: {}}

    stove_hub = StoveCoordinator(hass, config_entry)
    hass.data[DOMAIN][DATA_STOVES][config_entry.data[CONF_ID]] = stove_hub

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

    service_set_clock_schema = vol.Schema(
        {
            vol.Required(ATTR_STOVE_ID): vol.All(
                cv.string, vol.In(hass.data[DOMAIN][DATA_STOVES])
            ),
            vol.Optional(ATTR_DATE, default=date.today()): cv.date,
            vol.Optional(ATTR_TIME, default=datetime.now().time()): cv.time,
        }
    )

    async def set_device_clock(call: ServiceCall) -> None:
        """Set the clock on the stove."""
        stove_device = hass.data[DOMAIN][DATA_STOVES][call.data[ATTR_STOVE_ID]]
        if stove_device is None:
            return
        attr_date = call.data[ATTR_DATE]
        attr_time = call.data[ATTR_TIME]
        await stove_device.stove.set_time(datetime.combine(attr_date, attr_time))

    hass.services.async_register(
        DOMAIN, SERVICE_SET_CLOCK, set_device_clock, service_set_clock_schema
    )
