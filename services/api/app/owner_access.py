"""Validate the trusted web service and its owner identity assertion."""

from __future__ import annotations

import hmac
import re


_TOKEN = re.compile(r"[A-Za-z0-9_-]{43,128}")
_SUBJECT = re.compile(r"[a-z][a-z0-9_-]{0,62}")


class InternalAccessNotConfigured(ValueError):
    """The owner-demo service token is absent or malformed."""


def valid_internal_token(configured: str | None, supplied: str | None) -> bool:
    """Constant-time comparison after validating a server-side token format.

    Generate the token using a cryptographically secure random source with at
    least 32 bytes of entropy. Format validation cannot prove entropy.
    """
    if not isinstance(configured, str) or not _TOKEN.fullmatch(configured):
        raise InternalAccessNotConfigured("Owner demo internal access is not configured")
    if not isinstance(supplied, str) or not _TOKEN.fullmatch(supplied):
        return False
    return hmac.compare_digest(configured, supplied)


def valid_owner_subject(configured: str | None, supplied: str | None) -> bool:
    """Accept only the one subject assigned to this isolated owner instance."""
    if not isinstance(configured, str) or not _SUBJECT.fullmatch(configured):
        raise InternalAccessNotConfigured("Owner demo identity is not configured")
    return supplied == configured
