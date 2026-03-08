"""Config flow for the Gluetun integration."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry, ConfigFlow, OptionsFlowWithReload
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import selector

from .const import (
    AUTH_BASIC,
    AUTH_API_KEY,
    AUTH_NONE,
    CONF_AUTH_TYPE,
    CONF_HOST,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_SSL,
    CONF_API_KEY,
    CONF_USERNAME,
    CONF_VERIFY_SSL,
    DEFAULT_NAME,
    DEFAULT_PORT,
    DOMAIN,
)


def _unique_id(host: str, port: int, ssl: bool) -> str:
    """Build a unique ID for a Gluetun instance."""
    return f"{host}:{port}:{int(bool(ssl))}"


def _auth_type_selector(*, default: str) -> selector.SelectSelector:
    """Return the auth type selector."""
    return selector.SelectSelector(
        selector.SelectSelectorConfig(
            options=[
                selector.SelectOptionDict(
                    value=AUTH_BASIC,
                    label="Basic authentication",
                ),
                selector.SelectOptionDict(
                    value=AUTH_API_KEY,
                    label="API Key",
                ),
                selector.SelectOptionDict(
                    value=AUTH_NONE,
                    label="No authentication",
                ),
            ],
            mode=selector.SelectSelectorMode.LIST,
        )
    )


def _text_selector() -> selector.TextSelector:
    """Return a standard text selector."""
    return selector.TextSelector(
        selector.TextSelectorConfig(type=selector.TextSelectorType.TEXT)
    )


def _password_selector() -> selector.TextSelector:
    """Return a password selector."""
    return selector.TextSelector(
        selector.TextSelectorConfig(type=selector.TextSelectorType.PASSWORD)
    )


def _connection_schema(*, default_auth_type: str = AUTH_BASIC) -> vol.Schema:
    """Return the initial connection schema."""
    return vol.Schema(
        {
            vol.Required(CONF_HOST): _text_selector(),
            vol.Required(CONF_PORT, default=DEFAULT_PORT): selector.NumberSelector(
                selector.NumberSelectorConfig(
                    min=1,
                    max=65535,
                    mode=selector.NumberSelectorMode.BOX,
                )
            ),
            vol.Optional(CONF_SSL, default=False): selector.BooleanSelector(),
            vol.Optional(CONF_VERIFY_SSL, default=True): selector.BooleanSelector(),
            vol.Required(CONF_AUTH_TYPE, default=default_auth_type): _auth_type_selector(
                default=default_auth_type
            ),
        }
    )


def _basic_auth_schema(
    *,
    username: str = "",
    password: str = "",
) -> vol.Schema:
    """Return the basic auth schema."""
    return vol.Schema(
        {
            vol.Required(CONF_USERNAME, default=username): _text_selector(),
            vol.Required(CONF_PASSWORD, default=password): _password_selector(),
        }
    )


def _api_key_auth_schema(*, api_key: str = "") -> vol.Schema:
    """Return the API key schema."""
    return vol.Schema(
        {
            vol.Required(CONF_API_KEY, default=api_key): _text_selector(),
        }
    )


class GluetunConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Gluetun."""

    VERSION = 1

    def __init__(self) -> None:
        """Initialize the config flow."""
        self._config_data: dict[str, Any] = {}

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> GluetunOptionsFlow:
        """Return the options flow for this handler."""
        return GluetunOptionsFlow(config_entry)

    async def async_step_user(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Handle the initial connection step."""
        if user_input is not None:
            host = str(user_input[CONF_HOST]).strip()
            port = int(user_input[CONF_PORT])
            ssl = bool(user_input[CONF_SSL])
            auth_type = str(user_input[CONF_AUTH_TYPE])

            await self.async_set_unique_id(_unique_id(host, port, ssl))
            self._abort_if_unique_id_configured()

            self._config_data = {
                CONF_HOST: host,
                CONF_PORT: port,
                CONF_SSL: ssl,
                CONF_VERIFY_SSL: bool(user_input[CONF_VERIFY_SSL]),
                CONF_AUTH_TYPE: auth_type,
            }

            if auth_type == AUTH_BASIC:
                return await self.async_step_basic_auth()

            if auth_type == AUTH_API_KEY:
                return await self.async_step_api_key_auth()

            return self.async_create_entry(title=DEFAULT_NAME, data=self._config_data)

        return self.async_show_form(
            step_id="user",
            data_schema=_connection_schema(),
            errors={},
        )

    async def async_step_basic_auth(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Handle the basic auth step."""
        if user_input is not None:
            self._config_data.update(
                {
                    CONF_USERNAME: str(user_input[CONF_USERNAME]).strip(),
                    CONF_PASSWORD: str(user_input[CONF_PASSWORD]),
                }
            )
            return self.async_create_entry(title=DEFAULT_NAME, data=self._config_data)

        return self.async_show_form(
            step_id="basic_auth",
            data_schema=_basic_auth_schema(),
            errors={},
        )

    async def async_step_api_key_auth(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Handle the API key step."""
        if user_input is not None:
            self._config_data.update(
                {
                    CONF_API_KEY: str(user_input[CONF_API_KEY]).strip(),
                }
            )
            return self.async_create_entry(title=DEFAULT_NAME, data=self._config_data)
    
        return self.async_show_form(
            step_id="api_key_auth",
            data_schema=_api_key_auth_schema(),
            errors={},
        )


class GluetunOptionsFlow(OptionsFlowWithReload):
    """Handle Gluetun options."""

    def __init__(self, config_entry: ConfigEntry) -> None:
        """Initialize options flow."""
        self._config_entry = config_entry

    async def async_step_init(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Manage Gluetun options."""
        auth_type = str(
            self._config_entry.data.get(
                CONF_AUTH_TYPE,
                AUTH_BASIC,
            )
        )

        if auth_type == AUTH_BASIC:
            return await self.async_step_basic_auth(user_input)

        if auth_type == AUTH_API_KEY:
            return await self.async_step_api_key_auth(user_input)

        return self.async_create_entry(data={})

    async def async_step_basic_auth(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Manage basic auth options."""
        if user_input is not None:
            return self.async_create_entry(
                data={
                    CONF_USERNAME: str(user_input[CONF_USERNAME]).strip(),
                    CONF_PASSWORD: str(user_input[CONF_PASSWORD]),
                }
            )

        current_username = str(
            self._config_entry.options.get(
                CONF_USERNAME,
                self._config_entry.data.get(CONF_USERNAME, ""),
            )
        )
        current_password = str(
            self._config_entry.options.get(
                CONF_PASSWORD,
                self._config_entry.data.get(CONF_PASSWORD, ""),
            )
        )

        return self.async_show_form(
            step_id="basic_auth",
            data_schema=_basic_auth_schema(
                username=current_username,
                password=current_password,
            ),
            errors={},
        )

    async def async_step_api_key_auth(
        self,
        user_input: dict[str, Any] | None = None,
    ) -> FlowResult:
        """Manage api key options."""
        if user_input is not None:
            return self.async_create_entry(
                data={
                    CONF_API_KEY: str(user_input[CONF_API_KEY]).strip(),
                }
            )

        current_api_key = str(
            self._config_entry.options.get(
                CONF_API_KEY,
                self._config_entry.data.get(CONF_API_KEY, ""),
            )
        )

        return self.async_show_form(
            step_id="api_key_auth",
            data_schema=_api_key_auth_schema(api_key=current_api_key),
            errors={},
        )