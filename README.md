# Contract Clause Risk Analyzer — Layers 2/3/4

CUAD (TheAtticusProject/cuad) only does Layer 1: clause extraction. This
package adds everything your topic actually promises on top of it.

## Folder layout

```
contract-clause-risk-analyzer/
|-- cuad/                     <- clone CUAD's repo here (Layer 1, untouched)
|   |-- category_descriptions.csv
|   |-- train.py / evaluate.py / utils.py / run.sh
|-- risk_taxonomy.py          <- Layer 2: risk classification
|-- risk_scorer.py            <- Layer 3: risk scoring
|-- explainability.py         <- Layer 4: explainability
|-- pipeline.py               <- connects CUAD's output to Layers 2-4
|-- demo.py                   <- runnable proof-of-concept
`-- README.md
```

Set it up:
```bash
mkdir contract-clause-risk-analyzer && cd contract-clause-risk-analyzer
git clone https://github.com/The-Atticus-Project/cuad.git cuad
# then copy risk_taxonomy.py, risk_scorer.py, explainability.py,
# pipeline.py, demo.py into this same top-level folder (NOT inside cuad/)
```

## What each layer does

- **`risk_taxonomy.py` (Layer 2)** — maps CUAD's real 41 clause categories
  to business risk types (Financial, Restrictive Covenant, Termination,
  Renewal, Commercial, IP, Legal/Compliance) with a base severity per
  category. 8 categories use CUAD's exact annotator question text
  (marked `"source": "VERIFIED"`); the rest use real CUAD category names
  with descriptions consistent with the dataset (marked `"CUAD_CATEGORY"`).
- **`risk_scorer.py` (Layer 3)** — rule-based scoring engine: base
  severity + keyword modifiers (e.g. "unlimited", "sole discretion"),
  weighted by the extraction model's confidence, mapped to Low/Medium/High.
- **`explainability.py` (Layer 4)** — generates a natural-language
  justification per clause, plus an exact attribution breakdown of what
  contributed to the score (your "Explainable AI" evidence for the poster).
- **`pipeline.py`** — `load_cuad_questions()` reads the real
  `category_descriptions.csv` from your cloned `cuad/` folder (falling
  back to the verified subset in `risk_taxonomy.py` if that folder isn't
  present yet, so the demo still runs). `run_cuad_extraction()` shows how
  to call an actual CUAD-fine-tuned model via HuggingFace once you have a
  checkpoint + network/GPU. `analyze_contract()` runs Layers 2-4 on
  whatever extractions you feed it — real or sample.
- **`demo.py`** — runs the whole thing right now on sample data shaped
  like real CUAD output. No model, checkpoint, or network needed.

## Run it

```bash
python demo.py
```

## Connecting the real CUAD model (Layer 1) once you have GPU/network

```python
from pipeline import run_cuad_extraction, analyze_contract

extractions = run_cuad_extraction(contract_text, model_id="<cuad-finetuned-checkpoint>")
report = analyze_contract(extractions)
```

That's the full pipeline: CUAD extracts clauses -> your taxonomy classifies
risk type -> your scorer assigns severity -> your explainability layer
justifies the flag in plain language.
