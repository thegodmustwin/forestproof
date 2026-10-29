"""Internal service authentication for an isolated, synthetic owner demo.

This is not end-user authentication. The web service must be reachable only
through the separately authenticated owner gateway; both services must bind to
the trusted host's loopback interface. LIVE mode remains disabled.
"""

from __future__ import annotations

import hmac
import re


_TOKEN = re.compile(r"[A-Za-z0-9_-]{43,128}")


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
