"""Unit tests for pipeline integration and original demo regression."""

import unittest
from pipeline import full_analysis, load_cuad_questions


class TestPipelineAndRegression(unittest.TestCase):

    def test_load_cuad_questions(self):
        questions = load_cuad_questions()
        self.assertGreaterEqual(len(questions), 41)
        self.assertIn("Governing Law", questions)
        self.assertIn("Uncapped Liability", questions)
        self.assertIn("Cap On Liability", questions)

    def test_full_analysis_backward_compatibility_keys(self):
        extractions = [
            {"category": "Cap On Liability", "text": "Capped at $1000", "confidence": 0.8}
        ]
        report = full_analysis(extractions)

        # 3 required original keys
        self.assertIn("clauses", report)
        self.assertIn("missing_clauses", report)
        self.assertIn("contract_risk", report)

        # Extended keys
        self.assertIn("contract_type", report)
        self.assertIn("contract_checklist", report)

    def test_full_analysis_empty_inputs(self):
        report = full_analysis([], None)
        self.assertEqual(report["clauses"], [])
        self.assertEqual(report["contract_risk"]["contract_score"], 0.0)
        self.assertEqual(report["contract_risk"]["contract_level"], "Low")

    def test_original_demo_baseline_regression_score(self):
        """
        REGRESSION TEST:
        Must reproduce the baseline score of 8.16 / 10 (High)
        using the exact sample inputs from demo.py.
        """
        sample_extractions = [
            {
                "category": "Uncapped Liability",
                "text": "Vendor's liability under this Agreement shall be unlimited "
                        "and without limitation for breaches of confidentiality.",
                "confidence": 0.91,
            },
            {
                "category": "Cap On Liability",
                "text": "In no event shall either party's liability exceed the fees "
                        "paid in the preceding 12 months.",
                "confidence": 0.62,
            },
            {
                "category": "Non-Compete",
                "text": "Client shall not engage any competing service provider for "
                        "a period of 24 months following termination.",
                "confidence": 0.78,
            },
            {
                "category": "Renewal Term",
                "text": "This Agreement shall automatically renew for successive "
                        "one-year terms unless either party provides 30 days notice.",
                "confidence": 0.55,
            },
            {
                "category": "Termination For Convenience",
                "text": "Either party may terminate this Agreement at any time and "
                        "without notice for its sole discretion.",
                "confidence": 0.88,
            },
            {
                "category": "Parties",
                "text": "This Agreement is entered into between ABC Corp and XYZ Ltd.",
                "confidence": 0.95,
            },
        ]

        sample_raw_contract_text = """
        This Agreement is entered into between ABC Corp and XYZ Ltd.
        Vendor's liability under this Agreement shall be unlimited and without
        limitation for breaches of confidentiality. In no event shall either
        party's liability exceed the fees paid in the preceding 12 months.
        Client shall not engage any competing service provider for a period of
        24 months following termination. This Agreement shall automatically
        renew for successive one-year terms unless either party provides 30
        days notice. Either party may terminate this Agreement at any time and
        without notice for its sole discretion.
        """

        report = full_analysis(sample_extractions, sample_raw_contract_text)

        # 1. Verify contract risk matches original baseline
        cr = report["contract_risk"]
        self.assertEqual(cr["contract_score"], 8.16, "Contract score diverged from baseline 8.16!")
        self.assertEqual(cr["contract_level"], "High")
        self.assertEqual(cr["base_weighted_score"], 7.16)
        self.assertEqual(cr["interaction_bonus"], 1.0)
        self.assertEqual(cr["average_confidence"], 0.75)

        # 2. Verify triggered interaction is exactly Abrupt Walkaway Risk (+1.0)
        self.assertEqual(len(cr["interactions"]), 1)
        self.assertEqual(cr["interactions"][0]["name"], "Abrupt Walkaway Risk")
        self.assertEqual(cr["interactions"][0]["bonus"], 1.0)

        # 3. Verify per-clause scores match original demo
        clause_map = {c["category"]: c for c in report["clauses"]}
        self.assertEqual(clause_map["Uncapped Liability"]["score"], 10)
        self.assertEqual(clause_map["Uncapped Liability"]["risk_level"], "High")

        self.assertEqual(clause_map["Cap On Liability"]["score"], 3.76)
        self.assertEqual(clause_map["Cap On Liability"]["risk_level"], "Low")

        self.assertEqual(clause_map["Non-Compete"]["score"], 6.56)
        self.assertEqual(clause_map["Non-Compete"]["risk_level"], "Medium")

        self.assertEqual(clause_map["Renewal Term"]["score"], 5.0)
        self.assertEqual(clause_map["Renewal Term"]["risk_level"], "Medium")

        self.assertEqual(clause_map["Termination For Convenience"]["score"], 8.52)
        self.assertEqual(clause_map["Termination For Convenience"]["risk_level"], "High")

        self.assertEqual(clause_map["Parties"]["score"], 0)
        self.assertEqual(clause_map["Parties"]["risk_level"], "Not Applicable")

        # 4. Verify exactly 8 missing clauses in demo backward compatibility mode
        self.assertEqual(len(report["missing_clauses"]), 8)


if __name__ == "__main__":
    unittest.main()
