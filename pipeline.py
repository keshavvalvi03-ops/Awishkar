"""
Pipeline: connects CUAD's real repo output (Layer 1) to Layers 2-6
--------------------------------------------------------------------------
Expected folder layout:

    Awishkar/
    |-- cuad/                     <- `git clone https://github.com/The-Atticus-Project/cuad.git cuad`
    |   |-- category_descriptions.csv
    |-- risk_taxonomy.py                 <- Layer 2
    |-- risk_scorer.py                   <- Layer 3
    |-- explainability.py                <- Layer 4
    |-- missing_clause_detection.py      <- Layer 5
    |-- clause_interaction.py            <- Layer 6
    |-- pipeline.py                       (this file)
    `-- demo.py

WHAT CHANGED FROM THE PREVIOUS VERSION OF THIS FILE
------------------------------------------------------
The version of pipeline.py previously in this repo only imported
risk_scorer and explainability, and only ran Layers 2-4 via
analyze_contract(). Layers 5 and 6 existed as files
(missing_clause_detection.py, clause_interaction.py) but were never
imported or called from anywhere -- so they were disconnected from the
actual pipeline despite being present in the repo.

This version adds the missing imports and a new full_analysis() function
that runs the complete Layer 1 -> Layer 6 chain and returns one combined
report: per-clause results (Layers 2-4), missing-clause findings
(Layer 5), and one contract-level risk score with interaction findings
(Layer 6). analyze_contract() is kept for backwards compatibility but
full_analysis() is now the function your demo/UI should call.
"""

import csv
import os
from typing import Dict, List, Optional

from risk_scorer import score_contract
from explainability import build_report
from missing_clause_detection import detect_missing_clauses
from clause_interaction import aggregate_contract_risk

CUAD_REPO_DIR = os.path.join(os.path.dirname(__file__), "cuad")
CATEGORY_CSV_PATH = os.path.join(CUAD_REPO_DIR, "category_descriptions.csv")


def load_cuad_questions(csv_path: str = CATEGORY_CSV_PATH) -> Dict[str, str]:
    """
    Reads CUAD's real category_descriptions.csv (from the cloned repo) and
    returns {category_name: question_text}. Falls back to the verified
    question subset in risk_taxonomy.py if the CUAD repo isn't cloned yet,
    so this still works without network access.
    """
    if not os.path.exists(csv_path):
        print(f"[warning] {csv_path} not found -- clone the CUAD repo into "
              f"./cuad first. Falling back to the verified question subset "
              f"already in risk_taxonomy.py.")
        from risk_taxonomy import RISK_TAXONOMY
        return {cat: info["cuad_question"] for cat, info in RISK_TAXONOMY.items()}

    questions = {}
    with open(csv_path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames or []
        cat_col = next((c for c in fieldnames if c.strip().lower() == "category"), None)
        q_col = next((c for c in fieldnames if "question" in c.strip().lower()), None)

        if not (cat_col and q_col):
            raise ValueError(
                f"Couldn't find Category/Question columns in {csv_path}. "
                f"Found columns: {fieldnames}. Open the CSV and adjust "
                f"cat_col/q_col in load_cuad_questions() accordingly."
            )

        for row in reader:
            category = row[cat_col].strip()
            question = row[q_col].strip()
            if category and question:
                questions[category] = question

    return questions


def run_cuad_extraction(contract_text: str, threshold: float = 0.5,
                         model_id: str = "<path-or-hub-id-of-cuad-finetuned-model>"
                         ) -> List[Dict]:
    """
    Real Layer-1 inference using a CUAD-fine-tuned model (HuggingFace).
    Requires network + a checkpoint -- not runnable offline in this
    sandbox. Drop in your model path/hub id and run wherever you have
    GPU/network access.
    """
    from transformers import pipeline  # local import: optional dependency
    qa = pipeline("question-answering", model=model_id)
    questions = load_cuad_questions()

    extractions = []
    for category, question in questions.items():
        result = qa(question=question, context=contract_text)
        if result["score"] >= threshold and result["answer"].strip():
            extractions.append({
                "category": category,
                "text": result["answer"],
                "confidence": result["score"],
            })
    return extractions


def analyze_contract(extractions: List[Dict]) -> List[Dict]:
    """
    Layers 2-4 only (kept for backwards compatibility / simpler use).
    Runs today, fully offline, on real or sample Layer-1-shaped extractions.
    """
    scored = score_contract(extractions)
    return build_report(scored)


def full_analysis(extractions: List[Dict], raw_contract_text: Optional[str] = None) -> Dict:
    """
    The complete Layer 1 -> Layer 6 pipeline. This is what your demo/UI
    should call. `raw_contract_text` is optional but needed for the
    heuristic missing-clause checks in Layer 5 (Confidentiality, Dispute
    Resolution, Force Majeure, Data Privacy -- none of which are CUAD
    categories, so they can't be found in `extractions` at all).
    """
    scored_clauses = score_contract(extractions)
    clause_report = build_report(scored_clauses)                             # Layers 2-4
    missing_clauses = detect_missing_clauses(extractions, raw_contract_text)  # Layer 5
    contract_risk = aggregate_contract_risk(scored_clauses)                  # Layer 6

    return {
        "clauses": clause_report,
        "missing_clauses": missing_clauses,
        "contract_risk": contract_risk,
    }
