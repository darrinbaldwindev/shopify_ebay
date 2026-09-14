import unittest

from src.sync_contract import accept_once, inventory_change, order_handoff, tracking_update


class SyncContractTests(unittest.TestCase):
    def test_inventory_change_is_shopify_canonical_and_no_network(self):
        result = inventory_change({
            "event_id": "inv-1",
            "shopify_variant_id": "gid://shopify/ProductVariant/100",
            "sku": "SKU-100",
            "inventory_quantity": 7,
        })
        self.assertTrue(result["accepted"])
        self.assertEqual(result["candidate"]["source"], "SHOPIFY")
        self.assertFalse(result["receipt"]["publication_authority"])
        self.assertFalse(result["receipt"]["network_io"])

    def test_order_handoff_preserves_shopify_order_authority(self):
        result = order_handoff({
            "event_id": "ord-1",
            "ebay_order_id": "EBAY-ORDER-1",
            "sku": "SKU-100",
            "quantity": 2,
        })
        self.assertTrue(result["accepted"])
        self.assertEqual(result["shopify_order_candidate"]["canonical_order_authority"], "SHOPIFY")
        self.assertFalse(result["receipt"]["publication_authority"])

    def test_tracking_requires_exact_order_correlation(self):
        result = tracking_update({
            "event_id": "track-1",
            "shopify_order_id": "",
            "ebay_order_id": "EBAY-ORDER-1",
            "tracking_number": "TRACK-1",
        })
        self.assertFalse(result["accepted"])
        self.assertEqual(result["reason"], "MISSING_TRACKING_CORRELATION")
        self.assertFalse(result["receipt"]["network_io"])

    def test_duplicate_event_fails_closed(self):
        event = {"event_id": "evt-1", "sku": "SKU-100"}
        first = accept_once(event, frozenset())
        duplicate = accept_once(event, frozenset({"evt-1"}))
        self.assertTrue(first["accepted"])
        self.assertFalse(duplicate["accepted"])
        self.assertEqual(duplicate["reason"], "DUPLICATE_EVENT")
        self.assertEqual(first["receipt"]["input_hash"], duplicate["receipt"]["input_hash"])


if __name__ == "__main__":
    unittest.main()
