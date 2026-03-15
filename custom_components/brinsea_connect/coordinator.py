"""Data coordinator for Brinsea Connect."""

import logging

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import DEFAULT_SCAN_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


class BrinseaCoordinator(DataUpdateCoordinator):
    """Fetch data from Brinsea Connect API."""

    def __init__(self, hass: HomeAssistant, client) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=DEFAULT_SCAN_INTERVAL,
        )
        self.client = client
        self.devices: list = []

    async def _async_update_data(self) -> dict:
        """Fetch latest data from Brinsea API."""
        from .api_exceptions import BrinseaError

        try:
            if not self.devices:
                self.devices = await self.client.get_devices()

            data = {}
            for device in self.devices:
                status = await self.client.get_device_status(device.id)
                data[device.id] = {
                    "device": device,
                    "status": status,
                }
            return data
        except BrinseaError as err:
            raise UpdateFailed(f"Error fetching Brinsea data: {err}") from err
