"""Data update coordinator for the Gluetun integration."""

from __future__ import annotations

from datetime import timedelta
import logging
from typing import Any

from aiohttp import ClientError
from homeassistant.exceptions import ConfigEntryAuthFailed
from .api.gluetun_api import GluetunApi, GluetunAuthenticationError

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed


from .const import (
    COORDINATOR_PUBLIC_IP,
    COORDINATOR_SETTINGS,
    COORDINATOR_STATUS,
    SCAN_INTERVAL_SECONDS,
    STATUS_SCAN_INTERVAL_SECONDS,
)

_LOGGER = logging.getLogger(__name__)


class GluetunDataUpdateCoordinator(
    DataUpdateCoordinator[dict[str, dict[str, Any]]]
):
    """Coordinate Gluetun API polling."""

    def __init__(self, hass: HomeAssistant, api: GluetunApi) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="gluetun",
            update_interval=timedelta(seconds=STATUS_SCAN_INTERVAL_SECONDS),
        )
        self.api = api
        self._refresh_every = max(
            1, SCAN_INTERVAL_SECONDS // STATUS_SCAN_INTERVAL_SECONDS
        )
        self._refresh_count = 0
        self._last_public_ip_data: dict[str, Any] = {}
        self._last_settings_data: dict[str, Any] = {}

    @property
    def vpn_status(self) -> str | None:
        """Return the current VPN status."""
        return self.data.get(COORDINATOR_STATUS, {}).get("status") if self.data else None
        
    @property
    def vpn_type(self) -> str | None:
        """Return the configured VPN type."""
        if not self.data:
            return None
        value = self.data.get(COORDINATOR_SETTINGS, {}).get("type")
        if not isinstance(value, str) or not value:
            return None
        return value.upper()

    @property
    def provider_name(self) -> str | None:
        """Return the configured VPN provider name."""
        if not self.data:
            return None
        provider = self.data.get(COORDINATOR_SETTINGS, {}).get("provider", {})
        if not isinstance(provider, dict):
            return None
        value = provider.get("name")
        if not isinstance(value, str) or not value:
            return None
        return value.title()

    async def set_vpn_status(self, status: str) -> None:
        """Set the VPN status and refresh coordinator data."""
        try:
            await self.api.async_set_vpn_status(status)
        except GluetunAuthenticationError as err:
            raise ConfigEntryAuthFailed(str(err)) from err
        except ClientError as err:
            raise UpdateFailed(f"Error setting VPN status: {err}") from err

        await self.async_request_refresh()

    async def _async_update_data(self) -> dict[str, dict[str, Any]]:
        """Fetch and validate data from the configured endpoints."""
        self._refresh_count += 1

        try:
            status_data = await self.api.async_get_vpn_status()

            should_refresh_slow_data = (
                not self._last_public_ip_data
                or not self._last_settings_data
                or self._refresh_count % self._refresh_every == 0
            )
            if should_refresh_slow_data:
                self._last_public_ip_data = await self.api.async_get_public_ip()
                self._last_settings_data = await self.api.async_get_vpn_settings()

        except ClientError as err:
            raise UpdateFailed(f"Error fetching {self.name}: {err}") from err
        except ValueError as err:
            raise UpdateFailed(f"Invalid JSON response from {self.name}: {err}") from err

        if not isinstance(status_data, dict):
            raise UpdateFailed(
                f"Unexpected response type from {COORDINATOR_STATUS}: "
                f"{type(status_data).__name__}"
            )

        if not isinstance(self._last_public_ip_data, dict):
            raise UpdateFailed(
                f"Unexpected response type from {COORDINATOR_PUBLIC_IP}: "
                f"{type(self._last_public_ip_data).__name__}"
            )

        if not isinstance(self._last_settings_data, dict):
            raise UpdateFailed(
                f"Unexpected response type from {COORDINATOR_SETTINGS}: "
                f"{type(self._last_settings_data).__name__}"
            )

        return {
            COORDINATOR_STATUS: status_data,
            COORDINATOR_PUBLIC_IP: self._last_public_ip_data,
            COORDINATOR_SETTINGS: self._last_settings_data,
        }