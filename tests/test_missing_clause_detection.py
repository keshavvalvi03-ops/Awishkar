"""Unit tests for Layer 5 Missing Clause Detection."""

import unittest
from missing_clause_detection import (
    detect_missing_clauses,
    evaluate_contract_checklist,
    STATUS_DETECTED,
    STATUS_NOT_DETECTED,
    STATUS_UNCERTAIN,
    RELEVANCE_EXPECTED,
    RELEVANCE_CONDITIONAL,
)


class TestMissingClauseDetection(unittest.TestCase):

    def test_backward_compatibility_mode(self):
        # When contract_type is None, runs default general commercial missing clause checks
        extractions = [
            {"category": "Cap On Liability", "text": "Cap is $1000", "confidence": 0.8},
            {"category": "Termination For Convenience", "text": "May terminate", "confidence": 0.8},
        ]
        raw_text = "This agreement includes confidentiality obligations."
        findings = detect_missing_clauses(extractions, raw_text, contract_type=None)

        self.assertTrue(len(findings) > 0)
        clause_names = [f["clause_name"] for f in findings]

        # Present categories should NOT be reported as missing
        self.assertNotIn("Cap On Liability", clause_names)
        self.assertNotIn("Termination For Convenience", clause_names)
        self.assertNotIn("Confidentiality", clause_names)

        # Absent categories must be reported
        self.assertIn("Governing Law", clause_names)
        self.assertIn("Warranty Duration", clause_names)
        self.assertIn("Insurance", clause_names)
        self.assertIn("Dispute Resolution", clause_names)

        # Check required dictionary fields for backward compatibility
        for f in findings:
            self.assertIn("clause_name", f)
            self.assertIn("detection_method", f)
            self.assertIn("message", f)

    def test_contract_specific_checklist_service_agreement(self):
        extractions = [
            {"category": "Scope of Services", "text": "Consulting tasks", "confidence": 0.9},
            {"category": "Payment Terms", "text": "Net 30 days", "confidence": 0.85},
            {"category": "Cap On Liability", "text": "Capped at fees paid", "confidence": 0.40},  # Low confidence
        ]
        raw_text = "This agreement is governed by the laws of Delaware. Either party may terminate for material breach."

        checklist = evaluate_contract_checklist("Service Agreement", extractions, raw_text)
        self.assertTrue(len(checklist) >= 10)

        item_map = {item["clause_name"]: item for item in checklist}

        # Scope of Services -> Detected via extraction
        self.assertEqual(item_map["Scope of Services"]["status"], STATUS_DETECTED)

        # Cap On Liability has confidence 0.40 (< 0.50) -> Uncertain
        self.assertEqual(item_map["Cap On Liability"]["status"], STATUS_UNCERTAIN)

        # Governing Law -> Detected via raw text pattern
        self.assertEqual(item_map["Governing Law"]["status"], STATUS_DETECTED)

        # Indemnity not present in text or extractions -> Not detected
        self.assertEqual(item_map["Indemnity"]["status"], STATUS_NOT_DETECTED)

    def test_contract_specific_missing_clauses_filtered(self):
        extractions = [
            {"category": "Confidentiality", "text": "Protects secret info", "confidence": 0.95},
            {"category": "Governing Law", "text": "Laws of New York", "confidence": 0.95},
        ]
        # In NDA, Warranty Duration is NOT on the checklist and shouldn't be flagged
        findings = detect_missing_clauses(extractions, raw_contract_text="", contract_type="NDA")
        missing_names = [f["clause_name"] for f in findings]

        self.assertNotIn("Warranty Duration", missing_names)
        self.assertNotIn("Insurance", missing_names)
        self.assertNotIn("Confidentiality", missing_names)
        self.assertNotIn("Governing Law", missing_names)


if __name__ == "__main__":
    unittest.main()
