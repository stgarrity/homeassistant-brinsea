"""The Brinsea Connect integration."""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import CONF_EMAIL, CONF_PASSWORD, DOMAIN, PLATFORMS
from .coordinator import BrinseaCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Brinsea Connect from a config entry."""
    from brinsea_api import BrinseaClient

    client = BrinseaClient(
        email=entry.data[CONF_EMAIL],
        password=entry.data[CONF_PASSWORD],
    )

    coordinator = BrinseaCoordinator(hass, client)
    await coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a Brinsea Connect config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        coordinator = hass.data[DOMAIN].pop(entry.entry_id)
        await coordinator.client.close()
    return unload_ok
