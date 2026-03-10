"""Constants for the Gluetun integration."""

from __future__ import annotations

DOMAIN = "gluetun"

DEFAULT_NAME = "Gluetun"

PLATFORMS: list[str] = ["sensor", "button", "binary_sensor"]

CONF_HOST = "host"
CONF_PORT = "port"
CONF_SSL = "ssl"
CONF_VERIFY_SSL = "verify_ssl"
CONF_USERNAME = "username"
CONF_PASSWORD = "password"
CONF_AUTH_TYPE = "auth_type"
CONF_API_KEY = "api_key"

AUTH_BASIC = "basic"
AUTH_API_KEY = "api_key"
AUTH_NONE = "none"

DEFAULT_PORT = 8000

COORDINATOR_STATUS = "status"
COORDINATOR_PUBLIC_IP = "public_ip"
COORDINATOR_SETTINGS = "settings"

STATUS_SCAN_INTERVAL_SECONDS = 60
SCAN_INTERVAL_SECONDS = 300

EVENT_IP_CHANGED = f"{DOMAIN}_ip_changed"

MANUFACTURER = "Gluetun"
MODEL = "VPN"
