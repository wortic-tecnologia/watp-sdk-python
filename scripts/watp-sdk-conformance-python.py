#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SDK_ROOT = ROOT / "sdk" / "python"
if not SDK_ROOT.exists():
    SDK_ROOT = ROOT
sys.path.insert(0, str(SDK_ROOT))

from watp_sdk import MessageEnvelope, build_node_signature, compute_message_hash, verify_node_signature  # noqa: E402

EXPECTED = {
    "valid-hash-interest.json": True,
    "valid-hash-concluded-payment-url.json": True,
    "invalid-hash-interest-missing-buyer-url.json": False,
    "invalid-hash-counter-missing-negotiation-id.json": False,
    "invalid-hash-concluded-invalid-payment-url.json": False,
}


def main() -> int:
    failures = 0
    fixtures_dir = ROOT / "protocol" / "fixtures"

    for file_name, should_pass in EXPECTED.items():
        data = json.loads((fixtures_dir / file_name).read_text(encoding="utf-8"))

        try:
            envelope = MessageEnvelope.from_dict(data)
            computed_hash = compute_message_hash(
                message_type=envelope.type,
                payload=envelope.payload,
                previous_hash=envelope.previous_hash,
                timestamp=envelope.timestamp,
            )
            if computed_hash != envelope.hash:
                raise ValueError(f"hash mismatch: {computed_hash} != {envelope.hash}")
        except ValueError as exc:
            if should_pass:
                failures += 1
                print(f"FAIL {file_name}: expected valid, got {exc}", file=sys.stderr)
                continue
        else:
            if not should_pass:
                failures += 1
                print(f"FAIL {file_name}: expected invalid, got valid", file=sys.stderr)
                continue

        print(f"OK {file_name}")

    if failures:
        return 1

    expected_signature = "sha256=e94d4c3acf8e7f838218bb8aa3ab6e98f6a78b0755421a81efd1d96497e19411"
    signature = build_node_signature("{}", "secret-a")
    if (
        signature != expected_signature
        or not verify_node_signature("{}", signature, "secret-a")
        or verify_node_signature("{}", signature, "wrong-secret")
    ):
        print("FAIL shared HMAC signature vector", file=sys.stderr)
        return 1

    whole_number_hash = compute_message_hash(
        message_type="HASH_INTEREST",
        payload={"sku": "SKU-100", "qty": 1, "unit_price": 100.0, "currency": "BRL"},
        previous_hash=None,
        timestamp="2026-04-28T00:00:00.000000Z",
    )
    if whole_number_hash != "351a76ec467a22fcdde02586af196e866f0fd07e3609b3b145be568b4e02d56a":
        print("FAIL PHP-compatible whole-number float hash vector", file=sys.stderr)
        return 1

    print("Python SDK conformance: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())