"""Config flow for Brinsea Connect."""

import logging

import voluptuous as vol
from homeassistant import config_entries

from .const import CONF_EMAIL, CONF_PASSWORD, DOMAIN

_LOGGER = logging.getLogger(__name__)


class BrinseaConnectConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Brinsea Connect."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            from brinsea_api import BrinseaClient, BrinseaAuthError

            client = BrinseaClient(
                email=user_input[CONF_EMAIL],
                password=user_input[CONF_PASSWORD],
            )
            try:
                await client.authenticate()
                devices = await client.get_devices()
            except BrinseaAuthError:
                errors["base"] = "invalid_auth"
            except Exception:
                _LOGGER.exception("Unexpected error during setup")
                errors["base"] = "cannot_connect"
            else:
                await client.close()
                await self.async_set_unique_id(user_input[CONF_EMAIL])
                self._abort_if_unique_id_configured()

                device_names = ", ".join(d.name for d in devices) if devices else "Brinsea"
                return self.async_create_entry(
                    title=device_names,
                    data=user_input,
                )
            finally:
                await client.close()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_EMAIL): str,
                    vol.Required(CONF_PASSWORD): str,
                }
            ),
            errors=errors,
        )
