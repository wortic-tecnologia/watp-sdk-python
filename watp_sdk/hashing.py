from __future__ import annotations

import hashlib
import json
import math
from datetime import datetime, timezone

from .types import MessageType, PayloadMapping


def utc_timestamp() -> str:
    """Return a UTC timestamp compatible with the current WATP runtime."""

    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


def build_canonical_hash_input(
    *,
    message_type: str | MessageType,
    payload: PayloadMapping,
    previous_hash: str | None,
    timestamp: str,
) -> dict[str, object]:
    """
    Build the exact JSON structure hashed by the current PHP runtime.

    Important: payload key order is preserved on purpose to match the runtime
    behavior in the canonical supplier implementation.
    """

    return {
        "type": MessageType.coerce(message_type).value,
        "payload": dict(payload),
        "previousHash": previous_hash,
        "timestamp": timestamp,
    }


def canonical_json_dumps(value: object) -> str:
    """Serialize compact JSON without reordering keys."""

    return json.dumps(_normalize_php_json_numbers(value), ensure_ascii=False, separators=(",", ":"), sort_keys=False)


def _normalize_php_json_numbers(value: object) -> object:
    if isinstance(value, float) and math.isfinite(value) and value.is_integer():
        return int(value)

    if isinstance(value, dict):
        return {key: _normalize_php_json_numbers(item) for key, item in value.items()}

    if isinstance(value, list):
        return [_normalize_php_json_numbers(item) for item in value]

    return value


def compute_message_hash(
    *,
    message_type: str | MessageType,
    payload: PayloadMapping,
    previous_hash: str | None,
    timestamp: str,
) -> str:
    """Compute the WATP SHA-256 message hash used in the current runtime."""

    canonical = canonical_json_dumps(
        build_canonical_hash_input(
            message_type=message_type,
            payload=payload,
            previous_hash=previous_hash,
            timestamp=timestamp,
        )
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()
