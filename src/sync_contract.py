from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping
from src.channel_gate import canonical_identifier, shopify_identifier

SYNC_VERSION = "v0.3"


def _input_hash(payload: Mapping[str, Any]) -> str:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()


def _receipt(kind: str, payload: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "kind": kind,
        "input_hash": _input_hash(payload),
        "sync_version": SYNC_VERSION,
        "publication_authority": False,
        "production_mutation": False,
        "network_io": False,
        "canonical_commercial_authority": "SHOPIFY",
    }


def inventory_change(event: Mapping[str, Any], latest_revision: int | None = None) -> dict[str, Any]:
    required = ("event_id", "shopify_variant_id", "sku", "inventory_quantity")
    if any(event.get(key) in (None, "") for key in required):
        return {"accepted": False, "reason": "MISSING_SHOPIFY_INVENTORY_IDENTITY", "receipt": _receipt("inventory", event)}
    if not all(canonical_identifier(event.get(k)) for k in ("event_id", "sku")) or not shopify_identifier(event.get("shopify_variant_id"), "ProductVariant"):
        return {"accepted": False, "reason": "MALFORMED_INVENTORY_IDENTITY", "receipt": _receipt("inventory", event)}
    qty = event.get("inventory_quantity")
    if not isinstance(qty, int) or isinstance(qty, bool) or qty < 0:
        return {"accepted": False, "reason": "INVALID_INVENTORY_QUANTITY", "receipt": _receipt("inventory", event)}
    if latest_revision is not None:
        if not isinstance(latest_revision, int) or isinstance(latest_revision, bool) or latest_revision < 0:
            return {"accepted": False, "reason": "INVALID_LATEST_INVENTORY_REVISION", "receipt": _receipt("inventory", event)}
        revision = event.get("inventory_revision")
        if not isinstance(revision, int) or isinstance(revision, bool) or revision < 0:
            return {"accepted": False, "reason": "INVALID_INVENTORY_REVISION", "receipt": _receipt("inventory", event)}
        if revision <= latest_revision:
            return {"accepted": False, "reason": "STALE_INVENTORY_EVENT", "receipt": _receipt("inventory", event)}
    return {
        "accepted": True,
        "candidate": {
            "source": "SHOPIFY",
            "shopify_variant_id": event["shopify_variant_id"],
            "sku": event["sku"],
            "inventory_quantity": qty,
        },
        "receipt": _receipt("inventory", event),
    }


def order_handoff(event: Mapping[str, Any], seen_ebay_order_ids: frozenset[str] = frozenset()) -> dict[str, Any]:
    required = ("event_id", "ebay_order_id", "sku", "quantity")
    if any(event.get(key) in (None, "") for key in required):
        return {"accepted": False, "reason": "MISSING_EBAY_ORDER_IDENTITY", "receipt": _receipt("order", event)}
    if not all(canonical_identifier(event.get(k)) for k in ("event_id", "ebay_order_id", "sku")):
        return {"accepted": False, "reason": "MALFORMED_ORDER_IDENTITY", "receipt": _receipt("order", event)}
    if event["ebay_order_id"] in seen_ebay_order_ids:
        return {"accepted": False, "reason": "DUPLICATE_ORDER_IMPORT", "receipt": _receipt("order", event)}
    qty = event.get("quantity")
    if not isinstance(qty, int) or isinstance(qty, bool) or qty <= 0:
        return {"accepted": False, "reason": "INVALID_ORDER_QUANTITY", "receipt": _receipt("order", event)}
    return {
        "accepted": True,
        "shopify_order_candidate": {
            "source": "EBAY",
            "external_order_id": event["ebay_order_id"],
            "sku": event["sku"],
            "quantity": qty,
            "canonical_order_authority": "SHOPIFY",
        },
        "receipt": _receipt("order", event),
    }


def tracking_update(
    event: Mapping[str, Any],
    expected_correlation: tuple[str, str] | None = None,
    latest_sequence: int | None = None,
) -> dict[str, Any]:
    required = ("event_id", "shopify_order_id", "ebay_order_id", "tracking_number")
    if any(event.get(key) in (None, "") for key in required):
        return {"accepted": False, "reason": "MISSING_TRACKING_CORRELATION", "receipt": _receipt("tracking", event)}
    if not all(canonical_identifier(event.get(k)) for k in required):
        return {"accepted": False, "reason": "MALFORMED_TRACKING_IDENTITY", "receipt": _receipt("tracking", event)}
    if expected_correlation is not None:
        actual = (event["shopify_order_id"], event["ebay_order_id"])
        if actual != expected_correlation:
            return {"accepted": False, "reason": "TRACKING_CORRELATION_MISMATCH", "receipt": _receipt("tracking", event)}
    if latest_sequence is not None:
        sequence = event.get("tracking_sequence")
        if not isinstance(sequence, int) or isinstance(sequence, bool) or sequence <= latest_sequence:
            return {"accepted": False, "reason": "OUT_OF_ORDER_TRACKING_EVENT", "receipt": _receipt("tracking", event)}
    return {
        "accepted": True,
        "candidate": {
            "shopify_order_id": event["shopify_order_id"],
            "ebay_order_id": event["ebay_order_id"],
            "tracking_number": event["tracking_number"],
        },
        "receipt": _receipt("tracking", event),
    }


def accept_once(
    event: Mapping[str, Any],
    seen_event_ids: frozenset[str],
    seen_input_hashes: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    event_id = event.get("event_id")
    receipt = _receipt("dedupe", event)
    if not isinstance(event_id, str) or not event_id.strip():
        return {"accepted": False, "reason": "MISSING_EVENT_ID", "receipt": receipt}
    if not canonical_identifier(event_id):
        return {"accepted": False, "reason": "NON_CANONICAL_EVENT_ID", "receipt": receipt}
    if seen_input_hashes is not None and event_id in seen_input_hashes:
        receipt["prior_input_hash"] = seen_input_hashes[event_id]
        if event_id not in seen_event_ids:
            return {"accepted": False, "reason": "INCONSISTENT_REPLAY_EVIDENCE", "receipt": receipt}
    if event_id in seen_event_ids:
        if seen_input_hashes is not None:
            prior_hash = seen_input_hashes.get(event_id)
            if prior_hash is not None and prior_hash != receipt["input_hash"]:
                return {"accepted": False, "reason": "EVENT_ID_PAYLOAD_CONFLICT", "receipt": receipt}
        return {"accepted": False, "reason": "DUPLICATE_EVENT", "receipt": receipt}
    return {"accepted": True, "event_id": event_id, "receipt": receipt}
