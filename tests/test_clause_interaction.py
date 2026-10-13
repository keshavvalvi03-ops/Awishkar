"""Unit tests for Layer 6 Cross-Clause Interaction and Risk Aggregation."""

import unittest
from risk_scorer import ScoredClause
from clause_interaction import detect_interactions, aggregate_contract_risk


class TestClauseInteraction(unittest.TestCase):

    def test_empty_input_schema_completeness(self):
        # Bug fix: empty input must include all score fields to avoid KeyError
        res = aggregate_contract_risk([])
        self.assertIn("contract_score", res)
        self.assertIn("contract_level", res)
        self.assertIn("base_weighted_score", res)
        self.assertIn("interaction_bonus", res)
        self.assertIn("interactions", res)
        self.assertIn("average_confidence", res)
        self.assertIn("note", res)

        self.assertEqual(res["contract_score"], 0.0)
        self.assertEqual(res["contract_level"], "Low")
        self.assertEqual(res["base_weighted_score"], 0.0)
        self.assertEqual(res["interaction_bonus"], 0.0)

    def test_zero_confidence_avoids_division_by_zero(self):
        # Bug fix: all zero confidences must not raise ZeroDivisionError
        clause = ScoredClause(
            category="Cap On Liability",
            clause_text="Liability capped at $1000",
            confidence=0.0,
            risk_type="Financial Risk",
            base_severity=3.0,
            matched_keywords=[],
            keyword_bonus=0.0,
            raw_score=3.0,
            final_score=3.0,
            risk_level="Low",
        )
        res = aggregate_contract_risk([clause])
        self.assertEqual(res["contract_score"], 3.0)
        self.assertEqual(res["average_confidence"], 0.0)

    def test_exclusive_lock_in_requires_actual_auto_renewal(self):
        # Mutual agreement renewal: should NOT fire Exclusive Lock-In Trap
        mutual_renewal = ScoredClause(
            category="Renewal Term",
            clause_text="This agreement may be renewed upon mutual written agreement of both parties.",
            confidence=0.8,
            risk_type="Renewal Risk",
            base_severity=4.0,
            matched_keywords=[],
            keyword_bonus=0.0,
            raw_score=4.0,
            final_score=4.2,
            risk_level="Medium",
        )
        exclusivity = ScoredClause(
            category="Exclusivity",
            clause_text="Buyer agrees to purchase exclusively from Seller.",
            confidence=0.8,
            risk_type="Restrictive Covenant Risk",
            base_severity=6.0,
            matched_keywords=[],
            keyword_bonus=0.0,
            raw_score=6.0,
            final_score=5.8,
            risk_level="Medium",
        )
        interactions_mutual = detect_interactions([mutual_renewal, exclusivity])
        trap_names_mutual = [i.name for i in interactions_mutual]
        self.assertNotIn("Exclusive Lock-In Trap", trap_names_mutual)

        # Automatic renewal: MUST fire Exclusive Lock-In Trap
        auto_renewal = ScoredClause(
            category="Renewal Term",
            clause_text="This agreement shall automatically renew for successive one-year terms.",
            confidence=0.8,
            risk_type="Renewal Risk",
            base_severity=4.0,
            matched_keywords=["automatically renew"],
            keyword_bonus=1.0,
            raw_score=5.0,
            final_score=5.0,
            risk_level="Medium",
        )
        interactions_auto = detect_interactions([auto_renewal, exclusivity])
        trap_names_auto = [i.name for i in interactions_auto]
        self.assertIn("Exclusive Lock-In Trap", trap_names_auto)

    def test_uncapped_financial_exposure_interaction(self):
        uncapped = ScoredClause(
            category="Uncapped Liability",
            clause_text="Liability is unlimited without limitation.",
            confidence=0.9,
            risk_type="Financial Risk",
            base_severity=9.0,
            matched_keywords=["unlimited", "without limitation"],
            keyword_bonus=4.0,
            raw_score=13.0,
            final_score=10.0,
            risk_level="High",
        )
        # Without Cap on Liability or Insurance, fires +2.0
        interactions = detect_interactions([uncapped])
        names = [i.name for i in interactions]
        self.assertIn("Uncapped Financial Exposure", names)

    def test_abrupt_walkaway_interaction(self):
        term_convenience = ScoredClause(
            category="Termination For Convenience",
            clause_text="Either party may terminate at any time without cause.",
            confidence=0.9,
            risk_type="Termination Risk",
            base_severity=5.0,
            matched_keywords=[],
            keyword_bonus=0.0,
            raw_score=5.0,
            final_score=5.0,
            risk_level="Medium",
        )
        # Without Post-Termination Services, fires +1.0
        interactions = detect_interactions([term_convenience])
        names = [i.name for i in interactions]
        self.assertIn("Abrupt Walkaway Risk", names)


if __name__ == "__main__":
    unittest.main()
