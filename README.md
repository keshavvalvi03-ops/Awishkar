# Explainable AI-Based Contract Clause Risk Analyzer

**ClauseGuard AI — Explainable Contract Risk Analysis**

An explainable NLP and rule-based pipeline with an interactive web application for contract clause risk analysis and missing clause detection. Built on top of CUAD (TheAtticusProject/cuad) clause extraction (Layer 1), this project implements five additional layers (Layers 2–6) providing transparent risk scoring, exact feature attribution, contract-specific checklist verification, compounding cross-clause risk analysis, and an executive legal audit dashboard across **10 commercial contract types**.

---

## 1. System Architecture

The pipeline uses a modular six-layer architecture:

```
+-----------------------------------------------------------------------------------+
| Layer 1: Clause Extraction (CUAD QA Model / Experimental Keyword Detector)        |
+-----------------------------------------------------------------------------------+
                                         |
+-----------------------------------------------------------------------------------+
| Layer 2: Clause Classification & Risk Taxonomy (risk_taxonomy.py, custom_taxonomy)|
|   - 41 CUAD Categories + 40 Extended Commercial Categories                        |
|   - Canonical Alias Normalization (case-insensitive, British/American spellings)   |
|   - Risk Type & Base Severity (verified vs provisional baselines)                 |
+-----------------------------------------------------------------------------------+
                                         |
+-----------------------------------------------------------------------------------+
| Layer 3: Transparent Risk Scoring Engine (risk_scorer.py)                         |
|   - Base Severity + Regex Word-Boundary Keyword Modifiers                         |
|   - Confidence Calibration Weighting (pulls low-confidence towards neutral 5/10)   |
+-----------------------------------------------------------------------------------+
                                         |
+-----------------------------------------------------------------------------------+
| Layer 4: Explainability & Exact Attribution (explainability.py)                   |
|   - Natural Language Justifications                                               |
|   - Exact Feature Attribution Breakdowns (Rule-based, exact rather than SHAP/LIME)|
+-----------------------------------------------------------------------------------+
                                         |
+-----------------------------------------------------------------------------------+
| Layer 5: Contract-Specific Missing Clause Detection (missing_clause_detection.py) |
|   - 10 Contract Type Checklists (Expected, Conditional, Optional)                 |
|   - Statuses: Detected, Not detected — verify manually, Uncertain, Not applicable |
|   - Contract Type Suggestion Engine with Uncertainty & Evidence (contract_types)  |
+-----------------------------------------------------------------------------------+
                                         |
+-----------------------------------------------------------------------------------+
| Layer 6: Cross-Clause Interaction Risk & Document Aggregation (clause_interaction)|
|   - Compounding Risk Rules (Uncapped Exposure, Auto-Renew Lock-In, Abrupt Walkway)|
|   - Confidence-Calibrated Contract-Level Risk Score [0 - 10]                      |
+-----------------------------------------------------------------------------------+
```

---

## 2. Supported Contract Types (10 Types)

The system supports contract-specific analysis and checklist evaluation for:

1. **Service Agreement** (Master Services Agreement, Consulting Contract)
2. **Employment Agreement** (Executive Employment, Offer Letters)
3. **NDA / Confidentiality Agreement** (Mutual / Unilateral Non-Disclosure)
4. **Software / IT Agreement** (SaaS, Cloud Hosting, Software License)
5. **Vendor / Supply Agreement** (Manufacturing, Component Supply, Purchase Orders)
6. **Lease / Rental Agreement** (Commercial Tenancy, Real Estate Lease)
7. **Licensing Agreement** (Patent, Trademark, IP Technology Licensing)
8. **Partnership Agreement** (General Partnership, LLP, Joint Venture)
9. **Merger / Acquisition Agreement** (Stock Purchase, Asset Purchase, Merger Plan)
10. **General Business Agreement** (Commercial Trade, Bilateral Agreements)

Each contract type defines an explicit checklist with:
- **Relevance**: `Expected`, `Conditional`, or `Optional`
- **Reason**: Legal/commercial rationale for presence or absence
- **Detection Method**: `cuad_model`, `experimental_keyword`, or `manual_review`
- **Support Status**: `supported_cuad`, `supported_keyword`, or `manual_only`
- **Recommended Action**: Recommended triage step for reviewing counsel

