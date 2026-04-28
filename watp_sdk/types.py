from __future__ import annotations

from enum import Enum
from typing import Any, Mapping, TypeAlias

PayloadDict: TypeAlias = dict[str, Any]
PayloadMapping: TypeAlias = Mapping[str, Any]


class MessageType(str, Enum):
    HASH_INTEREST = "HASH_INTEREST"
    HASH_COUNTER = "HASH_COUNTER"
    HASH_CONCLUDED = "HASH_CONCLUDED"
    HASH_CANCELLED = "HASH_CANCELLED"

    @classmethod
    def coerce(cls, value: str | "MessageType") -> "MessageType":
        if isinstance(value, cls):
            return value
        try:
            return cls(value)
        except ValueError as exc:
            expected = ", ".join(member.value for member in cls)
            raise ValueError(f"Unsupported WATP message type: {value!r}. Expected one of: {expected}.") from exc
