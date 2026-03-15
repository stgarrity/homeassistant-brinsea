"""Exceptions for Brinsea Connect API."""


class BrinseaError(Exception):
    """Base exception for Brinsea API."""


class BrinseaAuthError(BrinseaError):
    """Authentication failed."""


class BrinseaConnectionError(BrinseaError):
    """Connection to Brinsea API failed."""
