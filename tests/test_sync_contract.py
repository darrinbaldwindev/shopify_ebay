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
        self.assertFalse(result["receipt"]["production_mutation"])
        self.assertFalse(result["receipt"]["network_io"])
        self.assertEqual(result["receipt"]["canonical_commercial_authority"], "SHOPIFY")

    def test_stale_inventory_event_fails_closed(self):
        event = {
            "event_id": "inv-stale",
            "shopify_variant_id": "gid://shopify/ProductVariant/100",
            "sku": "SKU-100",
            "inventory_quantity": 5,
            "inventory_revision": 41,
        }
        result = inventory_change(event, latest_revision=41)
        self.assertFalse(result["accepted"])
        self.assertEqual(result["reason"], "STALE_INVENTORY_EVENT")
        self.assertFalse(result["receipt"]["publication_authority"])

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

    def test_duplicate_order_import_fails_closed(self):
        event = {
            "event_id": "ord-replay",
            "ebay_order_id": "EBAY-ORDER-REPLAY",
            "sku": "SKU-100",
            "quantity": 1,
        }
        result = order_handoff(event, frozenset({"EBAY-ORDER-REPLAY"}))
        self.assertFalse(result["accepted"])
        self.assertEqual(result["reason"], "DUPLICATE_ORDER_IMPORT")
        self.assertFalse(result["receipt"]["network_io"])

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

    def test_tracking_correlation_mismatch_fails_closed(self):
        event = {
            "event_id": "track-mismatch",
            "shopify_order_id": "SHOPIFY-ORDER-2",
            "ebay_order_id": "EBAY-ORDER-1",
            "tracking_number": "TRACK-1",
        }
        result = tracking_update(event, expected_correlation=("SHOPIFY-ORDER-1", "EBAY-ORDER-1"))
        self.assertFalse(result["accepted"])
        self.assertEqual(result["reason"], "TRACKING_CORRELATION_MISMATCH")

    def test_out_of_order_tracking_event_fails_closed(self):
        event = {
            "event_id": "track-stale",
            "shopify_order_id": "SHOPIFY-ORDER-1",
            "ebay_order_id": "EBAY-ORDER-1",
            "tracking_number": "TRACK-OLD",
            "tracking_sequence": 8,
        }
        result = tracking_update(event, latest_sequence=9)
        self.assertFalse(result["accepted"])
        self.assertEqual(result["reason"], "OUT_OF_ORDER_TRACKING_EVENT")
        self.assertFalse(result["receipt"]["publication_authority"])

    def test_duplicate_event_fails_closed_with_stable_receipt(self):
        event = {"event_id": "evt-1", "sku": "SKU-100"}
        first = accept_once(event, frozenset())
        duplicate = accept_once(event, frozenset({"evt-1"}), {"evt-1": first["receipt"]["input_hash"]})
        self.assertTrue(first["accepted"])
        self.assertFalse(duplicate["accepted"])
        self.assertEqual(duplicate["reason"], "DUPLICATE_EVENT")
        self.assertEqual(first["receipt"]["input_hash"], duplicate["receipt"]["input_hash"])

    def test_reused_event_id_with_changed_payload_fails_as_conflict(self):
        original = {"event_id": "evt-conflict", "sku": "SKU-100", "quantity": 1}
        first = accept_once(original, frozenset())
        changed = {"event_id": "evt-conflict", "sku": "SKU-100", "quantity": 2}
        replay = accept_once(
            changed,
            frozenset({"evt-conflict"}),
            {"evt-conflict": first["receipt"]["input_hash"]},
        )
        self.assertFalse(replay["accepted"])
        self.assertEqual(replay["reason"], "EVENT_ID_PAYLOAD_CONFLICT")
        self.assertNotEqual(first["receipt"]["input_hash"], replay["receipt"]["input_hash"])
        self.assertFalse(replay["receipt"]["publication_authority"])
        self.assertFalse(replay["receipt"]["production_mutation"])
        self.assertFalse(replay["receipt"]["network_io"])

    def test_event_id_whitespace_cannot_bypass_replay_identity(self):
        event = {"event_id": " evt-1 ", "sku": "SKU-100"}
        result = accept_once(event, frozenset({"evt-1"}))
        self.assertFalse(result["accepted"])
        self.assertEqual(result["reason"], "NON_CANONICAL_EVENT_ID")
        self.assertFalse(result["receipt"]["publication_authority"])
        self.assertFalse(result["receipt"]["production_mutation"])
        self.assertFalse(result["receipt"]["network_io"])


if __name__ == "__main__":
    unittest.main()
