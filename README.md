# Explainable AI-Based Contract Clause Risk Analyzer

An explainable NLP and rule-based pipeline for contract clause risk analysis and missing clause detection. Built on top of CUAD (TheAtticusProject/cuad) clause extraction (Layer 1), this project implements five additional layers (Layers 2–6) providing transparent risk scoring, feature attribution, contract-specific checklist verification, and cross-clause compounding interaction analysis across **10 commercial contract types**.

---

## 1. System Architecture

The pipeline uses a modular six-layer architecture:

```
+-----------------------------------------------------------------------------------+
| Layer 1: Clause Extraction (CUAD Model / Experimental Keyword Detector)           |
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

## 5. Live CUAD Extraction Status

- **Status in Repository**: The live model loader in `pipeline.py` (`run_cuad_extraction()`) is an interface designed to connect to HuggingFace question-answering checkpoints (e.g. `mrm8488/roberta-base-finetuned-cuad`).
- **Dependencies**: Running live transformer inference requires optional dependencies (`torch`, `transformers`) which are documented in `requirements.txt`.
- **Offline Readiness**: The core 6-layer pipeline, `demo.py`, `demo_multi_contract.py`, `custom_detector.py`, and all 37 automated tests run **100% offline** on standard Python 3.8+ without downloading neural weights or requiring network/GPU access.

---

## 6. Bugs Fixed in this Version

1. **Empty Input Schema Completeness**: Fixed `aggregate_contract_risk([])` and `full_analysis([], None)` so that `base_weighted_score`, `interaction_bonus`, and all other fields are always present, eliminating `KeyError` crashes.
2. **`confidence=None` Handling**: Fixed `score_clause()` to handle `confidence=None` without raising `TypeError: unsupported operand type(s) for *: 'NoneType' and 'int'`.
3. **Zero-Confidence Division by Zero**: Fixed `aggregate_contract_risk()` when all clause confidences are `0.0`, eliminating `ZeroDivisionError`.
4. **Missing / None Extraction Text**: Handled `None` or non-string clause text safely, eliminating `AttributeError` on `.lower()`.
5. **Category Normalization**: Added robust case-insensitive and synonym normalization (e.g. `"INDEMNIFICATION"` -> `"Indemnity"`, `"limitation of liability"` -> `"Cap On Liability"`, `"licence grant"` -> `"License Grant"`).
6. **False-Positive Keyword Matching**: Replaced naive substring search with regex word-boundary matching (`\b`), preventing substring collisions (e.g. `"exceptional"` matching `"except"`).
7. **CUAD Questions CSV Parsing & Governing Law Fallback**: Fixed UTF-8 BOM encoding issues and column header mismatch (`Category (incl. context and answer)` / `Description`), ensuring all 41 CUAD questions (including `Governing Law`) load properly.
8. **Exclusive Lock-In Logic**: Updated `Exclusive Lock-In Trap` to verify actual automatic/evergreen renewal language rather than penalizing contracts with standard mutual-consent renewal clauses.
9. **Contract-Type Checklists**: Replaced hardcoded one-size-fits-all missing clause checks with contract-specific checklists while maintaining 100% backward compatibility for existing callers.

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

This score is mathematically derived from the transparent scoring formula and is verified by automated regression tests.

---

## 8. Installation & Windows CMD Commands

### Prerequisites
- Python 3.8, 3.10, 3.11, or 3.12 installed.
- No third-party packages are required for standard offline analysis.

### Running Demos in Windows CMD

Open Windows Command Prompt (`cmd.exe`) and navigate to the project directory:

```cmd
cd C:\Users\ADMIN\Documents\Awishkar
```

**1. Run Original Baseline Demo:**
```cmd
python demo.py
```

**2. Run Multi-Contract Demo (All 10 Contract Types):**
```cmd
python demo_multi_contract.py
```

**3. Run Multi-Contract Demo for a Specific Contract Type:**
```cmd
python demo_multi_contract.py --type nda
python demo_multi_contract.py --type service
python demo_multi_contract.py --type lease
python demo_multi_contract.py --type software
```

**4. Run Automated Test Suite (37 Unit & Regression Tests):**
```cmd
python -m unittest discover -s tests -v
```

### Optional: Installing Neural ML Dependencies (For Live QA Transformer Inference)
If you wish to test live HuggingFace QA extraction with PyTorch:
```cmd
pip install -r requirements.txt
```

---

## 9. Git Instructions (Pushing Verified Changes)

To review and push your verified local changes to your GitHub repository:

```cmd
cd C:\Users\ADMIN\Documents\Awishkar

git status
git add .
git commit -m "Extend Contract Risk Analyser: 10 contract types, extended taxonomy, custom detector, bug fixes, and unit tests"
git push origin main
```

---

## 10. Scope and Known Limitations

- **Scope**: This repository contains the core explainable NLP and rule-based risk analysis engine, contract type checklists, and automated test suite.
- **Web Interface & Database**: The web dashboard, user authentication, and database schemas referenced in high-level architectural proposals are future deployment milestones and are not yet implemented in this repository.
- **Document Ingestion**: File parsing for PDF/DOCX uploads is not yet implemented; the pipeline currently ingests plain text strings and structured extraction dictionaries.
- **Legal Advice**: This software is an explainable decision-support tool for contract triage and review acceleration. It does not provide legal advice or guarantee universal jurisdictional compliance.

---

## 11. References

1. Hendrycks et al. (2021). *CUAD: An Expert-Annotated NLP Dataset for Legal Contract Review.* NeurIPS Datasets & Benchmarks.
2. Dikmen et al. (2025). *Automated construction contract analysis for risk and responsibility assessment using NLP and ML.* Computers in Industry 166.
3. Anusha & Rani (2026). *Smart AI-Based Framework for Automated Legal Clause Risk Assessment in Contracts.* IJIFR 13(8).
4. Sandhya B S & Nishanth R (2025). *Hybrid NLP Framework for Contract Risk Assessment — A Dual-Agent Approach.* IJSRS 2(11).
