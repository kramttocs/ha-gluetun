"""Binary sensor platform for the Gluetun integration."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Final

from homeassistant.components.binary_sensor import BinarySensorEntity, BinarySensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DEFAULT_NAME, DOMAIN, MANUFACTURER, MODEL
from .coordinator import GluetunDataUpdateCoordinator

GluetunIsOnFn = Callable[[GluetunDataUpdateCoordinator], bool]


@dataclass(frozen=True, kw_only=True)
class GluetunBinarySensorEntityDescription(BinarySensorEntityDescription):
    """Describe a Gluetun binary sensor entity."""

    is_on_fn: GluetunIsOnFn


BINARY_SENSORS: Final[tuple[GluetunBinarySensorEntityDescription, ...]] = (
    GluetunBinarySensorEntityDescription(
        key="vpn_connected",
        translation_key="vpn_connected",
        icon="mdi:shield-check",
        is_on_fn=lambda coordinator: coordinator.vpn_status == "running",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Gluetun binary sensor entities."""
    coordinator: GluetunDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(
        GluetunBinarySensor(coordinator, entry.entry_id, description)
        for description in BINARY_SENSORS
    )


class GluetunBinarySensor(CoordinatorEntity[GluetunDataUpdateCoordinator], BinarySensorEntity):
    """Representation of a Gluetun binary sensor."""

    entity_description: GluetunBinarySensorEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: GluetunDataUpdateCoordinator,
        entry_id: str,
        description: GluetunBinarySensorEntityDescription,
    ) -> None:
        """Initialize the binary sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._entry_id = entry_id
        self._attr_unique_id = f"{entry_id}_{description.key}"

    @property
    def is_on(self) -> bool:
        """Return the binary sensor state."""
        return self.entity_description.is_on_fn(self.coordinator)

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information for the Gluetun device."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry_id)},
            name=DEFAULT_NAME,
            manufacturer=self.coordinator.provider_name or MANUFACTURER,
            model=self.coordinator.vpn_type or MODEL,
        )
