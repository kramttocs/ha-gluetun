"""Config flow for the Gluetun integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlowWithReload
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import (
    CONF_HOST,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_SSL,
    CONF_USERNAME,
    CONF_VERIFY_SSL,
    DEFAULT_NAME,
    DEFAULT_PORT,
    DOMAIN,
)


USER_STEP_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): selector.TextSelector(
            selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT)
        ),
        vol.Required(CONF_PORT, default=DEFAULT_PORT): selector.NumberSelector(
            selector.NumberSelectorConfig(
                min=1,
                max=65535,
                mode=selector.NumberSelectorMode.BOX,
            )
        ),
        vol.Optional(CONF_SSL, default=False): selector.BooleanSelector(),
        vol.Optional(CONF_VERIFY_SSL, default=True): selector.BooleanSelector(),
        vol.Required(CONF_USERNAME): selector.TextSelector(
            selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT)
        ),
        vol.Required(CONF_PASSWORD): selector.TextSelector(
            selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)
        ),
    }
)


def _unique_id(host: str, port: int, ssl: bool) -> str:
    """Build a unique ID for a Gluetun instance."""
    return f"{host}:{port}:{int(bool(ssl))}"


class GluetunConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Gluetun."""

    VERSION = 1

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> GluetunOptionsFlow:
        """Return the options flow for this handler."""
        return GluetunOptionsFlow(config_entry)

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            host = str(user_input[CONF_HOST]).strip()
            port = int(user_input[CONF_PORT])
            ssl = bool(user_input[CONF_SSL])
            username = str(user_input[CONF_USERNAME]).strip()
            password = str(user_input[CONF_PASSWORD])

            await self.async_set_unique_id(_unique_id(host, port, ssl))
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=DEFAULT_NAME,
                data={
                    CONF_HOST: host,
                    CONF_PORT: port,
                    CONF_SSL: ssl,
                    CONF_VERIFY_SSL: bool(user_input[CONF_VERIFY_SSL]),
                    CONF_USERNAME: username,
                    CONF_PASSWORD: password,
                },
            )

        return self.async_show_form(
            step_id="user",
            data_schema=USER_STEP_SCHEMA,
            errors=errors,
        )


class GluetunOptionsFlow(OptionsFlowWithReload):
    """Handle Gluetun options."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize options flow."""
        self._config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage Gluetun options."""
        if user_input is not None:
            return self.async_create_entry(data=user_input)

        current_username = self._config_entry.options.get(
            CONF_USERNAME,
            self._config_entry.data.get(CONF_USERNAME, ""),
        )
        current_password = self._config_entry.options.get(
            CONF_PASSWORD,
            self._config_entry.data.get(CONF_PASSWORD, ""),
        )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Required(
                        CONF_USERNAME,
                        default=current_username,
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.TEXT
                        )
                    ),
                    vol.Required(
                        CONF_PASSWORD,
                        default=current_password,
                    ): selector.TextSelector(
                        selector.TextSelectorConfig(
                            type=selector.TextSelectorType.PASSWORD
                        )
                    ),
                }
            ),
        )