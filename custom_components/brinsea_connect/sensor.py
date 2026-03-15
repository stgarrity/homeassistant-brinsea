"""Sensor platform for Brinsea Connect."""

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import PERCENTAGE, UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import BrinseaCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Brinsea sensors from a config entry."""
    coordinator: BrinseaCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities = []
    for device_id, device_data in coordinator.data.items():
        device = device_data["device"]
        entities.extend([
            BrinseaTemperatureSensor(coordinator, device),
            BrinseaHumiditySensor(coordinator, device),
            BrinseaConnectionSensor(coordinator, device),
        ])

    async_add_entities(entities)


class BrinseaSensorBase(CoordinatorEntity):
    """Base class for Brinsea sensors."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: BrinseaCoordinator, device) -> None:
        super().__init__(coordinator)
        self._device = device
        self._attr_device_info = {
            "identifiers": {(DOMAIN, device.id)},
            "name": device.name,
            "manufacturer": "Brinsea",
            "model": device.model,
        }

    @property
    def _status(self):
        """Get current device status from coordinator data."""
        data = self.coordinator.data.get(self._device.id)
        if data:
            return data["status"]
        return None


class BrinseaTemperatureSensor(BrinseaSensorBase, SensorEntity):
    """Temperature sensor for Brinsea incubator."""

    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_name = "Temperature"

    def __init__(self, coordinator, device) -> None:
        super().__init__(coordinator, device)
        self._attr_unique_id = f"{device.id}_temperature"

    @property
    def native_value(self):
        status = self._status
        return status.temperature if status else None


class BrinseaHumiditySensor(BrinseaSensorBase, SensorEntity):
    """Humidity sensor for Brinsea incubator."""

    _attr_device_class = SensorDeviceClass.HUMIDITY
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = PERCENTAGE
    _attr_name = "Humidity"

    def __init__(self, coordinator, device) -> None:
        super().__init__(coordinator, device)
        self._attr_unique_id = f"{device.id}_humidity"

    @property
    def native_value(self):
        status = self._status
        return status.humidity if status else None


class BrinseaConnectionSensor(BrinseaSensorBase, SensorEntity):
    """Connection status sensor for Brinsea incubator."""

    _attr_name = "Connection"
    _attr_icon = "mdi:wifi"

    def __init__(self, coordinator, device) -> None:
        super().__init__(coordinator, device)
        self._attr_unique_id = f"{device.id}_connection"

    @property
    def native_value(self):
        status = self._status
        return status.connection_status if status else None

    @property
    def icon(self):
        status = self._status
        if status and status.connection_status == "connected":
            return "mdi:wifi"
        return "mdi:wifi-off"
