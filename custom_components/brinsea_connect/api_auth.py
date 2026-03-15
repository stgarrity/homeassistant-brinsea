"""Cognito SRP authentication for Brinsea Connect."""

import asyncio
import base64
import json
import logging
from functools import partial

from pycognito import Cognito

from .api_const import COGNITO_CLIENT_ID, COGNITO_REGION, COGNITO_USER_POOL_ID
from .api_exceptions import BrinseaAuthError

_LOGGER = logging.getLogger(__name__)


class BrinseaAuth:
    """Handle Cognito SRP authentication."""

    def __init__(self, email: str, password: str) -> None:
        self._email = email
        self._password = password
        self._cognito: Cognito | None = None
        self._identity_id: str | None = None

    @property
    def id_token(self) -> str | None:
        """Return the current ID token."""
        if self._cognito is None:
            return None
        return self._cognito.id_token

    @property
    def identity_id(self) -> str | None:
        """Return the Cognito identity ID extracted from the ID token."""
        return self._identity_id

    @property
    def identity_id_b64(self) -> str | None:
        """Return base64-encoded identity ID for API calls."""
        if self._identity_id is None:
            return None
        return base64.b64encode(self._identity_id.encode()).decode()

    def _authenticate_sync(self) -> None:
        """Perform synchronous Cognito SRP auth."""
        try:
            self._cognito = Cognito(
                COGNITO_USER_POOL_ID,
                COGNITO_CLIENT_ID,
                username=self._email,
            )
            self._cognito.authenticate(password=self._password)
            self._extract_identity_id()
        except Exception as err:
            raise BrinseaAuthError(f"Authentication failed: {err}") from err

    def _refresh_sync(self) -> None:
        """Refresh tokens synchronously."""
        try:
            self._cognito.renew_access_token()
            self._extract_identity_id()
        except Exception as err:
            raise BrinseaAuthError(f"Token refresh failed: {err}") from err

    def _extract_identity_id(self) -> None:
        """Extract identity ID from the ID token claims."""
        if self._cognito and self._cognito.id_token:
            # Decode JWT payload (second segment)
            payload = self._cognito.id_token.split(".")[1]
            # Add padding
            padding = 4 - len(payload) % 4
            if padding != 4:
                payload += "=" * padding
            claims = json.loads(base64.b64decode(payload))
            self._identity_id = claims.get("custom:identityId")

    async def authenticate(self) -> None:
        """Authenticate with Cognito (async wrapper)."""
        await asyncio.to_thread(self._authenticate_sync)

    async def refresh(self) -> None:
        """Refresh auth tokens (async wrapper)."""
        await asyncio.to_thread(self._refresh_sync)

    async def ensure_valid_token(self) -> str:
        """Return a valid ID token, refreshing if needed."""
        if self._cognito is None:
            await self.authenticate()
        else:
            try:
                await self.refresh()
            except BrinseaAuthError:
                _LOGGER.debug("Refresh failed, re-authenticating")
                await self.authenticate()
        return self.id_token
