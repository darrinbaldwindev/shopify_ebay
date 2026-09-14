import copy
import unittest

from src.candidate_mapper import map_candidate


BASE = {
    "shopify_product_id": "gid://shopify/Product/100",
    "shopify_variant_id": "gid://shopify/ProductVariant/200",
    "sku": "SYNTH-001",
    "title": "Synthetic compact organiser",
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


class CandidateMapperTests(unittest.TestCase):
    def test_eligible_input_maps_without_publication_authority(self):
        result = map_candidate(BASE)
        self.assertEqual(result["candidate"]["source"], "SHOPIFY")
        self.assertFalse(result["candidate"]["publication_authority"])
        self.assertFalse(result["receipt"]["publication_authority"])
        self.assertEqual(result["receipt"]["gate"]["reason"], "ELIGIBLE_FOR_MAPPING_ONLY")

    def test_unknown_channel_fields_remain_explicit_unknown(self):
        result = map_candidate(BASE)
        self.assertEqual(result["candidate"]["ebay_category_id"], "UNKNOWN")
        self.assertEqual(result["candidate"]["gtin"], "UNKNOWN")
        self.assertEqual(result["candidate"]["condition"], "UNKNOWN")
        self.assertEqual(result["candidate"]["inventory_quantity"], "UNKNOWN")

    def test_denied_input_produces_receipt_but_no_candidate(self):
        denied = copy.deepcopy(BASE)
        denied["marketplace_permission"] = "PERMISSION-REQUIRED"
        result = map_candidate(denied)
        self.assertIsNone(result["candidate"])
        self.assertFalse(result["receipt"]["gate"]["eligible"])
        self.assertEqual(result["receipt"]["gate"]["reason"], "MARKETPLACE_PERMISSION_NOT_ELIGIBLE")

    def test_unknown_commercial_evidence_produces_no_candidate(self):
        for field in ("supplier_trade_cost_known", "freight_landed_cost_known", "marketplace_plan_fee_known", "category_fee_known", "inventory_evidence_fresh"):
            denied = copy.deepcopy(BASE)
            denied[field] = False
            with self.subTest(field=field):
                self.assertIsNone(map_candidate(denied)["candidate"])

    def test_receipt_is_deterministic_for_equivalent_input_ordering(self):
        reversed_items = dict(reversed(list(BASE.items())))
        first = map_candidate(BASE)
        second = map_candidate(reversed_items)
        self.assertEqual(first["receipt"]["input_hash"], second["receipt"]["input_hash"])
        self.assertEqual(first, second)

    def test_receipt_binds_shopify_identity_and_mapper_version(self):
        result = map_candidate(BASE)
        receipt = result["receipt"]
        self.assertEqual(receipt["shopify_product_id"], BASE["shopify_product_id"])
        self.assertEqual(receipt["shopify_variant_id"], BASE["shopify_variant_id"])
        self.assertEqual(receipt["sku"], BASE["sku"])
        self.assertEqual(receipt["mapper_version"], "v0.1")
        self.assertEqual(len(receipt["input_hash"]), 64)

    def test_mapper_does_not_mutate_input(self):
        original = copy.deepcopy(BASE)
        map_candidate(BASE)
        self.assertEqual(BASE, original)


if __name__ == "__main__":
    unittest.main()
