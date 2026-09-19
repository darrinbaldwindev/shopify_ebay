from __future__ import annotations

from dataclasses import dataclass
import re
import math
from typing import Any, Mapping

DENIALS = {
    "MISSING_SHOPIFY_IDENTITY", "MISSING_SKU", "MARKETPLACE_PERMISSION_NOT_ELIGIBLE",
    "CONFLICTING_MARKETPLACE_PERMISSION_EVIDENCE", "FREIGHT_UNKNOWN", "CONFLICTING_FREIGHT_EVIDENCE",
    "TRADE_COST_UNKNOWN", "CONFLICTING_TRADE_COST_EVIDENCE", "CHANNEL_FEE_EVIDENCE_UNKNOWN",
    "CONFLICTING_CHANNEL_FEE_EVIDENCE", "FULFILMENT_IDENTITY_UNKNOWN", "CONFLICTING_FULFILMENT_IDENTITY_EVIDENCE",
    "PRICE_INVALID", "INVENTORY_CONTROL_UNKNOWN", "STALE_INVENTORY_EVIDENCE", "CONFLICTING_INVENTORY_EVIDENCE",
    "STALE_SOURCE_IDENTITY", "CONFLICTING_SOURCE_IDENTITY_EVIDENCE", "CHANNEL_ECONOMICS_NOT_POSITIVE",
}

@dataclass(frozen=True)
class GateResult:
    eligible: bool
    reason: str
    sku: str | None

def _present(value: Any) -> bool:
    return value is not None and (not isinstance(value, str) or bool(value.strip()))

def canonical_identifier(value: Any) -> bool:
    return isinstance(value, str) and bool(value) and value == value.strip() and all(ord(c) >= 32 and ord(c) != 127 for c in value)

def shopify_identifier(value: Any, kind: str) -> bool:
    return isinstance(value, str) and re.fullmatch(r"gid://shopify/" + kind + r"/[1-9][0-9]*", value) is not None

def evaluate_channel_gate(candidate: Mapping[str, Any]) -> GateResult:
    """Pure V0 eBay mapping gate; no I/O/state mutation and no publication authority."""
    product_id, variant_id, sku = candidate.get("shopify_product_id"), candidate.get("shopify_variant_id"), candidate.get("sku")
    if not (_present(product_id) and _present(variant_id)): return GateResult(False, "MISSING_SHOPIFY_IDENTITY", sku if _present(sku) else None)
    if not _present(sku): return GateResult(False, "MISSING_SKU", None)
    if not shopify_identifier(product_id, "Product") or not shopify_identifier(variant_id, "ProductVariant"):
        return GateResult(False, "MALFORMED_SHOPIFY_IDENTITY", None)
    if not canonical_identifier(sku): return GateResult(False, "MALFORMED_SKU", None)
    sku = str(sku)
    if candidate.get("source_identity_conflict") is True: return GateResult(False, "CONFLICTING_SOURCE_IDENTITY_EVIDENCE", sku)
    if candidate.get("source_identity_current") is not True: return GateResult(False, "STALE_SOURCE_IDENTITY", sku)
    if candidate.get("marketplace_permission_conflict") is True: return GateResult(False, "CONFLICTING_MARKETPLACE_PERMISSION_EVIDENCE", sku)
    if candidate.get("marketplace_permission") != "EBAY-ELIGIBLE": return GateResult(False, "MARKETPLACE_PERMISSION_NOT_ELIGIBLE", sku)
    if candidate.get("trade_cost_evidence_conflict") is True: return GateResult(False, "CONFLICTING_TRADE_COST_EVIDENCE", sku)
    if candidate.get("supplier_trade_cost_known") is not True: return GateResult(False, "TRADE_COST_UNKNOWN", sku)
    if candidate.get("freight_evidence_conflict") is True: return GateResult(False, "CONFLICTING_FREIGHT_EVIDENCE", sku)
    if candidate.get("freight_landed_cost_known") is not True: return GateResult(False, "FREIGHT_UNKNOWN", sku)
    if candidate.get("channel_fee_evidence_conflict") is True: return GateResult(False, "CONFLICTING_CHANNEL_FEE_EVIDENCE", sku)
    if candidate.get("marketplace_plan_fee_known") is not True or candidate.get("category_fee_known") is not True: return GateResult(False, "CHANNEL_FEE_EVIDENCE_UNKNOWN", sku)
    if candidate.get("fulfilment_identity_evidence_conflict") is True: return GateResult(False, "CONFLICTING_FULFILMENT_IDENTITY_EVIDENCE", sku)
    if candidate.get("fulfilment_seller_identity_known") is not True: return GateResult(False, "FULFILMENT_IDENTITY_UNKNOWN", sku)
    if candidate.get("inventory_evidence_conflict") is True: return GateResult(False, "CONFLICTING_INVENTORY_EVIDENCE", sku)
    if candidate.get("inventory_control_evidence") is not True: return GateResult(False, "INVENTORY_CONTROL_UNKNOWN", sku)
    if candidate.get("inventory_evidence_fresh") is not True: return GateResult(False, "STALE_INVENTORY_EVIDENCE", sku)
    price = candidate.get("price_aud")
    if not isinstance(price, (int, float)) or isinstance(price, bool) or (isinstance(price, float) and not math.isfinite(price)) or price <= 0: return GateResult(False, "PRICE_INVALID", sku)
    contribution = candidate.get("channel_contribution_aud")
    if not isinstance(contribution, (int, float)) or isinstance(contribution, bool) or (isinstance(contribution, float) and not math.isfinite(contribution)) or contribution <= 0: return GateResult(False, "CHANNEL_ECONOMICS_NOT_POSITIVE", sku)
    return GateResult(True, "ELIGIBLE_FOR_MAPPING_ONLY", sku)
