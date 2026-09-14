from __future__ import annotations

import hashlib
import json
from typing import Any, Mapping

SYNC_VERSION = "v0.1"


def _receipt(kind: str, payload: Mapping[str, Any]) -> dict[str, Any]:
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return {
        "kind": kind,
        "input_hash": hashlib.sha256(canonical.encode("utf-8")).hexdigest(),
        "sync_version": SYNC_VERSION,
        "publication_authority": False,
        "network_io": False,
    }


def inventory_change(event: Mapping[str, Any]) -> dict[str, Any]:
    required = ("event_id", "shopify_variant_id", "sku", "inventory_quantity")
    if any(event.get(key) in (None, "") for key in required):
        return {"accepted": False, "reason": "MISSING_SHOPIFY_INVENTORY_IDENTITY", "receipt": _receipt("inventory", event)}
    qty = event.get("inventory_quantity")
    if not isinstance(qty, int) or isinstance(qty, bool) or qty < 0:
        return {"accepted": False, "reason": "INVALID_INVENTORY_QUANTITY", "receipt": _receipt("inventory", event)}
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


def order_handoff(event: Mapping[str, Any]) -> dict[str, Any]:
    required = ("event_id", "ebay_order_id", "sku", "quantity")
    if any(event.get(key) in (None, "") for key in required):
        return {"accepted": False, "reason": "MISSING_EBAY_ORDER_IDENTITY", "receipt": _receipt("order", event)}
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


def tracking_update(event: Mapping[str, Any]) -> dict[str, Any]:
    required = ("event_id", "shopify_order_id", "ebay_order_id", "tracking_number")
    if any(event.get(key) in (None, "") for key in required):
        return {"accepted": False, "reason": "MISSING_TRACKING_CORRELATION", "receipt": _receipt("tracking", event)}
    return {
        "accepted": True,
        "candidate": {
            "shopify_order_id": event["shopify_order_id"],
            "ebay_order_id": event["ebay_order_id"],
            "tracking_number": event["tracking_number"],
        },
        "receipt": _receipt("tracking", event),
    }


def accept_once(event: Mapping[str, Any], seen_event_ids: frozenset[str]) -> dict[str, Any]:
    event_id = event.get("event_id")
    if not isinstance(event_id, str) or not event_id.strip():
        return {"accepted": False, "reason": "MISSING_EVENT_ID", "receipt": _receipt("dedupe", event)}
    if event_id in seen_event_ids:
        return {"accepted": False, "reason": "DUPLICATE_EVENT", "receipt": _receipt("dedupe", event)}
    return {"accepted": True, "event_id": event_id, "receipt": _receipt("dedupe", event)}
