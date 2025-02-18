"""AsusRouter binary sensors."""

from __future__ import annotations

import logging

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .compilers import (
    list_sensors_gwlan,
    list_sensors_vpn_clients,
    list_sensors_vpn_servers,
    list_sensors_wlan,
)
from .const import (
    CONF_ENABLE_CONTROL,
    CONF_HIDE_PASSWORDS,
    DEFAULT_HIDE_PASSWORDS,
    PASSWORD,
    PARENTAL_CONTROL,
    WAN,
)
from .dataclass import ARBinarySensorDescription
from .entity import ARBinaryEntity, async_setup_ar_entry
from .router import ARDevice

_LOGGER = logging.getLogger(__name__)

BINARY_SENSORS = {
    (WAN, "status"): ARBinarySensorDescription(
        key="status",
        key_group=WAN,
        name="WAN",
        entity_category=EntityCategory.DIAGNOSTIC,
        device_class=BinarySensorDeviceClass.CONNECTIVITY,
        entity_registry_enabled_default=True,
        extra_state_attributes={
            "dns": "dns",
            "gateway": "gateway",
            "ip": "ip",
            "ip_type": "ip_type",
            "mask": "mask",
            "private_subnet": "private_subnet",
        },
    ),
}
BINARY_SENSORS_PARENTAL_CONTROL = {
    (PARENTAL_CONTROL, "state"): ARBinarySensorDescription(
        key="state",
        key_group=PARENTAL_CONTROL,
        name="Parental control",
        icon_on="mdi:magnify-expand",
        icon_off="mdi:magnify",
        entity_category=EntityCategory.DIAGNOSTIC,
        entity_registry_enabled_default=True,
        extra_state_attributes={
            "list": "list",
        },
    ),
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Setup AsusRouter binary sensors."""

    hide = list()
    if entry.options.get(CONF_HIDE_PASSWORDS, DEFAULT_HIDE_PASSWORDS):
        hide.append(PASSWORD)

    if not entry.options[CONF_ENABLE_CONTROL]:
        BINARY_SENSORS.update(list_sensors_vpn_clients(5))
        BINARY_SENSORS.update(list_sensors_vpn_servers(5))
        BINARY_SENSORS.update(list_sensors_wlan(3, hide))
        BINARY_SENSORS.update(list_sensors_gwlan(3, hide))
        BINARY_SENSORS.update(BINARY_SENSORS_PARENTAL_CONTROL)

    await async_setup_ar_entry(
        hass, entry, async_add_entities, BINARY_SENSORS, ARBinarySensor
    )


class ARBinarySensor(ARBinaryEntity, BinarySensorEntity):
    """AsusRouter binary sensor."""

    def __init__(
        self,
        coordinator: DataUpdateCoordinator,
        router: ARDevice,
        description: ARBinarySensorDescription,
    ) -> None:
        """Initialize AsusRouter binary sensor."""

        super().__init__(coordinator, router, description)