---

## 3. Clause Categories & Taxonomy Coverage

The taxonomy reuses existing CUAD categories where applicable and extends them with commercial categories without creating duplicates:

- **General Commercial**: Indemnity, Limitation of Liability / Cap On Liability, Uncapped Liability, Scope of Services, Payment Terms, Late Fees, Termination for Convenience, Termination for Cause, Governing Law, Dispute Resolution, Confidentiality, Insurance, Warranties, Warranty Duration, Force Majeure, Data Privacy, Data Protection and Security, Entire Agreement, Notice Requirements, Assignment, Non-Solicitation, Non-Compete, Change of Control.
- **Software & Intellectual Property**: IP Ownership Assignment (canonical for IP Ownership & IP Assignment), Joint IP Ownership, License Grant, Licence Restrictions, Royalties, Licence Fees, Source Code Escrow, Support and Maintenance, Service Levels (SLA), Delivery and Acceptance.
- **Lease & Real Estate**: Rent, Security Deposit, Property Maintenance, Landlord and Tenant Obligations, Lease Termination.
- **Employment**: Salary and Compensation, Benefits, Working Conditions, Employment Termination.
- **Partnership & Corporate**: Capital Contributions, Profit and Loss Sharing, Partner Responsibilities, Partner Exit and Dissolution.
- **Mergers & Acquisitions**: Representations and Warranties, Purchase Price, Closing Conditions, Post-Closing Obligations.
- **Vendor & Supply**: Product Specifications and Quality, Inspection and Acceptance, Delivery Obligations, Remedies for Non-Performance.

> [!NOTE]
> **Provisional Severity Notice**: Severity scores for extended categories are provisional heuristic baselines intended for review prioritization and have **not** been validated by an expert legal panel. Only categories marked `"source": "VERIFIED"` originate directly from CUAD's expert-annotated task specifications.

---

## 4. Detection Transparency & Limitations

The system clearly differentiates detection methodologies:

- **CUAD-based Extraction (`cuad_model`)**: Probabilistic span extraction using fine-tuned transformer QA models. Extraction confidence (0.0 to 1.0) is factored into scoring and aggregation.
- **Experimental Keyword Detection (`experimental_keyword`)**: Rule-based regex pattern matching enforcing strict word boundaries (`\b`) to eliminate false-positive substring matches (e.g. preventing `"exceptional"` from triggering `"except"`). Evidence snippets are returned. **Confidence scores are explicitly set to None** to avoid inventing pseudo-probabilities. This is heuristic pattern matching, **not** a trained machine learning model.
- **Manual Review Required (`manual_review`)**: Clauses that require human legal interpretation (e.g. bespoke indemnification caps or complex earnouts).
- **Uncertain (`Uncertain`)**: Extractions with low confidence (< 50%) or ambiguous contract-type signals are flagged as uncertain rather than silently accepted.

> [!WARNING]
> A missing keyword match does **not** prove a clause is legally absent. Conversely, a detected keyword does **not** prove a clause is legally adequate, enforceable, or commercially favorable.

---

## 5. Web Application Features (ClauseGuard AI)

The web dashboard is built for local execution and presentation at college research competitions (Avishkar):

- **Overview / Home**: Research summary, 6-layer architecture cards, quick-start action buttons.
- **Analyse Contract**: Raw text pasteboard, genuine file drag-and-drop for `.txt`, `.pdf`, `.docx`, contract-type auto-suggestion with confidence and uncertainty badges, quick benchmark sample loaders.
- **Risk Dashboard**: Contract risk score gauge [0–10], Low/Medium/High badge, summary counters, interactive Chart.js donut and bar charts, searchable and filterable clause matrix.
- **Explainable AI (XAI)**: Clause-by-clause explainability cards showing exact evidence snippets, risk-modifying phrases (`'unlimited'`, `'sole discretion'`), and full mathematical attribution breakdowns.
- **Missing Clauses Checklist**: Contract-specific checklist filterable by `Expected`, `Conditional`, `Optional`, and `Not detected — verify manually`.
- **Cross-Clause Interactions**: Triggered compounding interaction trap cards (bonus score, reasons, mitigating conditions) and non-triggered rules.
- **Executive Report**: Printable legal memo layout with one-click print-to-PDF export.
- **Architecture & Methodology**: Detailed academic breakdown of all 6 layers and research citations.
- **Clause Inspector Modal**: Click any clause row to inspect its exact evidence and mathematical attribution breakdown.

