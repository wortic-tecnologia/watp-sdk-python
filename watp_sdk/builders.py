from __future__ import annotations

from typing import Any
from uuid import uuid4

from .envelope import MessageEnvelope
from .hashing import compute_message_hash, utc_timestamp
from .types import MessageType, PayloadDict, PayloadMapping


def build_hash_interest(
    *,
    sku: str | None = None,
    item: str | None = None,
    product_name: str | None = None,
    qty: int,
    unit_price: float | None = None,
    price: float | None = None,
    currency: str | None = None,
    buyer: str | None = None,
    buyer_name: str | None = None,
    buyer_url: str | None = None,
    billing: PayloadMapping | None = None,
    message: str | None = None,
    sender: str | None = None,
    negotiation_id: str | None = None,
    timestamp: str | None = None,
    message_id: str | None = None,
    signature: str | None = None,
    extra_payload: PayloadMapping | None = None,
) -> MessageEnvelope:
    payload = _merge_extra_payload(
        _base_trade_payload(
            sku=sku,
            item=item,
            product_name=product_name,
            qty=qty,
            unit_price=unit_price,
            price=price,
            currency=currency,
        ),
        extra_payload,
    )
    _assign_optional(payload, "buyer", buyer)
    _assign_optional(payload, "buyer_name", buyer_name)
    _assign_optional(payload, "buyer_url", buyer_url)
    _assign_optional(payload, "billing", dict(billing) if billing is not None else None)
    _assign_optional(payload, "message", message)

    return _build_message(
        message_type=MessageType.HASH_INTEREST,
        payload=payload,
        negotiation_id=negotiation_id,
        previous_hash=None,
        sender=sender,
        timestamp=timestamp,
        message_id=message_id,
        signature=signature,
    )


def build_hash_counter(
    *,
    negotiation_id: str,
    previous_hash: str,
    sku: str | None = None,
    item: str | None = None,
    product_name: str | None = None,
    qty: int,
    unit_price: float | None = None,
    price: float | None = None,
    currency: str | None = None,
    counter_by: str | None = None,
    agent: str | None = None,
    message: str | None = None,
    sender: str | None = None,
    timestamp: str | None = None,
    message_id: str | None = None,
    signature: str | None = None,
    extra_payload: PayloadMapping | None = None,
) -> MessageEnvelope:
    payload = _merge_extra_payload(
        _base_trade_payload(
            sku=sku,
            item=item,
            product_name=product_name,
            qty=qty,
            unit_price=unit_price,
            price=price,
            currency=currency,
        ),
        extra_payload,
    )
    _assign_optional(payload, "counter_by", counter_by)
    _assign_optional(payload, "agent", agent)
    _assign_optional(payload, "message", message)

    return _build_message(
        message_type=MessageType.HASH_COUNTER,
        payload=payload,
        negotiation_id=negotiation_id,
        previous_hash=previous_hash,
        sender=sender,
        timestamp=timestamp,
        message_id=message_id,
        signature=signature,
    )


def build_hash_concluded(
    *,
    negotiation_id: str,
    previous_hash: str,
    sku: str | None = None,
    item: str | None = None,
    product_name: str | None = None,
    qty: int,
    unit_price: float | None = None,
    price: float | None = None,
    currency: str | None = None,
    accepted_by: str | None = None,
    approved_by: str | None = None,
    payment_url: str | None = None,
    message: str | None = None,
    sender: str | None = None,
    timestamp: str | None = None,
    message_id: str | None = None,
    signature: str | None = None,
    extra_payload: PayloadMapping | None = None,
) -> MessageEnvelope:
    payload = _merge_extra_payload(
        _base_trade_payload(
            sku=sku,
            item=item,
            product_name=product_name,
            qty=qty,
            unit_price=unit_price,
            price=price,
            currency=currency,
        ),
        extra_payload,
    )
    _assign_optional(payload, "accepted_by", accepted_by)
    _assign_optional(payload, "approved_by", approved_by)
    _assign_optional(payload, "payment_url", payment_url)
    _assign_optional(payload, "message", message)

    return _build_message(
        message_type=MessageType.HASH_CONCLUDED,
        payload=payload,
        negotiation_id=negotiation_id,
        previous_hash=previous_hash,
        sender=sender,
        timestamp=timestamp,
        message_id=message_id,
        signature=signature,
    )


def build_hash_cancelled(
    *,
    negotiation_id: str,
    previous_hash: str,
    reason: str | None = None,
    message: str | None = None,
    approved_by: str | None = None,
    agent: str | None = None,
    sender: str | None = None,
    timestamp: str | None = None,
    message_id: str | None = None,
    signature: str | None = None,
    extra_payload: PayloadMapping | None = None,
) -> MessageEnvelope:
    payload: PayloadDict = {}
    _assign_optional(payload, "reason", reason)
    _assign_optional(payload, "message", message)
    _assign_optional(payload, "approved_by", approved_by)
    _assign_optional(payload, "agent", agent)
    payload = _merge_extra_payload(payload, extra_payload)

    return _build_message(
        message_type=MessageType.HASH_CANCELLED,
        payload=payload,
        negotiation_id=negotiation_id,
        previous_hash=previous_hash,
        sender=sender,
        timestamp=timestamp,
        message_id=message_id,
        signature=signature,
    )


def _build_message(
    *,
    message_type: MessageType,
    payload: PayloadMapping,
    negotiation_id: str | None,
    previous_hash: str | None,
    sender: str | None,
    timestamp: str | None,
    message_id: str | None,
    signature: str | None,
) -> MessageEnvelope:
    message_timestamp = timestamp or utc_timestamp()
    message_hash = compute_message_hash(
        message_type=message_type,
        payload=payload,
        previous_hash=previous_hash,
        timestamp=message_timestamp,
    )
    return MessageEnvelope(
        id=message_id or str(uuid4()),
        negotiation_id=negotiation_id,
        type=message_type,
        payload=dict(payload),
        hash=message_hash,
        previous_hash=previous_hash,
        timestamp=message_timestamp,
        sender=sender,
        signature=signature,
    )


def _base_trade_payload(
    *,
    sku: str | None,
    item: str | None,
    product_name: str | None,
    qty: int,
    unit_price: float | None,
    price: float | None,
    currency: str | None,
) -> PayloadDict:
    if unit_price is None and price is None:
        raise ValueError("Provide unit_price or price.")

    payload: PayloadDict = {}
    _assign_optional(payload, "sku", sku)
    _assign_optional(payload, "item", item)
    _assign_optional(payload, "product_name", product_name)
    payload["qty"] = qty
    if unit_price is not None:
        payload["unit_price"] = unit_price
    else:
        payload["price"] = price
    _assign_optional(payload, "currency", currency)
    return payload


def _merge_extra_payload(payload: PayloadDict, extra_payload: PayloadMapping | None) -> PayloadDict:
    if extra_payload is None:
        return payload

    duplicate_keys = set(payload).intersection(extra_payload)
    if duplicate_keys:
        duplicate_keys_csv = ", ".join(sorted(duplicate_keys))
        raise ValueError(f"extra_payload contains keys already set by the builder: {duplicate_keys_csv}.")

    for key, value in extra_payload.items():
        payload[key] = value
    return payload


def _assign_optional(payload: PayloadDict, key: str, value: Any) -> None:
    if value is not None:
        payload[key] = value
