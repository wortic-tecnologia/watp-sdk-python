from __future__ import annotations

import hmac
from hashlib import sha256


def build_node_signature(raw_body: str, secret: str) -> str:
    """Build the X-WATP-Node-Signature HMAC header value."""

    if not secret.strip():
        raise ValueError("secret is required")

    digest = hmac.new(secret.encode("utf-8"), raw_body.encode("utf-8"), sha256).hexdigest()
    return f"sha256={digest}"


def verify_node_signature(raw_body: str, signature: str, secret: str) -> bool:
    """Verify an X-WATP-Node-Signature header in constant time."""

    if not signature.strip() or not secret.strip():
        return False

    expected = build_node_signature(raw_body, secret)
    return hmac.compare_digest(expected, signature)