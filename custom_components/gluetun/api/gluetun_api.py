"""API client for the Gluetun integration."""

from __future__ import annotations

from typing import Any
from urllib.parse import urljoin

import aiohttp
from aiohttp import ClientResponseError, ClientSession


class GluetunAuthenticationError(Exception):
    """Raised when Gluetun authentication fails."""


class GluetunApi:
    """Small API client for Gluetun."""

    def __init__(
        self,
        session: ClientSession,
        *,
        host: str,
        port: int,
        ssl: bool,
        verify_ssl: bool,
        username: str,
        password: str,
    ) -> None:
        """Initialize the API client."""
        self._session = session
        self._host = (
            host.strip()
            .removeprefix("http://")
            .removeprefix("https://")
            .rstrip("/")
        )
        self._port = port
        self._ssl = ssl
        self._verify_ssl = verify_ssl
        self._auth = aiohttp.BasicAuth(username, password)

    @property
    def _api_url(self) -> str:
        """Return the base API URL for the configured Gluetun instance."""
        scheme = "https" if self._ssl else "http"
        return f"{scheme}://{self._host}:{self._port}"

    async def _get_json(self, path: str) -> dict[str, Any]:
        """Fetch JSON from a Gluetun endpoint."""
        url = urljoin(self._api_url, path)

        try:
            async with self._session.get(
                url,
                auth=self._auth,
                ssl=self._verify_ssl,
            ) as response:
                response.raise_for_status()
                data = await response.json(content_type=None)
        except ClientResponseError as err:
            if err.status == 401:
                raise GluetunAuthenticationError("Invalid username or password") from err
            raise

        if not isinstance(data, dict):
            raise ValueError(f"Unexpected response type: {type(data).__name__}")

        return data

    async def async_get_vpn_status(self) -> dict[str, Any]:
        """Return the VPN status payload."""
        return await self._get_json("/v1/vpn/status")

    async def async_get_public_ip(self) -> dict[str, Any]:
        """Return the public IP payload."""
        return await self._get_json("/v1/publicip/ip")
        
    async def async_get_vpn_settings(self) -> dict[str, Any]:
        """Return the VPN settings payload."""
        return await self._get_json("/v1/vpn/settings")

    async def async_set_vpn_status(self, status: str) -> None:
        """Set the VPN status."""
        url = urljoin(self._api_url, "/v1/vpn/status")
        payload = {"status": status}

        try:
            async with self._session.put(
                url,
                json=payload,
                auth=self._auth,
                ssl=self._verify_ssl,
            ) as response:
                response.raise_for_status()
        except ClientResponseError as err:
            if err.status == 401:
                raise GluetunAuthenticationError("Invalid username or password") from err
            raise