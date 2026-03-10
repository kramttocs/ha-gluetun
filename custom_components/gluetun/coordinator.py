"""Data update coordinator for the Gluetun integration."""

from __future__ import annotations

from datetime import datetime, timedelta
import logging
from typing import Any

from aiohttp import ClientError
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.util import dt as dt_util

from .api.gluetun_api import GluetunApi, GluetunAuthenticationError
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import (
    COORDINATOR_PUBLIC_IP,
    COORDINATOR_SETTINGS,
    COORDINATOR_STATUS,
    EVENT_IP_CHANGED,
    SCAN_INTERVAL_SECONDS,
    STATUS_SCAN_INTERVAL_SECONDS,
)

_LOGGER = logging.getLogger(__name__)


class GluetunDataUpdateCoordinator(DataUpdateCoordinator[dict[str, dict[str, Any]]]):
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
        self._refresh_every = max(1, SCAN_INTERVAL_SECONDS // STATUS_SCAN_INTERVAL_SECONDS)
        self._refresh_count = 0
        self._last_public_ip_data: dict[str, Any] = {}
        self._last_settings_data: dict[str, Any] = {}
        self._previous_public_ip: str | None = None
        self._latest_public_ip: str | None = None
        self._last_ip_change_at: datetime | None = None

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

    @property
    def current_public_ip(self) -> str | None:
        """Return the latest known public IP address."""
        if self._latest_public_ip:
            return self._latest_public_ip
        if not self.data:
            return None
        value = self.data.get(COORDINATOR_PUBLIC_IP, {}).get("public_ip")
        return value if isinstance(value, str) and value else None

    @property
    def previous_public_ip(self) -> str | None:
        """Return the previous public IP address before the last change."""
        return self._previous_public_ip

    @property
    def last_ip_change_at(self) -> datetime | None:
        """Return when the public IP last changed."""
        return self._last_ip_change_at

    @property
    def latitude(self) -> float | None:
        """Return parsed latitude from the location payload."""
        return _parse_location_value(self.data.get(COORDINATOR_PUBLIC_IP, {}).get("location"), index=0) if self.data else None

    @property
    def longitude(self) -> float | None:
        """Return parsed longitude from the location payload."""
        return _parse_location_value(self.data.get(COORDINATOR_PUBLIC_IP, {}).get("location"), index=1) if self.data else None

    async def set_vpn_status(self, status: str) -> None:
        """Set the VPN status and refresh coordinator data."""
        try:
            await self.api.async_set_vpn_status(status)
        except GluetunAuthenticationError as err:
            raise ConfigEntryAuthFailed(str(err)) from err
        except ClientError as err:
            raise UpdateFailed(f"Error setting VPN status: {err}") from err

        await self.async_refresh_all_data()

    async def async_restart_vpn(self) -> None:
        """Restart the VPN and refresh coordinator data."""
        await self.set_vpn_status("stopped")
        await self.set_vpn_status("running")

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
                public_ip_data = await self.api.async_get_public_ip()
                settings_data = await self.api.async_get_vpn_settings()
                self._handle_public_ip_change(public_ip_data)
                self._last_public_ip_data = public_ip_data
                self._last_settings_data = settings_data

        except ClientError as err:
            raise UpdateFailed(f"Error fetching {self.name}: {err}") from err
        except ValueError as err:
            raise UpdateFailed(f"Invalid JSON response from {self.name}: {err}") from err

        if not isinstance(status_data, dict):
            raise UpdateFailed(
                f"Unexpected response type from {COORDINATOR_STATUS}: {type(status_data).__name__}"
            )

        if not isinstance(self._last_public_ip_data, dict):
            raise UpdateFailed(
                f"Unexpected response type from {COORDINATOR_PUBLIC_IP}: {type(self._last_public_ip_data).__name__}"
            )

        if not isinstance(self._last_settings_data, dict):
            raise UpdateFailed(
                f"Unexpected response type from {COORDINATOR_SETTINGS}: {type(self._last_settings_data).__name__}"
            )

        return {
            COORDINATOR_STATUS: status_data,
            COORDINATOR_PUBLIC_IP: self._last_public_ip_data,
            COORDINATOR_SETTINGS: self._last_settings_data,
        }

    async def async_refresh_all_data(self) -> None:
        """Force refresh of all coordinator data, including slow-changing data."""
        self._last_public_ip_data = {}
        self._last_settings_data = {}
        await self.async_request_refresh()

    def _handle_public_ip_change(self, public_ip_data: dict[str, Any]) -> None:
        """Track and broadcast public IP changes."""
        new_ip = public_ip_data.get("public_ip")
        if not isinstance(new_ip, str) or not new_ip:
            return

        if self._latest_public_ip is None:
            self._latest_public_ip = new_ip
            return

        if new_ip == self._latest_public_ip:
            return

        old_ip = self._latest_public_ip
        self._previous_public_ip = old_ip
        self._latest_public_ip = new_ip
        self._last_ip_change_at = dt_util.utcnow()

        self.hass.bus.async_fire(
            EVENT_IP_CHANGED,
            {
                "old_ip": old_ip,
                "new_ip": new_ip,
                "changed_at": self._last_ip_change_at.isoformat(),
            },
        )


def _parse_location_value(value: Any, *, index: int) -> float | None:
    """Parse a latitude/longitude value from the API location field."""
    if isinstance(value, dict):
        if index == 0:
            candidate = value.get("latitude", value.get("lat"))
        else:
            candidate = value.get("longitude", value.get("lon"))
        return _coerce_float(candidate)

    if isinstance(value, str):
        parts = [part.strip() for part in value.split(",", 1)]
        if len(parts) != 2:
            return None
        return _coerce_float(parts[index])

    return None


def _coerce_float(value: Any) -> float | None:
    """Convert a value to float if possible."""
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value.strip())
        except ValueError:
            return None
    return None
