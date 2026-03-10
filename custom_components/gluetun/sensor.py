"""Sensor platform for the Gluetun integration."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Final

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorEntityDescription
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

GluetunConfigEntry = ConfigEntry[dict[str, Any]]
GluetunValueFn = Callable[[GluetunDataUpdateCoordinator], str | float | datetime | None]
GluetunAttrFn = Callable[[GluetunDataUpdateCoordinator], dict[str, Any] | None]


@dataclass(frozen=True, kw_only=True)
class GluetunSensorEntityDescription(SensorEntityDescription):
    """Describe a Gluetun sensor entity."""

    value_fn: GluetunValueFn
    extra_attributes_fn: GluetunAttrFn | None = None


def _provider_name(coordinator: GluetunDataUpdateCoordinator) -> str | None:
    settings = coordinator.data.get(COORDINATOR_SETTINGS, {})
    provider = settings.get("provider", {})
    if not isinstance(provider, dict):
        return None
    name = provider.get("name")
    return name if isinstance(name, str) and name else None


def _vpn_type(coordinator: GluetunDataUpdateCoordinator) -> str | None:
    settings = coordinator.data.get(COORDINATOR_SETTINGS, {})
    value = settings.get("type")
    return value if isinstance(value, str) and value else None


def _vpn_status(coordinator: GluetunDataUpdateCoordinator) -> str | None:
    status = coordinator.data.get(COORDINATOR_STATUS, {})
    value = status.get("status")
    return value if isinstance(value, str) and value else None


def _public_ip(coordinator: GluetunDataUpdateCoordinator) -> str | None:
    public_ip = coordinator.data.get(COORDINATOR_PUBLIC_IP, {})
    value = public_ip.get("public_ip")
    return value if isinstance(value, str) and value else None


def _string_public_ip_field(coordinator: GluetunDataUpdateCoordinator, key: str) -> str | None:
    public_ip = coordinator.data.get(COORDINATOR_PUBLIC_IP, {})
    value = public_ip.get(key)
    return value if isinstance(value, str) and value else None


def _latitude(coordinator: GluetunDataUpdateCoordinator) -> float | None:
    return coordinator.latitude


def _longitude(coordinator: GluetunDataUpdateCoordinator) -> float | None:
    return coordinator.longitude


def _last_ip_change(coordinator: GluetunDataUpdateCoordinator) -> datetime | None:
    return coordinator.last_ip_change_at


def _last_ip_change_attrs(coordinator: GluetunDataUpdateCoordinator) -> dict[str, Any] | None:
    if coordinator.last_ip_change_at is None:
        return None
    return {
        "old_ip": coordinator.previous_public_ip,
        "new_ip": coordinator.current_public_ip,
        "changed_at": coordinator.last_ip_change_at.isoformat(),
    }


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
        value_fn=lambda coordinator: _string_public_ip_field(coordinator, "location"),
    ),
    GluetunSensorEntityDescription(
        key="organization",
        translation_key="organization",
        icon="mdi:domain",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda coordinator: _string_public_ip_field(coordinator, "organization"),
    ),
    GluetunSensorEntityDescription(
        key="postal_code",
        translation_key="postal_code",
        icon="mdi:mailbox",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda coordinator: _string_public_ip_field(coordinator, "postal_code"),
    ),
    GluetunSensorEntityDescription(
        key="country",
        translation_key="country",
        icon="mdi:earth",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda coordinator: _string_public_ip_field(coordinator, "country"),
    ),
    GluetunSensorEntityDescription(
        key="region",
        translation_key="region",
        icon="mdi:map-marker-radius",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda coordinator: _string_public_ip_field(coordinator, "region"),
    ),
    GluetunSensorEntityDescription(
        key="city",
        translation_key="city",
        icon="mdi:city",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda coordinator: _string_public_ip_field(coordinator, "city"),
    ),
    GluetunSensorEntityDescription(
        key="timezone",
        translation_key="timezone",
        icon="mdi:clock-outline",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=lambda coordinator: _string_public_ip_field(coordinator, "timezone"),
    ),
    GluetunSensorEntityDescription(
        key="latitude",
        translation_key="latitude",
        icon="mdi:latitude",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=_latitude,
    ),
    GluetunSensorEntityDescription(
        key="longitude",
        translation_key="longitude",
        icon="mdi:longitude",
        entity_category=EntityCategory.DIAGNOSTIC,
        value_fn=_longitude,
    ),
    GluetunSensorEntityDescription(
        key="last_ip_change",
        translation_key="last_ip_change",
        icon="mdi:history",
        entity_category=EntityCategory.DIAGNOSTIC,
        device_class=SensorDeviceClass.TIMESTAMP,
        value_fn=_last_ip_change,
        extra_attributes_fn=_last_ip_change_attrs,
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


class GluetunSensorEntity(CoordinatorEntity[GluetunDataUpdateCoordinator], SensorEntity):
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
    def native_value(self) -> str | float | datetime | None:
        """Return the sensor state."""
        return self.entity_description.value_fn(self.coordinator)

    @property
    def extra_state_attributes(self) -> dict[str, Any] | None:
        """Return extra state attributes."""
        if self.entity_description.extra_attributes_fn is None:
            return None
        return self.entity_description.extra_attributes_fn(self.coordinator)

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