---

## 6. Installation & Execution (Windows CMD)

### Prerequisites
- Python 3.8+ installed (tested on Python 3.12).
- Pip package manager.

### 1. Install Dependencies
Open Windows Command Prompt (`cmd.exe`) and navigate to the project directory:

```cmd
cd C:\Users\ADMIN\Documents\Awishkar

pip install -r requirements.txt
```

### 2. Launch the Web Application
Run the FastAPI web server:

```cmd
python app.py
```
*Or using uvicorn directly:*
```cmd
uvicorn app:app --host 127.0.0.1 --port 8000 --reload
```

Open your web browser and navigate to:
**http://127.0.0.1:8000**

---

### 3. Run Command-Line Demos & Automated Tests

**Run Baseline Demo (Original PoC):**
```cmd
python demo.py
```
*(Produces exact verified score: `8.16 / 10 High`)*

**Run Multi-Contract CLI Demo (All 10 Contract Types):**
```cmd
python demo_multi_contract.py
```

**Run Multi-Contract CLI Demo for a Specific Type:**
```cmd
python demo_multi_contract.py --type nda
python demo_multi_contract.py --type service
python demo_multi_contract.py --type lease
```

**Run All 47 Automated Unit and Integration Tests:**
```cmd
python -m unittest discover -s tests -v
```

---

## 7. Baseline Score Verification

The baseline proof-of-concept demonstration (`demo.py`) produces the verified baseline score:

```
Contract-level risk score: 8.16 / 10 (High)
  base weighted score: 7.16, interaction bonus: +1.0
  average extraction confidence: 75%

Triggered interactions:
  - Abrupt Walkaway Risk (+1.0): Either party can terminate without cause, but no post-termination obligations (wind-down, transition, hand-back) are defined...
```

This score is mathematically derived from the transparent scoring formula and is verified by automated regression tests in `tests/test_pipeline_and_regression.py` and `tests/test_api.py`.

---

## 8. Git Instructions (Pushing Verified Changes)

To review and push your verified local changes to your GitHub repository:

```cmd
cd C:\Users\ADMIN\Documents\Awishkar

git status
git add .
git commit -m "Build ClauseGuard AI: Interactive FastAPI web application, document upload, and 47 automated tests"
git push origin main
```

---

## 9. Scope and Known Limitations

- **Scope**: Core explainable NLP pipeline, multi-contract type checklists, keyword pattern matching, FastAPI backend, and single-page interactive dashboard.
- **Genuine Document Ingestion**: Text extraction is fully implemented and tested for `.txt`, `.pdf` (via `pypdf`), and `.docx` (via `python-docx`). Scanned PDFs containing only images without text OCR are transparently flagged.
- **Database & Authentication**: User login and persistent database storage are future roadmap items; all processing currently runs locally in memory without tracking user data.
- **Legal Advice**: This software is an explainable decision-support tool for contract triage and review acceleration. It does not provide legal advice or guarantee universal jurisdictional compliance.

---

## 10. References

1. Hendrycks et al. (2021). *CUAD: An Expert-Annotated NLP Dataset for Legal Contract Review.* NeurIPS Datasets & Benchmarks.
2. Dikmen et al. (2025). *Automated construction contract analysis for risk and responsibility assessment using NLP and ML.* Computers in Industry 166.
3. Anusha & Rani (2026). *Smart AI-Based Framework for Automated Legal Clause Risk Assessment in Contracts.* IJIFR 13(8).
4. Sandhya B S & Nishanth R (2025). *Hybrid NLP Framework for Contract Risk Assessment — A Dual-Agent Approach.* IJSRS 2(11).
