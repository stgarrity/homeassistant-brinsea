# Brinsea Connect for Home Assistant

Home Assistant integration for Brinsea Connect incubators (Maxi, Mini, Ovation series with WiFi).

## Features

- **Temperature** monitoring (°C)
- **Humidity** monitoring (%)
- **Connection status** tracking

## Installation (HACS)

1. Add this repository as a custom repository in HACS
2. Install "Brinsea Connect"
3. Restart Home Assistant
4. Go to Settings → Integrations → Add Integration → "Brinsea Connect"
5. Enter your Brinsea Connect app email and password

## Sensors

Each incubator creates 3 sensors:
- `sensor.<name>_temperature` — Current temperature in °C
- `sensor.<name>_humidity` — Current humidity %
- `sensor.<name>_connection` — WiFi connection status

Data polls every 60 seconds.
