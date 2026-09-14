from __future__ import annotations

from dataclasses import asdict
import hashlib
import json
from typing import Any, Mapping

from src.channel_gate import evaluate_channel_gate

MAPPER_VERSION = "v0.1"


def _canonical_hash(candidate: Mapping[str, Any]) -> str:
    payload = json.dumps(candidate, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def map_candidate(candidate: Mapping[str, Any]) -> dict[str, Any]:
    """Pure Shopify-canonical mapping preview. Never publishes and never persists state."""
    gate = evaluate_channel_gate(candidate)
    receipt = {
        "shopify_product_id": candidate.get("shopify_product_id"),
        "shopify_variant_id": candidate.get("shopify_variant_id"),
        "sku": candidate.get("sku"),
        "input_hash": _canonical_hash(candidate),
        "mapper_version": MAPPER_VERSION,
        "gate": asdict(gate),
        "publication_authority": False,
    }

    if not gate.eligible:
        return {"candidate": None, "receipt": receipt}

    mapped = {
        "source": "SHOPIFY",
        "shopify_product_id": candidate["shopify_product_id"],
        "shopify_variant_id": candidate["shopify_variant_id"],
        "sku": candidate["sku"],
        "title": candidate.get("title", "UNKNOWN"),
        "price_aud": candidate["price_aud"],
        "ebay_category_id": candidate.get("ebay_category_id", "UNKNOWN"),
        "gtin": candidate.get("gtin", "UNKNOWN"),
        "condition": candidate.get("condition", "UNKNOWN"),
        "inventory_quantity": candidate.get("inventory_quantity", "UNKNOWN"),
        "publication_authority": False,
    }
    return {"candidate": mapped, "receipt": receipt}
