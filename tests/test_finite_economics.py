import unittest

from src.candidate_mapper import map_candidate
from test_channel_gate import BASE


class FiniteEconomicsTests(unittest.TestCase):
    def test_nonfinite_economics_never_produces_mapping_candidate(self):
        for field, reason in (("price_aud", "PRICE_INVALID"),
                              ("channel_contribution_aud", "CHANNEL_ECONOMICS_NOT_POSITIVE")):
            for value in (float("nan"), float("inf"), float("-inf")):
                with self.subTest(field=field, value=value):
                    result = map_candidate(dict(BASE, **{field: value}))
                    self.assertIsNone(result["candidate"])
                    self.assertFalse(result["receipt"]["gate"]["eligible"])
                    self.assertEqual(result["receipt"]["gate"]["reason"], reason)
                    self.assertFalse(result["receipt"]["publication_authority"])

    def test_finite_positive_economics_remains_mapping_only(self):
        for value in (1, 0.01, 1e300, 10 ** 400):
            with self.subTest(value=value):
                result = map_candidate(dict(BASE, price_aud=value, channel_contribution_aud=value))
                self.assertIsNotNone(result["candidate"])
                self.assertFalse(result["candidate"]["publication_authority"])

