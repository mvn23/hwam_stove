"""OpenTherm Gateway config flow."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_ID, CONF_NAME
import homeassistant.helpers.config_validation as cv
import voluptuous as vol

from pystove import pystove

from .const import DOMAIN


class HWAMStoveConfigFlow(ConfigFlow, domain=DOMAIN):  # type: ignore[call-arg]
    """HWAM Stove Config Flow."""

    VERSION = 1

    async def async_step_init(
        self, info: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle config flow initiation."""
        if info:
            name = info[CONF_NAME]
            host = info[CONF_HOST]
            stove_id = cv.slugify(info.get(CONF_NAME, name))

            entries = [e.data for e in self._async_current_entries()]

            if stove_id in [e[CONF_ID] for e in entries]:
                return self._show_form({"base": "id_exists"})

            if host in [e[CONF_HOST] for e in entries]:
                return self._show_form({"base": "already_configured"})

            async def test_connection() -> None:
                """Try to connect to the OpenTherm Gateway."""
                stove = await pystove.Stove.create(host)
                status = (
                    stove.name != pystove.UNKNOWN and stove.stove_ip != pystove.UNKNOWN  # type: ignore[attr-defined]
                )
                await stove.destroy()
                if not status:
                    raise ConnectionError

            try:
                await test_connection()
            except ConnectionError:
                return self._show_form({"base": "cannot_connect"})

            return self._create_entry(stove_id, name, host)

        return self._show_form()

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle manual initiation of the config flow."""
        return await self.async_step_init(user_input)

    async def async_step_import(self, import_data: dict[str, Any]) -> ConfigFlowResult:
        """Import an OpenTherm Gateway device as a config entry.

        This flow is triggered by `async_setup` for configured devices.
        """
        formatted_config = {
            CONF_NAME: import_data[CONF_NAME],
            CONF_HOST: import_data[CONF_HOST],
        }
        return await self.async_step_init(info=formatted_config)

    def _show_form(self, errors: dict[str, str] | None = None) -> ConfigFlowResult:
        """Show the config flow form with possible errors."""
        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_NAME): str,
                    vol.Required(CONF_HOST): str,
                    vol.Optional(CONF_ID): str,
                }
            ),
            errors=errors or {},
        )

    def _create_entry(self, stove_id: str, name: str, host: str) -> ConfigFlowResult:
        """Create entry for the HWAM Stove."""
        return self.async_create_entry(
            title=name, data={CONF_ID: stove_id, CONF_HOST: host, CONF_NAME: name}
        )
