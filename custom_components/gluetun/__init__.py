"""The Gluetun integration."""

from __future__ import annotations

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .api.gluetun_api import GluetunApi
from .const import (
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
    api = GluetunApi(
        session,
        host=str(entry.data[CONF_HOST]),
        port=int(entry.data[CONF_PORT]),
        ssl=bool(entry.data.get(CONF_SSL, False)),
        verify_ssl=bool(entry.data.get(CONF_VERIFY_SSL, True)),
        username=str(entry.options.get(CONF_USERNAME, entry.data[CONF_USERNAME])),
        password=str(entry.options.get(CONF_PASSWORD, entry.data[CONF_PASSWORD])),
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
