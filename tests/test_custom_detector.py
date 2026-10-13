"""Unit tests for custom regex detector and pattern matching."""

import unittest
from custom_detector import detect_clause_in_text, scan_all_clauses


class TestCustomDetector(unittest.TestCase):

    def test_positive_clause_detection(self):
        text = "Supplier shall defend and indemnify Buyer against any patent infringement claims."
        res = detect_clause_in_text("Indemnity", text)
        self.assertIsNotNone(res)
        self.assertEqual(res["category"], "Indemnity")
        self.assertEqual(res["detection_method"], "experimental_keyword")
        self.assertIsNone(res["confidence"])  # Must not invent fake confidence scores
        self.assertTrue(res["is_heuristic"])
        self.assertIn("indemnify", res["text"].lower())

    def test_governing_law_detection(self):
        text = "This contract shall be governed by and construed in accordance with the laws of New York."
        res = detect_clause_in_text("Governing Law", text)
        self.assertIsNotNone(res)
        self.assertEqual(res["category"], "Governing Law")
        self.assertIn("governed by", res["text"].lower())

    def test_force_majeure_detection(self):
        text = "Neither party is liable for failure caused by force majeure or acts of God."
        res = detect_clause_in_text("Force Majeure", text)
        self.assertIsNotNone(res)
        self.assertEqual(res["category"], "Force Majeure")

    def test_negative_matching_word_boundary_preventing_false_positives(self):
        # Text with irrelevant words should NOT trigger
        text = "The company had an exceptional year with high expectations."
        res = detect_clause_in_text("Rent", text)
        self.assertIsNone(res)

        res_indemnity = detect_clause_in_text("Indemnity", text)
        self.assertIsNone(res_indemnity)

    def test_scan_all_clauses(self):
        text = """
        1. PAYMENT TERMS: Invoices are payable net 30 days.
        2. CONFIDENTIALITY: Parties agree to protect proprietary information.
        3. DISPUTE RESOLUTION: Disputes shall be settled by binding arbitration.
        """
        results = scan_all_clauses(text)
        cats = {r["category"] for r in results}
        self.assertIn("Payment Terms", cats)
        self.assertIn("Confidentiality", cats)
        self.assertIn("Dispute Resolution", cats)

    def test_empty_and_none_text_handling(self):
        self.assertIsNone(detect_clause_in_text("Indemnity", ""))
        self.assertIsNone(detect_clause_in_text("Indemnity", None))
        self.assertEqual(scan_all_clauses(""), [])
        self.assertEqual(scan_all_clauses(None), [])


if __name__ == "__main__":
    unittest.main()
