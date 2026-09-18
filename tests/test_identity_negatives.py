import copy
import unittest

from src.candidate_mapper import map_candidate
from src.sync_contract import accept_once, inventory_change, order_handoff, tracking_update
from test_candidate_mapper import BASE


class IdentityNegatives(unittest.TestCase):
    def test_mapper_rejects_malformed_shopify_identity(self):
        for field, wrong_kind in (("shopify_product_id", "ProductVariant"), ("shopify_variant_id", "Product")):
            for value in (True, 123, [], {}, "gid://shopify/" + wrong_kind + "/100", "gid://shopify/ProductVariant/", "gid://shopify/ProductVariant/200?x=1", "gid://shopify/ProductVariant/0"):
                with self.subTest(field=field, value=value):
                    result = map_candidate(dict(BASE, **{field: value}))
                    self.assertIsNone(result["candidate"])
                    self.assertFalse(result["receipt"]["publication_authority"])

    def test_mapper_rejects_malformed_sku_without_normalizing_it(self):
        for value in (True, 42, [], {}, " SKU-1", "SKU-1 ", "SKU\x00-1", "SKU\n-1"):
            with self.subTest(value=value):
                result = map_candidate(dict(BASE, sku=value))
                self.assertIsNone(result["candidate"])
                self.assertEqual(result["receipt"]["sku"], value)

    def test_operation_identities_cannot_bypass_dedupe_validation(self):
        cases = [
            (inventory_change, {"event_id": "i", "shopify_variant_id": "gid://shopify/ProductVariant/1", "sku": "SKU", "inventory_quantity": 1}, ("event_id", "shopify_variant_id", "sku")),
            (order_handoff, {"event_id": "o", "ebay_order_id": "ORDER", "sku": "SKU", "quantity": 1}, ("event_id", "ebay_order_id", "sku")),
            (tracking_update, {"event_id": "t", "shopify_order_id": "SHOP", "ebay_order_id": "ORDER", "tracking_number": "TRACK"}, ("event_id", "shopify_order_id", "ebay_order_id", "tracking_number")),
        ]
        for fn, event, fields in cases:
            for field in fields:
                for value in (True, 42, [], {}, " value", "value ", "val\x00ue"):
                    with self.subTest(fn=fn.__name__, field=field, value=value):
                        result = fn(dict(event, **{field: value}))
                        self.assertFalse(result["accepted"])
                        self.assertFalse(result["receipt"]["network_io"])

    def test_inventory_revision_types_fail_closed_without_comparison_errors(self):
        event = {
            "event_id": "inventory-1",
            "shopify_variant_id": "gid://shopify/ProductVariant/1",
            "sku": "SKU-1",
            "inventory_quantity": 4,
            "inventory_revision": 2,
        }
        for latest in (True, -1, 1.0, "1", [], {}):
            with self.subTest(latest_revision=latest):
                result = inventory_change(event, latest_revision=latest)
                self.assertFalse(result["accepted"])
                self.assertEqual(result["reason"], "INVALID_LATEST_INVENTORY_REVISION")
                self.assertFalse(result["receipt"]["network_io"])
        for revision in (None, True, -1, 2.0, "2", [], {}):
            with self.subTest(inventory_revision=revision):
                malformed = dict(event, inventory_revision=revision)
                result = inventory_change(malformed, latest_revision=1)
                self.assertFalse(result["accepted"])
                self.assertEqual(result["reason"], "INVALID_INVENTORY_REVISION")
                self.assertFalse(result["receipt"]["publication_authority"])
        self.assertEqual(inventory_change(event, latest_revision=2)["reason"], "STALE_INVENTORY_EVENT")
        self.assertTrue(inventory_change(event, latest_revision=1)["accepted"])

    def test_conflicting_replay_evidence_never_becomes_first_acceptance(self):
        event = {"event_id": "original", "quantity": 1}
        first = accept_once(event, frozenset())
        hashes = {"original": first["receipt"]["input_hash"]}
        before = copy.deepcopy(hashes)
        changed = dict(event, quantity=2)
        result = accept_once(changed, frozenset(), hashes)
        self.assertFalse(result["accepted"])
        self.assertEqual(result["reason"], "INCONSISTENT_REPLAY_EVIDENCE")
        self.assertEqual(result["receipt"]["prior_input_hash"], before["original"])
        self.assertNotEqual(result["receipt"]["input_hash"], before["original"])
        self.assertEqual(hashes, before)

    def test_duplicate_preserves_first_input_hash_and_input_order_invariance(self):
        event = {"event_id": "original", "quantity": 1}
        first = accept_once(event, frozenset())
        hashes = {"original": first["receipt"]["input_hash"]}
        replay = accept_once(dict(reversed(list(event.items()))), frozenset(hashes), hashes)
        self.assertEqual(replay["reason"], "DUPLICATE_EVENT")
        self.assertEqual(replay["receipt"]["input_hash"], hashes["original"])
        conflict = accept_once(dict(event, quantity=2), frozenset(hashes), hashes)
        self.assertEqual(conflict["reason"], "EVENT_ID_PAYLOAD_CONFLICT")
        self.assertEqual(conflict["receipt"]["prior_input_hash"], hashes["original"])

    def test_control_character_event_id_fails_closed(self):
        self.assertFalse(accept_once({"event_id": "evt\x00id"}, frozenset())["accepted"])
