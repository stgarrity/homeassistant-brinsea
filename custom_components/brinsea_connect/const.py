"""Constants for the Brinsea Connect integration."""

from datetime import timedelta

DOMAIN = "brinsea_connect"
CONF_EMAIL = "email"
CONF_PASSWORD = "password"
DEFAULT_SCAN_INTERVAL = timedelta(minutes=1)
PLATFORMS = ["sensor"]
