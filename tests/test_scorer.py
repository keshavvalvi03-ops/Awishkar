"""Unit tests for Layer 3 Risk Scoring Engine."""

import unittest
from risk_scorer import score_clause, score_contract, ScoredClause


class TestScorer(unittest.TestCase):

    def test_score_clause_normal(self):
        # Base severity 9 + unlimited (2) + without limitation (2) = raw 13
        # 0.9 * 13 + 0.1 * 5 = 11.7 + 0.5 = 12.2 -> clamped to 10
        c = score_clause("Uncapped Liability", "Liability is unlimited and without limitation.", 0.9)
        self.assertEqual(c.category, "Uncapped Liability")
        self.assertEqual(c.final_score, 10)
        self.assertEqual(c.risk_level, "High")

    def test_confidence_none_handling(self):
        # Bug fix: confidence=None must not raise TypeError
        c = score_clause("Cap On Liability", "Liability capped at $1000", confidence=None)
        self.assertIsNotNone(c)
        self.assertEqual(c.confidence, 1.0)
        self.assertEqual(c.final_score, 3.0)

    def test_zero_confidence_handling(self):
        # When confidence is 0.0, score pulls completely to neutral 5.0
        c = score_clause("Uncapped Liability", "Liability is unlimited", confidence=0.0)
        self.assertEqual(c.final_score, 5.0)

    def test_empty_and_none_text_handling(self):
        # Bug fix: None text must not raise AttributeError on lower()
        c_none = score_clause("Non-Compete", None, 0.8)
        self.assertEqual(c_none.clause_text, "")
        self.assertEqual(c_none.category, "Non-Compete")

        c_empty = score_clause("Non-Compete", "", 0.8)
        self.assertEqual(c_empty.clause_text, "")

    def test_unknown_and_informational_categories(self):
        # Informational CUAD categories like Parties
        c_parties = score_clause("Parties", "Between ABC Corp and XYZ Ltd", 0.95)
        self.assertEqual(c_parties.risk_level, "Not Applicable")
        self.assertEqual(c_parties.final_score, 0)

        # Unrecognized category name
        c_unknown = score_clause("CompletelyUnknownCategory123", "Some text", 0.8)
        self.assertEqual(c_unknown.risk_level, "Not Applicable")
        self.assertEqual(c_unknown.final_score, 0)

    def test_alias_handling_in_scorer(self):
        # Lowercase alias should normalize and score
        c = score_clause("indemnification", "Vendor shall indemnify client.", 0.9)
        self.assertEqual(c.category, "Indemnity")
        self.assertEqual(c.risk_type, "Financial Risk")
        self.assertGreater(c.final_score, 0)

    def test_word_boundary_modifier_avoiding_false_positives(self):
        # "exceptional" should NOT trigger modifier "except" (-1)
        text_exceptional = "The vendor provides exceptional service at all times."
        c1 = score_clause("Scope of Services", text_exceptional, 1.0)
        self.assertNotIn("except", c1.matched_keywords)

        # Real "except" should trigger modifier
        text_except = "All services are included except for hardware maintenance."
        c2 = score_clause("Scope of Services", text_except, 1.0)
        self.assertIn("except", c2.matched_keywords)

    def test_score_contract_empty_and_malformed(self):
        self.assertEqual(score_contract([]), [])
        self.assertEqual(score_contract(None), [])

        # Extractions with missing fields
        extractions = [
            {"category": "Cap On Liability"},
            {"category": "Parties", "text": None, "confidence": None},
            "malformed_string_entry",  # invalid entry
        ]
        results = score_contract(extractions)
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].category, "Cap On Liability")


if __name__ == "__main__":
    unittest.main()
