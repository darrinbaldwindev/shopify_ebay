import ast
from pathlib import Path
import unittest
from unittest import mock

from src.candidate_mapper import map_candidate
from src.sync_contract import inventory_change, order_handoff, tracking_update


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


class ZeroNetworkBoundaryTests(unittest.TestCase):
    def test_fixture_modules_have_no_network_or_marketplace_sdk_imports(self):
        forbidden_roots = {"requests", "httpx", "urllib", "socket", "ebaysdk", "shopify"}
        for path in Path("src").glob("*.py"):
            tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
            imported = set()
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    imported.update(alias.name.split(".")[0] for alias in node.names)
                elif isinstance(node, ast.ImportFrom) and node.module:
                    imported.add(node.module.split(".")[0])
            with self.subTest(path=str(path)):
                self.assertFalse(imported & forbidden_roots, f"forbidden external/network import: {imported & forbidden_roots}")

    @mock.patch("socket.create_connection", side_effect=AssertionError("network forbidden"))
    def test_candidate_mapping_is_zero_network(self, _network):
        result = map_candidate(BASE)
        self.assertIsNotNone(result["candidate"])
        self.assertFalse(result["receipt"]["publication_authority"])

    @mock.patch("socket.create_connection", side_effect=AssertionError("network forbidden"))
    def test_sync_contracts_are_zero_network_and_non_publishing(self, _network):
        results = [
            inventory_change({"event_id": "i-1", "shopify_variant_id": "gid://shopify/ProductVariant/200", "sku": "SYNTH-001", "inventory_quantity": 2}),
            order_handoff({"event_id": "o-1", "ebay_order_id": "EBAY-SYNTH-1", "sku": "SYNTH-001", "quantity": 1}),
            tracking_update({"event_id": "t-1", "shopify_order_id": "SHOP-SYNTH-1", "ebay_order_id": "EBAY-SYNTH-1", "tracking_number": "TRACK-SYNTH-1"}),
        ]
        for result in results:
            with self.subTest(kind=result["receipt"]["kind"]):
                self.assertTrue(result["accepted"])
                self.assertFalse(result["receipt"]["network_io"])
                self.assertFalse(result["receipt"]["publication_authority"])


if __name__ == "__main__":
    unittest.main()
