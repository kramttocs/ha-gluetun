"""The Gluetun integration."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api.gluetun_api import GluetunApi
from .const import (
    AUTH_BASIC,
    CONF_API_KEY,
    CONF_AUTH_TYPE,
    CONF_HOST,
    CONF_PASSWORD,
    CONF_PORT,
    CONF_SSL,
    CONF_USERNAME,
    CONF_VERIFY_SSL,
    DOMAIN,
    PLATFORMS,
)
from .coordinator import GluetunDataUpdateCoordinator

type GluetunConfigEntry = ConfigEntry[dict[str, Any]]


async def async_setup_entry(hass: HomeAssistant, entry: GluetunConfigEntry) -> bool:
    """Set up Gluetun from a config entry."""
    session = async_get_clientsession(hass)
    data = entry.data
    options = entry.options
    
    api = GluetunApi(
        session,
        host=str(data[CONF_HOST]),
        port=int(data[CONF_PORT]),
        ssl=bool(data.get(CONF_SSL, False)),
        verify_ssl=bool(data.get(CONF_VERIFY_SSL, True)),
        auth_type=str(data.get(CONF_AUTH_TYPE, AUTH_BASIC)),
        username=str(options.get(CONF_USERNAME, data.get(CONF_USERNAME, ""))),
        password=str(options.get(CONF_PASSWORD, data.get(CONF_PASSWORD, ""))),
        api_key=str(options.get(CONF_API_KEY, data.get(CONF_API_KEY, ""))),
    )

    coordinator = GluetunDataUpdateCoordinator(hass, api)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: GluetunConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id, None)

    return unload_ok
