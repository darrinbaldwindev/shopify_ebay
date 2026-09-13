from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

DENIALS = {
    "MISSING_SHOPIFY_IDENTITY",
    "MISSING_SKU",
    "MARKETPLACE_PERMISSION_NOT_ELIGIBLE",
    "FREIGHT_UNKNOWN",
    "FULFILMENT_IDENTITY_UNKNOWN",
    "PRICE_INVALID",
    "INVENTORY_CONTROL_UNKNOWN",
    "STALE_SOURCE_IDENTITY",
    "CHANNEL_ECONOMICS_NOT_POSITIVE",
}


@dataclass(frozen=True)
class GateResult:
    eligible: bool
    reason: str
    sku: str | None


def _present(value: Any) -> bool:
    return value is not None and (not isinstance(value, str) or bool(value.strip()))


def evaluate_channel_gate(candidate: Mapping[str, Any]) -> GateResult:
    """Pure V0 eBay eligibility gate. No I/O and no state mutation."""
    product_id = candidate.get("shopify_product_id")
    variant_id = candidate.get("shopify_variant_id")
    sku = candidate.get("sku")

    if not (_present(product_id) and _present(variant_id)):
        return GateResult(False, "MISSING_SHOPIFY_IDENTITY", sku if _present(sku) else None)
    if not _present(sku):
        return GateResult(False, "MISSING_SKU", None)

    if candidate.get("source_identity_current") is not True:
        return GateResult(False, "STALE_SOURCE_IDENTITY", str(sku))

    if candidate.get("marketplace_permission") != "EBAY-ELIGIBLE":
        return GateResult(False, "MARKETPLACE_PERMISSION_NOT_ELIGIBLE", str(sku))

    if candidate.get("freight_landed_cost_known") is not True:
        return GateResult(False, "FREIGHT_UNKNOWN", str(sku))

    if candidate.get("fulfilment_seller_identity_known") is not True:
        return GateResult(False, "FULFILMENT_IDENTITY_UNKNOWN", str(sku))

    if candidate.get("inventory_control_evidence") is not True:
        return GateResult(False, "INVENTORY_CONTROL_UNKNOWN", str(sku))

    price = candidate.get("price_aud")
    if not isinstance(price, (int, float)) or isinstance(price, bool) or price <= 0:
        return GateResult(False, "PRICE_INVALID", str(sku))

    contribution = candidate.get("channel_contribution_aud")
    if not isinstance(contribution, (int, float)) or isinstance(contribution, bool) or contribution <= 0:
        return GateResult(False, "CHANNEL_ECONOMICS_NOT_POSITIVE", str(sku))

    return GateResult(True, "ELIGIBLE_FOR_MAPPING_ONLY", str(sku))
