"""Constants for the Gluetun integration."""

from __future__ import annotations

DOMAIN = "gluetun"

DEFAULT_NAME = "Gluetun"

PLATFORMS: list[str] = ["sensor", "button"]

CONF_HOST = "host"
CONF_PORT = "port"
CONF_SSL = "ssl"
CONF_VERIFY_SSL = "verify_ssl"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"

DEFAULT_PORT = 8000

COORDINATOR_STATUS = "status"
COORDINATOR_PUBLIC_IP = "public_ip"
COORDINATOR_SETTINGS = "settings"

STATUS_SCAN_INTERVAL_SECONDS = 60
SCAN_INTERVAL_SECONDS = 300

MANUFACTURER = "Gluetun"
MODEL = "VPN"