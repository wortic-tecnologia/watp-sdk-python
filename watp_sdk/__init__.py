"""Minimal Python SDK for the current WATP real contract."""

from .builders import (
    build_hash_cancelled,
    build_hash_concluded,
    build_hash_counter,
    build_hash_interest,
)
from .auth import build_node_signature, verify_node_signature
from .envelope import MessageEnvelope
from .hashing import compute_message_hash, utc_timestamp
from .types import MessageType, PayloadDict, PayloadMapping

__all__ = [
    "MessageEnvelope",
    "MessageType",
    "PayloadDict",
    "PayloadMapping",
    "build_hash_interest",
    "build_hash_counter",
    "build_hash_concluded",
    "build_hash_cancelled",
    "build_node_signature",
    "verify_node_signature",
    "compute_message_hash",
    "utc_timestamp",
]

__version__ = "0.1.0"
