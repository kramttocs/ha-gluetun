"""Sensor platform for the Gluetun integration."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Final, Any

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    COORDINATOR_PUBLIC_IP,
    COORDINATOR_SETTINGS,
    COORDINATOR_STATUS,
    DEFAULT_NAME,
    DOMAIN,
    MANUFACTURER,
    MODEL,
)
from .coordinator import GluetunDataUpdateCoordinator


type GluetunConfigEntry = ConfigEntry[dict[str, Any]]
type GluetunValueFn = Callable[[GluetunDataUpdateCoordinator], str | None]


@dataclass(frozen=True, kw_only=True)
class GluetunSensorEntityDescription(SensorEntityDescription):
    """Describe a Gluetun sensor entity."""

    value_fn: GluetunValueFn


def _provider_name(coordinator: GluetunDataUpdateCoordinator) -> str | None:
    """Return the VPN provider name."""
    settings = coordinator.data.get(COORDINATOR_SETTINGS, {})
    provider = settings.get("provider", {})
    if not isinstance(provider, dict):
        return None

    name = provider.get("name")
    return name if isinstance(name, str) and name else None


def _vpn_type(coordinator: GluetunDataUpdateCoordinator) -> str | None:
    """Return the VPN type."""
    settings = coordinator.data.get(COORDINATOR_SETTINGS, {})
    value = settings.get("type")
    return value if isinstance(value, str) and value else None


def _vpn_status(coordinator: GluetunDataUpdateCoordinator) -> str | None:
    """Return the VPN status."""
    status = coordinator.data.get(COORDINATOR_STATUS, {})
    value = status.get("status")
    return value if isinstance(value, str) and value else None


def _public_ip(coordinator: GluetunDataUpdateCoordinator) -> str | None:
    """Return the public IP."""
    public_ip = coordinator.data.get(COORDINATOR_PUBLIC_IP, {})
    value = public_ip.get("public_ip")
    return value if isinstance(value, str) and value else None
    

def _location(coordinator: GluetunDataUpdateCoordinator) -> str | None:
    """Return the location."""
    public_ip = coordinator.data.get(COORDINATOR_PUBLIC_IP, {})
    value = public_ip.get("location")
    return value if isinstance(value, str) and value else None


def _organization(coordinator: GluetunDataUpdateCoordinator) -> str | None:
    """Return the organization."""
    public_ip = coordinator.data.get(COORDINATOR_PUBLIC_IP, {})
    value = public_ip.get("organization")
    return value if isinstance(value, str) and value else None


def _postal_code(coordinator: GluetunDataUpdateCoordinator) -> str | None:
    """Return the postal code."""
    public_ip = coordinator.data.get(COORDINATOR_PUBLIC_IP, {})
    value = public_ip.get("postal_code")
    return value if isinstance(value, str) and value else None


def _country(coordinator: GluetunDataUpdateCoordinator) -> str | None:
    """Return the country."""
    public_ip = coordinator.data.get(COORDINATOR_PUBLIC_IP, {})
    value = public_ip.get("country")
    return value if isinstance(value, str) and value else None


def _region(coordinator: GluetunDataUpdateCoordinator) -> str | None:
    """Return the region."""
    public_ip = coordinator.data.get(COORDINATOR_PUBLIC_IP, {})
    value = public_ip.get("region")
    return value if isinstance(value, str) and value else None


def _city(coordinator: GluetunDataUpdateCoordinator) -> str | None:
    """Return the city."""
    public_ip = coordinator.data.get(COORDINATOR_PUBLIC_IP, {})
    value = public_ip.get("city")
    return value if isinstance(value, str) and value else None


def _timezone(coordinator: GluetunDataUpdateCoordinator) -> str | None:
    """Return the timezone."""
    public_ip = coordinator.data.get(COORDINATOR_PUBLIC_IP, {})
    value = public_ip.get("timezone")
    return value if isinstance(value, str) and value else None


SENSOR_DESCRIPTIONS: Final[tuple[GluetunSensorEntityDescription, ...]] = (
    GluetunSensorEntityDescription(
        key="vpn_status",
        translation_key="vpn_status",
        value_fn=_vpn_status,
    ),
    GluetunSensorEntityDescription(
        key="public_ip",
        translation_key="public_ip",
        icon="mdi:ip-network",
        value_fn=_public_ip,
    ),
    GluetunSensorEntityDescription(
        key="provider",
        translation_key="provider",
        icon="mdi:cloud",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=_provider_name,
    ),
    GluetunSensorEntityDescription(
        key="vpn_type",
        translation_key="vpn_type",
        icon="mdi:vpn",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=_vpn_type,
    ),
    GluetunSensorEntityDescription(
        key="location",
        translation_key="location",
        icon="mdi:crosshairs-gps",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=_location,
    ),
    GluetunSensorEntityDescription(
        key="organization",
        translation_key="organization",
        icon="mdi:domain",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=_organization,
    ),
    GluetunSensorEntityDescription(
        key="postal_code",
        translation_key="postal_code",
        icon="mdi:mailbox",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=_postal_code,
    ),
    GluetunSensorEntityDescription(
        key="country",
        translation_key="country",
        icon="mdi:earth",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=_country,
    ),
    GluetunSensorEntityDescription(
        key="region",
        translation_key="region",
        icon="mdi:map-marker-radius",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=_region,
    ),
    GluetunSensorEntityDescription(
        key="city",
        translation_key="city",
        icon="mdi:city",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=_city,
    ),
    GluetunSensorEntityDescription(
        key="timezone",
        translation_key="timezone",
        icon="mdi:clock-outline",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=_timezone,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: GluetunConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Gluetun sensor entities from a config entry."""
    coordinator: GluetunDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        GluetunSensorEntity(coordinator, entry, description)
        for description in SENSOR_DESCRIPTIONS
    )


class GluetunSensorEntity(
    CoordinatorEntity[GluetunDataUpdateCoordinator],
    SensorEntity,
):
    """Representation of a Gluetun sensor."""

    entity_description: GluetunSensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: GluetunDataUpdateCoordinator,
        entry: GluetunConfigEntry,
        description: GluetunSensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._entry = entry
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"

    @property
    def native_value(self) -> str | None:
        """Return the sensor state."""
        return self.entity_description.value_fn(self.coordinator)

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information for the Gluetun device."""
        manufacturer = self.coordinator.provider_name or MANUFACTURER
        model = self.coordinator.vpn_type or MODEL

        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name=DEFAULT_NAME,
            manufacturer=manufacturer,
            model=model,
        )
        
    @property
    def icon(self) -> str | None:
        """Return the entity icon."""
        if self.entity_description.key != "vpn_status":
            return self.entity_description.icon

        status = self.native_value
        if status == "running":
            return "mdi:shield-check"
        if status == "stopped":
            return "mdi:shield-off"
        return "mdi:shield-outline"