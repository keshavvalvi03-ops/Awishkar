"""Unit tests for contract types, checklists, and suggestion engine."""

import unittest
from contract_types import (
    CONTRACT_TYPES,
    list_supported_contract_types,
    get_contract_type,
    suggest_contract_type,
    RELEVANCE_EXPECTED,
    RELEVANCE_CONDITIONAL,
    RELEVANCE_OPTIONAL,
    STATUS_DETECTED,
    STATUS_NOT_DETECTED,
    STATUS_UNCERTAIN,
)


class TestContractTypes(unittest.TestCase):

    def test_all_10_contract_types_present(self):
        types = list_supported_contract_types()
        self.assertEqual(len(types), 10)
        expected_types = [
            "Service Agreement",
            "Employment Agreement",
            "NDA / Confidentiality Agreement",
            "Software / IT Agreement",
            "Vendor / Supply Agreement",
            "Lease / Rental Agreement",
            "Licensing Agreement",
            "Partnership Agreement",
            "Merger / Acquisition Agreement",
            "General Business Agreement",
        ]
        for et in expected_types:
            self.assertIn(et, types)

    def test_checklist_structure_for_all_types(self):
        for ct_id, ct in CONTRACT_TYPES.items():
            self.assertTrue(len(ct.checklist) >= 5, f"Checklist for {ct.name} is too short")
            has_expected = False
            for item in ct.checklist:
                self.assertIn(item.relevance, [RELEVANCE_EXPECTED, RELEVANCE_CONDITIONAL, RELEVANCE_OPTIONAL])
                self.assertTrue(bool(item.reason), f"Reason missing for {item.clause_name} in {ct.name}")
                self.assertTrue(bool(item.recommended_action), f"Action missing for {item.clause_name} in {ct.name}")
                if item.relevance == RELEVANCE_EXPECTED:
                    has_expected = True
            self.assertTrue(has_expected, f"No Expected clauses in {ct.name}")

    def test_get_contract_type_by_alias_and_id(self):
        self.assertIsNotNone(get_contract_type("service_agreement"))
        self.assertIsNotNone(get_contract_type("Service Agreement"))
        self.assertIsNotNone(get_contract_type("msa"))
        self.assertIsNotNone(get_contract_type("NDA"))
        self.assertIsNotNone(get_contract_type("saas agreement"))
        self.assertIsNotNone(get_contract_type("commercial lease"))
        self.assertIsNone(get_contract_type("nonexistent_contract_type_xyz"))

    def test_suggest_contract_type_confident(self):
        nda_text = "MUTUAL NON-DISCLOSURE AGREEMENT\nThis Agreement protects confidential information..."
        s = suggest_contract_type(nda_text)
        self.assertEqual(s["primary_suggestion"], "NDA / Confidentiality Agreement")
        self.assertFalse(s["is_uncertain"])
        self.assertGreater(s["confidence"], 0.5)

    def test_suggest_contract_type_employment(self):
        emp_text = "EXECUTIVE EMPLOYMENT AGREEMENT\nEmployee shall receive base salary and duties..."
        s = suggest_contract_type(emp_text)
        self.assertEqual(s["primary_suggestion"], "Employment Agreement")
        self.assertFalse(s["is_uncertain"])

    def test_suggest_contract_type_uncertain_handling(self):
        # Ambiguous contract text with minimal signals
        vague_text = "AGREEMENT\nThe parties agree to work together on stuff."
        s = suggest_contract_type(vague_text)
        self.assertTrue(s["is_uncertain"])
        self.assertIn("General Business Agreement", s["primary_suggestion"])

    def test_suggest_contract_type_empty(self):
        s = suggest_contract_type("")
        self.assertTrue(s["is_uncertain"])
        self.assertIsNone(s["primary_suggestion"])


if __name__ == "__main__":
    unittest.main()
