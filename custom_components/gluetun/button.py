"""Button platform for Gluetun control."""

from __future__ import annotations

from collections.abc import Callable, Coroutine
from dataclasses import dataclass
from typing import Any, Final

from homeassistant.components.button import ButtonEntity, ButtonEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DEFAULT_NAME, DOMAIN, MANUFACTURER, MODEL
from .coordinator import GluetunDataUpdateCoordinator

GluetunPressFn = Callable[[GluetunDataUpdateCoordinator], Coroutine[Any, Any, None]]
GluetunAvailableFn = Callable[[GluetunDataUpdateCoordinator], bool]


@dataclass(frozen=True, kw_only=True)
class GluetunButtonEntityDescription(ButtonEntityDescription):
    """Describe a Gluetun button entity."""

    press_fn: GluetunPressFn
    available_fn: GluetunAvailableFn


BUTTONS: Final[tuple[GluetunButtonEntityDescription, ...]] = (
    GluetunButtonEntityDescription(
        key="start_vpn",
        translation_key="start_vpn",
        icon="mdi:play-circle",
        press_fn=lambda coordinator: coordinator.set_vpn_status("running"),
        available_fn=lambda coordinator: coordinator.vpn_status != "running",
    ),
    GluetunButtonEntityDescription(
        key="stop_vpn",
        translation_key="stop_vpn",
        icon="mdi:stop-circle",
        press_fn=lambda coordinator: coordinator.set_vpn_status("stopped"),
        available_fn=lambda coordinator: coordinator.vpn_status != "stopped",
    ),
    GluetunButtonEntityDescription(
        key="restart_vpn",
        translation_key="restart_vpn",
        icon="mdi:restart",
        press_fn=lambda coordinator: coordinator.async_restart_vpn(),
        available_fn=lambda coordinator: coordinator.vpn_status is not None,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up Gluetun button entities."""
    coordinator: GluetunDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    async_add_entities(GluetunButton(coordinator, entry.entry_id, description) for description in BUTTONS)


class GluetunButton(CoordinatorEntity[GluetunDataUpdateCoordinator], ButtonEntity):
    """Representation of a Gluetun control button."""

    entity_description: GluetunButtonEntityDescription
    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: GluetunDataUpdateCoordinator,
        entry_id: str,
        description: GluetunButtonEntityDescription,
    ) -> None:
        """Initialize the button."""
        super().__init__(coordinator)
        self.entity_description = description
        self._entry_id = entry_id
        self._attr_unique_id = f"{entry_id}_{description.key}"

    @property
    def available(self) -> bool:
        """Return availability."""
        return super().available and self.entity_description.available_fn(self.coordinator)

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info."""
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry_id)},
            name=DEFAULT_NAME,
            manufacturer=self.coordinator.provider_name or MANUFACTURER,
            model=self.coordinator.vpn_type or MODEL,
        )

    async def async_press(self) -> None:
        """Handle the button press."""
        await self.entity_description.press_fn(self.coordinator)
