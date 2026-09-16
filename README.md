# Explainable AI-Based Contract Clause Risk Analyzer

An explainable NLP pipeline for contract clause risk analysis. CUAD
(TheAtticusProject/cuad) provides clause extraction (Layer 1); this
project builds five layers on top of it — including two (Layers 5 and 6)
that address gaps left open by existing work in this area.

## Folder layout

```
Aavishkar/
|-- cuad/                            <- cloned CUAD repo (Layer 1, untouched)
|   |-- category_descriptions.csv
|-- risk_taxonomy.py                 <- Layer 2: Risk Classification
|-- risk_scorer.py                   <- Layer 3: Risk Scoring
|-- explainability.py                <- Layer 4: Explainability
|-- missing_clause_detection.py      <- Layer 5: Missing Clause Detection
|-- clause_interaction.py            <- Layer 6: Interaction Risk Analysis
|-- pipeline.py                      <- connects Layers 1-6; full_analysis() is the entry point
|-- demo.py                          <- runnable proof-of-concept
`-- README.md
```

Setup:

```bash
git clone https://github.com/The-Atticus-Project/cuad.git cuad
```

## Run it

```bash
python demo.py
```

Runs the complete Layer 1–6 pipeline on sample data shaped like real CUAD
output. No model checkpoint, GPU, or network required.

## What each layer does

**Layers 1–4 — existing work (foundation)**

- **Layer 1 — Clause Extraction (CUAD).** A CUAD-fine-tuned QA model
  (RoBERTa/DeBERTa) extracts clause spans, categories, and confidence
  scores. Used as-is; this repo does not modify CUAD.
- **Layer 2 — Risk Classification (`risk_taxonomy.py`).** Maps CUAD's real
  41 clause categories to business risk types (Financial, Restrictive
  Covenant, Termination, Renewal, Commercial, IP, Legal/Compliance) with a
  base severity per category. 8 categories use CUAD's exact annotator
  question text (marked `"source": "VERIFIED"`); the rest use real CUAD
  category names with descriptions consistent with the dataset (marked
  `"CUAD_CATEGORY"`).
- **Layer 3 — Risk Scoring (`risk_scorer.py`).** Transparent rule-based
  scoring: base severity + keyword modifiers (e.g. "unlimited", "sole
  discretion", "perpetual"), weighted by extraction confidence, mapped to
  Low / Medium / High.
- **Layer 4 — Explainability (`explainability.py`).** Natural-language
  justification per clause plus an exact attribution breakdown showing
  what contributed to each score. Because the scorer is rule-based, the
  attribution is exact rather than approximated.

**Layers 5–6 — this project's contribution**

- **Layer 5 — Missing Clause Detection (`missing_clause_detection.py`).**
  Existing contract-risk systems analyze only the clauses that are
  present; a contract missing a liability cap or dispute-resolution
  clause is never surfaced, because there is no clause to score. This
  layer reports absent protections via two clearly separated mechanisms:
  - *CUAD-model gaps* — essential CUAD categories the Layer 1 model
    returned no answer for. This signal is already computed during
    extraction and normally discarded.
  - *Heuristic gaps* — keyword checks for clause types outside CUAD's
    taxonomy entirely (Confidentiality, Dispute Resolution, Force
    Majeure, Data Privacy). These are explicitly **not** machine
    learning, and are labelled as such in the output.
- **Layer 6 — Interaction Risk Analysis (`clause_interaction.py`).**
  Existing systems score clauses independently and sum or average them,
  so compounding combinations are invisible. This layer detects known
  dangerous clause combinations — e.g. *Uncapped Financial Exposure*
  (uncapped liability with no liability cap and no insurance, +2.0) and
  *Exclusive Lock-In Trap* (exclusivity plus auto-renewal with no
  termination-for-convenience clause, +1.5) — and produces a single
  **contract-level** risk score weighted by extraction confidence, so a
  document is not rated high-risk on the strength of low-confidence
  detections.

## Entry point

```python
from pipeline import full_analysis

report = full_analysis(extractions, raw_contract_text)

report["clauses"]          # Layers 2-4: per-clause risk type, score, explanation
report["missing_clauses"]  # Layer 5: absent protections, tagged by detection method
report["contract_risk"]    # Layer 6: contract-level score + triggered interactions
```

`extractions` is Layer-1-shaped output — either from a real CUAD-fine-tuned
model via `pipeline.run_cuad_extraction()`, or the sample data in
`demo.py`. `raw_contract_text` is optional but required for Layer 5's
heuristic checks.

## Scope and status

The Layer 1–6 analysis pipeline is implemented and runnable via `demo.py`.
The web application and database shown in the project's system-architecture
diagram are the deployment plan, not yet implemented — this repository is
the analysis pipeline proof-of-concept.

## References

1. Hendrycks et al. (2021). *CUAD: An Expert-Annotated NLP Dataset for
   Legal Contract Review.* NeurIPS Datasets & Benchmarks.
2. Dikmen et al. (2025). *Automated construction contract analysis for
   risk and responsibility assessment using NLP and ML.* Computers in
   Industry 166.
3. Anusha & Rani (2026). *Smart AI-Based Framework for Automated Legal
   Clause Risk Assessment in Contracts.* IJIFR 13(8).
4. Sandhya B S & Nishanth R (2025). *Hybrid NLP Framework for Contract
   Risk Assessment — A Dual-Agent Approach.* IJSRS 2(11).
