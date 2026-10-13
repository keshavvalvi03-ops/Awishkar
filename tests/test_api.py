"""Unit tests for FastAPI Web Backend Endpoints."""

import unittest
from fastapi.testclient import TestClient
from app import app
from demo import sample_extractions, sample_raw_contract_text


class TestAPIEndpoints(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = TestClient(app)

    def test_health_check(self):
        resp = self.client.get("/api/health")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["status"], "healthy")
        self.assertEqual(data["supported_contract_types"], 10)

    def test_contract_types_endpoint(self):
        resp = self.client.get("/api/contract-types")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["count"], 10)
        self.assertEqual(len(data["contract_types"]), 10)
        type_names = [t["name"] for t in data["contract_types"]]
        self.assertIn("Service Agreement", type_names)
        self.assertIn("NDA / Confidentiality Agreement", type_names)

    def test_suggest_type_endpoint(self):
        resp = self.client.post(
            "/api/suggest-type",
            json={"text": "EMPLOYMENT AGREEMENT\nBetween Employer and Employee for salary and duties."}
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["primary_suggestion"], "Employment Agreement")

    def test_suggest_type_empty_error(self):
        resp = self.client.post("/api/suggest-type", json={"text": ""})
        self.assertEqual(resp.status_code, 400)

    def test_samples_endpoint(self):
        resp = self.client.get("/api/samples")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("samples", data)
        self.assertIn("Baseline Demo (Original PoC)", data["samples"])
        self.assertIn("Service Agreement", data["samples"])

    def test_analyze_endpoint_normal_text(self):
        text = """
        SERVICES AGREEMENT
        1. SCOPE: Provider will perform web development services.
        2. PAYMENT: Fees payable net 30 days upon invoice.
        3. LIABILITY: Liability is capped at $5000.
        4. GOVERNING LAW: Laws of Delaware.
        """
        resp = self.client.post(
            "/api/analyze",
            json={"text": text, "contract_type": "Service Agreement"}
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("contract_risk", data)
        self.assertIn("clauses", data)
        self.assertIn("contract_checklist", data)
        self.assertIn("summary", data)
        self.assertGreater(data["summary"]["risk_bearing_clauses"], 0)

    def test_analyze_endpoint_baseline_demo_regression(self):
        # Sends the exact baseline demo inputs through the API
        resp = self.client.post(
            "/api/analyze",
            json={
                "text": sample_raw_contract_text,
                "extractions": sample_extractions,
                "contract_type": None,
                "is_sample": True,
            }
        )
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["contract_risk"]["contract_score"], 8.16)
        self.assertEqual(data["contract_risk"]["contract_level"], "High")
        self.assertEqual(data["contract_risk"]["base_weighted_score"], 7.16)
        self.assertEqual(data["contract_risk"]["interaction_bonus"], 1.0)
        self.assertEqual(data["summary"]["is_sample_data"], True)

    def test_analyze_endpoint_empty_error(self):
        resp = self.client.post("/api/analyze", json={"text": "", "extractions": []})
        self.assertEqual(resp.status_code, 400)

    def test_upload_txt_file(self):
        file_content = b"COMMERCIAL LEASE AGREEMENT\nMonthly rent is $5000 payable on the 1st."
        files = {"file": ("lease.txt", file_content, "text/plain")}
        resp = self.client.post("/api/upload", files=files)
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertEqual(data["filename"], "lease.txt")
        self.assertIn("Monthly rent", data["text"])
        self.assertEqual(data["suggestion"]["primary_suggestion"], "Lease / Rental Agreement")

    def test_upload_unsupported_file_format(self):
        files = {"file": ("malicious.exe", b"\x4d\x5a\x90\x00", "application/octet-stream")}
        resp = self.client.post("/api/upload", files=files)
        self.assertEqual(resp.status_code, 400)
        self.assertIn("Unsupported file format", resp.json()["detail"])


if __name__ == "__main__":
    unittest.main()
