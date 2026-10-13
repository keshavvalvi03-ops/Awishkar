"""Unit tests for clause taxonomy, extended categories, and alias normalization."""

import unittest
from risk_taxonomy import RISK_TAXONOMY
from custom_taxonomy import (
    CUSTOM_TAXONOMY,
    EXTENDED_TAXONOMY,
    normalize_category_name,
    get_category_info,
    is_provisional_category,
)


class TestTaxonomy(unittest.TestCase):

    def test_original_cuad_categories_preserved(self):
        # All original CUAD categories in risk_taxonomy must exist in EXTENDED_TAXONOMY
        for cat in RISK_TAXONOMY.keys():
            self.assertIn(cat, EXTENDED_TAXONOMY)
            info = get_category_info(cat)
            self.assertIsNotNone(info)
            self.assertEqual(info["base_severity"], RISK_TAXONOMY[cat]["base_severity"])

    def test_extended_categories_present(self):
        required_custom_cats = [
            "Indemnity",
            "Scope of Services",
            "Payment Terms",
            "Late Fees",
            "Termination For Cause",
            "Governing Law",
            "Dispute Resolution",
            "Confidentiality",
            "Warranties",
            "Force Majeure",
            "Data Privacy",
            "Data Protection and Security",
            "Entire Agreement",
            "Notice Requirements",
            "Assignment",
            "Non-Solicitation",
            "IP Ownership Assignment",  # Reused from CUAD without duplicate
            "Licence Restrictions",
            "Royalties",
            "Licence Fees",
            "Support and Maintenance",
            "Service Levels",
            "Delivery and Acceptance",
            "Rent",
            "Security Deposit",
            "Property Maintenance",
            "Landlord and Tenant Obligations",
            "Lease Termination",
            "Salary and Compensation",
            "Benefits",
            "Working Conditions",
            "Employment Termination",
            "Capital Contributions",
            "Profit and Loss Sharing",
            "Partner Responsibilities",
            "Partner Exit and Dissolution",
            "Representations and Warranties",
            "Purchase Price",
            "Closing Conditions",
            "Post-Closing Obligations",
            "Product Specifications and Quality",
            "Inspection and Acceptance",
            "Delivery Obligations",
            "Remedies for Non-Performance",
        ]
        for cat in required_custom_cats:
            self.assertIn(cat, EXTENDED_TAXONOMY, f"Missing category: {cat}")
            info = get_category_info(cat)
            self.assertIsNotNone(info, f"get_category_info failed for {cat}")
            self.assertIn("risk_type", info)
            self.assertIn("base_severity", info)

    def test_alias_normalization(self):
        test_cases = [
            ("INDEMNIFICATION", "Indemnity"),
            ("indemnity", "Indemnity"),
            ("hold harmless", "Indemnity"),
            ("limitation of liability", "Cap On Liability"),
            ("liability cap", "Cap On Liability"),
            ("cap on liability", "Cap On Liability"),
            ("uncapped liability", "Uncapped Liability"),
            ("UNLIMITED LIABILITY", "Uncapped Liability"),
            ("licence grant", "License Grant"),
            ("license grant", "License Grant"),
            ("ip ownership", "IP Ownership Assignment"),
            ("ip assignment", "IP Ownership Assignment"),
            ("intellectual property ownership", "IP Ownership Assignment"),
            ("non-disclosure", "Confidentiality"),
            ("nda", "Confidentiality"),
            ("governing law", "Governing Law"),
            ("choice of law", "Governing Law"),
            ("dispute resolution", "Dispute Resolution"),
            ("arbitration", "Dispute Resolution"),
            ("salary", "Salary and Compensation"),
            ("sla", "Service Levels"),
            ("security deposit", "Security Deposit"),
            ("reps and warranties", "Representations and Warranties"),
        ]
        for raw, expected in test_cases:
            normalized = normalize_category_name(raw)
            self.assertEqual(normalized, expected, f"Failed normalizing '{raw}': got '{normalized}', expected '{expected}'")

    def test_provisional_severity_flagging(self):
        # CUAD verified categories are not provisional
        self.assertFalse(is_provisional_category("Uncapped Liability"))
        self.assertFalse(is_provisional_category("Non-Compete"))
        # Custom provisional categories must be marked as provisional
        self.assertTrue(is_provisional_category("Indemnity"))
        self.assertTrue(is_provisional_category("Scope of Services"))
        self.assertTrue(is_provisional_category("Rent"))


if __name__ == "__main__":
    unittest.main()
