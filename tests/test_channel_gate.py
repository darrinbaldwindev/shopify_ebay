import copy
import unittest

from src.channel_gate import evaluate_channel_gate


BASE = {
    "shopify_product_id": "gid://shopify/Product/100",
    "shopify_variant_id": "gid://shopify/ProductVariant/200",
    "sku": "SYNTH-001",
    "source_identity_current": True,
    "marketplace_permission": "EBAY-ELIGIBLE",
    "supplier_trade_cost_known": True,
    "freight_landed_cost_known": True,
    "marketplace_plan_fee_known": True,
    "category_fee_known": True,
    "fulfilment_seller_identity_known": True,
    "inventory_control_evidence": True,
    "inventory_evidence_fresh": True,
    "price_aud": 49.95,
    "channel_contribution_aud": 8.25,
}


class ChannelGateTests(unittest.TestCase):
    def result_for(self, **changes):
        case = copy.deepcopy(BASE)
        case.update(changes)
        return evaluate_channel_gate(case)

    def test_eligible_fixture_is_mapping_only(self):
        result = self.result_for()
        self.assertTrue(result.eligible)
        self.assertEqual(result.reason, "ELIGIBLE_FOR_MAPPING_ONLY")

    def test_missing_variant_denied(self):
        self.assertEqual(self.result_for(shopify_variant_id=None).reason, "MISSING_SHOPIFY_IDENTITY")

    def test_blank_sku_denied(self):
        self.assertEqual(self.result_for(sku=" ").reason, "MISSING_SKU")

    def test_permission_required_denied(self):
        self.assertEqual(self.result_for(marketplace_permission="PERMISSION-REQUIRED").reason, "MARKETPLACE_PERMISSION_NOT_ELIGIBLE")

    def test_unknown_permission_denied(self):
        self.assertEqual(self.result_for(marketplace_permission="UNKNOWN").reason, "MARKETPLACE_PERMISSION_NOT_ELIGIBLE")

    def test_conflicting_permission_evidence_denied_even_if_positive_value_present(self):
        self.assertEqual(self.result_for(marketplace_permission_conflict=True).reason, "CONFLICTING_MARKETPLACE_PERMISSION_EVIDENCE")

    def test_unknown_trade_cost_denied(self):
        self.assertEqual(self.result_for(supplier_trade_cost_known=False).reason, "TRADE_COST_UNKNOWN")

    def test_unknown_freight_denied(self):
        self.assertEqual(self.result_for(freight_landed_cost_known=False).reason, "FREIGHT_UNKNOWN")

    def test_unknown_plan_fee_denied(self):
        self.assertEqual(self.result_for(marketplace_plan_fee_known=False).reason, "CHANNEL_FEE_EVIDENCE_UNKNOWN")

    def test_unknown_category_fee_denied(self):
        self.assertEqual(self.result_for(category_fee_known=False).reason, "CHANNEL_FEE_EVIDENCE_UNKNOWN")

    def test_unknown_fulfilment_identity_denied(self):
        self.assertEqual(self.result_for(fulfilment_seller_identity_known=False).reason, "FULFILMENT_IDENTITY_UNKNOWN")

    def test_zero_price_denied(self):
        self.assertEqual(self.result_for(price_aud=0).reason, "PRICE_INVALID")

    def test_inventory_control_unknown_denied(self):
        self.assertEqual(self.result_for(inventory_control_evidence=False).reason, "INVENTORY_CONTROL_UNKNOWN")

    def test_stale_inventory_evidence_denied(self):
        self.assertEqual(self.result_for(inventory_evidence_fresh=False).reason, "STALE_INVENTORY_EVIDENCE")

    def test_conflicting_inventory_evidence_denied_even_if_current_flag_is_true(self):
        self.assertEqual(self.result_for(inventory_evidence_conflict=True).reason, "CONFLICTING_INVENTORY_EVIDENCE")

    def test_stale_source_identity_denied(self):
        self.assertEqual(self.result_for(source_identity_current=False).reason, "STALE_SOURCE_IDENTITY")

    def test_conflicting_source_identity_denied_even_if_current_flag_is_true(self):
        self.assertEqual(self.result_for(source_identity_conflict=True).reason, "CONFLICTING_SOURCE_IDENTITY_EVIDENCE")

    def test_non_positive_channel_contribution_denied(self):
        self.assertEqual(self.result_for(channel_contribution_aud=0).reason, "CHANNEL_ECONOMICS_NOT_POSITIVE")

    def test_input_not_mutated(self):
        original = copy.deepcopy(BASE)
        evaluate_channel_gate(BASE)
        self.assertEqual(BASE, original)


if __name__ == "__main__":
    unittest.main()
