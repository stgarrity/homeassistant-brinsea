"""Brinsea Connect API client."""

import base64
import logging

import aiohttp

from .api_auth import BrinseaAuth
from .api_const import API_BASE_URL, API_DEVICE_CACHE, API_DEVICE_DB
from .api_exceptions import BrinseaConnectionError, BrinseaError
from .api_models import Device, DeviceStatus

_LOGGER = logging.getLogger(__name__)


class BrinseaClient:
    """Async client for the Brinsea Connect API."""

    def __init__(
        self,
        email: str,
        password: str,
        session: aiohttp.ClientSession | None = None,
    ) -> None:
        self._auth = BrinseaAuth(email, password)
        self._session = session
        self._owns_session = session is None

    async def _get_session(self) -> aiohttp.ClientSession:
        if self._session is None or self._session.closed:
            self._session = aiohttp.ClientSession()
            self._owns_session = True
        return self._session

    async def _request(self, method: str, path: str, **kwargs) -> dict:
        """Make an authenticated API request."""
        token = await self._auth.ensure_valid_token()
        session = await self._get_session()

        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
        }

        url = f"{API_BASE_URL}{path}"
        try:
            async with session.request(method, url, headers=headers, **kwargs) as resp:
                if resp.status != 200:
                    text = await resp.text()
                    raise BrinseaError(f"API error {resp.status}: {text}")
                data = await resp.json()
        except aiohttp.ClientError as err:
            raise BrinseaConnectionError(f"Connection error: {err}") from err

        if not data.get("success"):
            raise BrinseaError(f"API returned error: {data.get('error')}")

        return data

    async def authenticate(self) -> None:
        """Authenticate with the Brinsea API. Call to validate credentials."""
        await self._auth.authenticate()

    async def get_devices(self) -> list[Device]:
        """Get all devices associated with this account."""
        iid = self._auth.identity_id_b64
        data = await self._request("GET", f"{API_DEVICE_DB}?iid={iid}")

        devices = []
        for d in data.get("message", []):
            devices.append(
                Device(
                    id=d["id"],
                    name=d["name"],
                    model=d["model"],
                    firmware_id=d.get("firmwareId", ""),
                )
            )
        return devices

    async def get_device_status(self, device_id: str) -> DeviceStatus:
        """Get live status for a specific device."""
        iid = self._auth.identity_id_b64
        device_id_b64 = base64.b64encode(device_id.encode()).decode()
        data = await self._request(
            "GET",
            f"{API_DEVICE_CACHE}?iid={iid}&deviceId={device_id_b64}",
        )

        msg = data.get("message", {})
        return DeviceStatus(
            thing_id=msg.get("thingId", ""),
            temperature=msg.get("temperature"),
            humidity=msg.get("humidity"),
            connection_status=msg.get("connection_status", "unknown"),
        )

    async def close(self) -> None:
        """Close the client session."""
        if self._owns_session and self._session and not self._session.closed:
            await self._session.close()
