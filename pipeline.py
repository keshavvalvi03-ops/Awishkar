"""
Pipeline: connects CUAD's real repo output (Layer 1) to your Layer 2/3/4
--------------------------------------------------------------------------
Expected folder layout (as set up earlier):

    contract-clause-risk-analyzer/
    |-- cuad/                     <- `git clone https://github.com/The-Atticus-Project/cuad.git cuad`
    |   |-- category_descriptions.csv
    |   |-- train.py / evaluate.py / utils.py / run.sh
    |-- risk_taxonomy.py          <- Layer 2
    |-- risk_scorer.py            <- Layer 3
    |-- explainability.py         <- Layer 4
    |-- pipeline.py                (this file)
    `-- demo.py

WHAT THIS FILE DOES
--------------------
1. load_cuad_questions() reads cuad/category_descriptions.csv directly from
   the cloned CUAD repo, so your questions come from the actual dataset
   file, not a hand-typed list.
2. run_cuad_extraction() calls a CUAD-fine-tuned model (HuggingFace) using
   those questions, exactly the way CUAD's own train.py/run.sh treat each
   category as a SQuAD-style question. This needs network + a checkpoint,
   so it is NOT executed in this sandbox -- it's ready to run wherever you
   have both.
3. analyze_contract() is the part that runs right now, fully offline: it
   takes Layer-1-shaped extractions (real or sample) and runs them through
   Layer 2 (risk_taxonomy) + Layer 3 (risk_scorer) + Layer 4 (explainability).
"""

import csv
import os
from typing import Dict, List

from risk_scorer import score_contract
from explainability import build_report

CUAD_REPO_DIR = os.path.join(os.path.dirname(__file__), "cuad")
CATEGORY_CSV_PATH = os.path.join(CUAD_REPO_DIR, "category_descriptions.csv")


def load_cuad_questions(csv_path: str = CATEGORY_CSV_PATH) -> Dict[str, str]:
    """
    Reads CUAD's real category_descriptions.csv (from the cloned repo) and
    returns {category_name: question_text}.

    CUAD's CSV column names aren't 100% fixed across versions, so this
    looks for the most likely column names and falls back gracefully.
    If the repo hasn't been cloned yet (file not found), it falls back to
    the verified subset of questions bundled in risk_taxonomy.py instead
    of crashing -- so this module still works for the demo even before
    you `git clone` the CUAD repo.
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
        # CUAD's actual header uses "Category" and "Question" (naming has
        # varied slightly across releases) -- check common variants.
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
    Real Layer-1 inference using a CUAD-fine-tuned model.
    Requires network + a HuggingFace checkpoint fine-tuned on CUAD
    (e.g. one following the repo's train.py/run.sh recipe on RoBERTa or
    DeBERTa). NOT runnable offline in this sandbox -- drop in your
    checkpoint path/hub id and run this wherever you have GPU/network.
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
    Runs TODAY, fully offline: takes Layer-1-style extractions (whether
    from the real CUAD model or sample/mock data) and runs Layers 2, 3,
    and 4 on them.
    """
    scored = score_contract(extractions)
    return build_report(scored)
