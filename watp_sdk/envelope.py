from __future__ import annotations

import json
import ipaddress
from dataclasses import dataclass
from typing import Any, Mapping
from urllib.parse import urlparse

from .hashing import build_canonical_hash_input, canonical_json_dumps
from .types import MessageType, PayloadDict


def _coerce_payload(payload: Mapping[str, Any]) -> PayloadDict:
    return dict(payload)


def _payload_has_identity(payload: PayloadDict) -> bool:
    return any(payload.get(field) for field in ("sku", "item", "product_name"))


def _payload_qty(payload: PayloadDict) -> float | None:
    raw_qty = payload.get("qty", payload.get("quantity"))
    if raw_qty is None:
        return None
    try:
        return float(raw_qty)
    except (TypeError, ValueError):
        return None


def _payload_price(payload: PayloadDict) -> float | None:
    raw_price = payload.get("unit_price", payload.get("price"))
    if raw_price is None:
        return None
    try:
        return float(raw_price)
    except (TypeError, ValueError):
        return None


@dataclass(slots=True, kw_only=True)
class MessageEnvelope:
    id: str
    negotiation_id: str | None
    type: MessageType
    payload: PayloadDict
    hash: str
    previous_hash: str | None
    timestamp: str
    sender: str
    signature: str | None = None

    def __post_init__(self) -> None:
        self.type = MessageType.coerce(self.type)
        self.payload = _coerce_payload(self.payload)
        self._validate()

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "MessageEnvelope":
        payload = data.get("payload")
        if not isinstance(payload, Mapping):
            raise ValueError("WATP envelope requires a mapping payload.")

        return cls(
            id=_required_string(data.get("id"), field_name="id"),
            negotiation_id=_optional_string(data.get("negotiation_id")),
            type=MessageType.coerce(data["type"]),
            payload=dict(payload),
            hash=_required_string(data.get("hash"), field_name="hash"),
            previous_hash=_optional_string(data.get("previousHash") or data.get("prev_hash")),
            timestamp=_required_string(data.get("timestamp"), field_name="timestamp"),
            sender=_required_string(data.get("sender"), field_name="sender"),
            signature=_optional_string(data.get("signature")),
        )

    def _validate(self) -> None:
        if not self.id:
            raise ValueError("WATP envelope requires id.")
        if not self.sender:
            raise ValueError("WATP envelope requires sender.")
        if not self.hash:
            raise ValueError("WATP envelope requires a hash.")
        if not self.timestamp:
            raise ValueError("WATP envelope requires a timestamp.")
        if self.type is not MessageType.HASH_INTEREST and not self.negotiation_id:
            raise ValueError(f"{self.type.value} requires negotiation_id.")

        if self.type is not MessageType.HASH_INTEREST and not self.previous_hash:
            raise ValueError(f"{self.type.value} requires previousHash.")

        if self.type is MessageType.HASH_CANCELLED:
            return

        if not _payload_has_identity(self.payload):
            raise ValueError("Payload must include sku, item, or product_name.")

        qty = _payload_qty(self.payload)
        if qty is None or qty <= 0:
            raise ValueError("Payload must include qty or quantity greater than zero.")

        price = _payload_price(self.payload)
        if price is None or price < 0:
            raise ValueError("Payload must include unit_price or price greater than or equal to zero.")

        if self.type is MessageType.HASH_INTEREST and not _is_public_https_url(self.payload.get("buyer_url"), allow_query=False):
            raise ValueError("buyer_url is required for HASH_INTEREST and must be a public HTTPS URL.")

        payment_url = self.payload.get("payment_url")
        if payment_url and not _is_public_https_url(payment_url, allow_query=True):
            raise ValueError("payment_url must be a public HTTPS URL.")

    def canonical_hash_input(self) -> dict[str, object]:
        return build_canonical_hash_input(
            message_type=self.type,
            payload=self.payload,
            previous_hash=self.previous_hash,
            timestamp=self.timestamp,
        )

    def to_dict(self, *, include_nulls: bool = False) -> dict[str, Any]:
        data: dict[str, Any] = {
            "id": self.id,
            "negotiation_id": self.negotiation_id,
            "type": self.type.value,
            "payload": dict(self.payload),
            "hash": self.hash,
            "previousHash": self.previous_hash,
            "timestamp": self.timestamp,
            "sender": self.sender,
            "signature": self.signature,
        }
        if include_nulls:
            return data
        return {key: value for key, value in data.items() if value is not None}

    def to_json(self, *, include_nulls: bool = False) -> str:
        return json.dumps(
            self.to_dict(include_nulls=include_nulls),
            ensure_ascii=False,
            separators=(",", ":"),
            sort_keys=False,
        )

    def canonical_hash_json(self) -> str:
        return canonical_json_dumps(self.canonical_hash_input())


def _optional_string(value: Any) -> str | None:
    if value is None:
        return None
    return str(value)


def _required_string(value: Any, *, field_name: str) -> str:
    if value is None or value == "":
        raise ValueError(f"WATP envelope requires {field_name}.")
    return str(value)


def _is_public_https_url(value: Any, *, allow_query: bool) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False

    parsed = urlparse(value)
    host = (parsed.hostname or "").lower()
    if parsed.scheme != "https" or not host:
        return False

    if parsed.username or parsed.password or parsed.fragment:
        return False

    if parsed.query and not allow_query:
        return False

    if host == "localhost" or host.endswith(".local") or host.endswith(".internal"):
        return False

    try:
        ip = ipaddress.ip_address(host)
    except ValueError:
        return True

    return not (ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast)
