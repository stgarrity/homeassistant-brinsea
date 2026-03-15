"""Data models for Brinsea Connect API."""

from dataclasses import dataclass


@dataclass
class Device:
    """A Brinsea incubator device."""

    id: str
    name: str
    model: str
    firmware_id: str


@dataclass
class DeviceStatus:
    """Live status readings from a Brinsea device."""

    thing_id: str
    temperature: float | None
    humidity: float | None
    connection_status: str
