"""
Pipeline: connects CUAD Layer 1 to Layers 2-6 with Multi-Contract Support
-------------------------------------------------------------------------
Connects:
- Layer 1: Clause Extraction (CUAD model or Custom Detector)
- Layer 2: Risk Classification Taxonomy (risk_taxonomy.py, custom_taxonomy.py)
- Layer 3: Risk Scoring Engine (risk_scorer.py)
- Layer 4: Explainability & Attribution (explainability.py)
- Layer 5: Contract-Specific Missing Clause Detection (missing_clause_detection.py, contract_types.py)
- Layer 6: Cross-Clause Interaction Risk & Contract Aggregation (clause_interaction.py)

Bugs fixed:
- Fixes CSV parsing and BOM issues in load_cuad_questions(), restoring Governing Law loading.
- Normalizes CUAD category names to canonical taxonomy keys.
- Graceful handling of missing model checkpoints and optional transformers dependency.
- Backward compatibility for full_analysis() keys (clauses, missing_clauses, contract_risk).
- Adds support for 10 contract types, contract-specific checklists, and suggestions.
"""

import csv
import os
import re
from typing import Dict, List, Optional, Any

from risk_scorer import score_contract
from explainability import build_report
from missing_clause_detection import detect_missing_clauses, evaluate_contract_checklist
from clause_interaction import aggregate_contract_risk
from contract_types import suggest_contract_type, get_contract_type, CONTRACT_TYPES
from custom_taxonomy import normalize_category_name

CUAD_REPO_DIR = os.path.join(os.path.dirname(__file__), "cuad")
CATEGORY_CSV_PATH = os.path.join(CUAD_REPO_DIR, "category_descriptions.csv")


def load_cuad_questions(csv_path: str = CATEGORY_CSV_PATH) -> Dict[str, str]:
    """
    Reads CUAD's category_descriptions.csv (from the cloned repo) and
    returns {category_name: question_text}.

    Bugs fixed:
    - Handles utf-8-sig encoding (BOM) cleanly.
    - Matches real CSV column names ('Category (incl. context and answer)' and 'Description').
    - Strips 'Category: ' and 'Description: ' prefixes from values.
    - Normalizes category names to canonical taxonomy keys (e.g. 'Cap On Liability').
    - Gracefully falls back to risk_taxonomy and custom_taxonomy with Governing Law included.
    """
    if os.path.exists(csv_path):
        try:
            questions = {}
            with open(csv_path, newline="", encoding="utf-8-sig") as f:
                reader = csv.DictReader(f)
                fieldnames = reader.fieldnames or []
                cat_col = next((c for c in fieldnames if "category" in c.lower()), None)
                q_col = next((c for c in fieldnames if any(k in c.lower() for k in ["question", "description"])), None)

                if cat_col and q_col:
                    for row in reader:
                        raw_cat = row.get(cat_col, "")
                        raw_q = row.get(q_col, "")
                        cat_clean = re.sub(r"^category:\s*", "", raw_cat.strip(), flags=re.IGNORECASE)
                        q_clean = re.sub(r"^description:\s*", "", raw_q.strip(), flags=re.IGNORECASE)
                        cat_canonical = normalize_category_name(cat_clean)
                        if cat_canonical and q_clean:
                            questions[cat_canonical] = q_clean

            if questions:
                return questions
        except Exception as e:
            print(f"[warning] Failed parsing {csv_path} ({e}). Falling back to internal taxonomy questions.")

    # Fallback to verified internal question set
    from risk_taxonomy import RISK_TAXONOMY
    from custom_taxonomy import CUSTOM_TAXONOMY

    fallback = {cat: info.get("cuad_question", "") for cat, info in RISK_TAXONOMY.items()}
    fallback["Governing Law"] = "Which state/country's law governs the interpretation of the contract?"
    for cat, info in CUSTOM_TAXONOMY.items():
        if "cuad_question" in info:
            fallback[cat] = info["cuad_question"]
    return fallback


def run_cuad_extraction(contract_text: str,
                         threshold: float = 0.5,
                         model_id: str = "<path-or-hub-id-of-cuad-finetuned-model>"
                         ) -> List[Dict[str, Any]]:
    """
    Layer-1 inference using a CUAD-fine-tuned QA model (HuggingFace).

    REQUIREMENTS & STATUS:
    - Requires 'transformers' and 'torch' installed in Python.
    - Requires a fine-tuned model checkpoint (e.g., 'mrm8488/roberta-base-finetuned-cuad' or local path).
    - If running offline or without weights, use custom_detector.scan_all_clauses() instead.
    """
    try:
        from transformers import pipeline  # optional dependency
    except ImportError as e:
        raise ImportError(
            "Transformers is not installed. To run live Layer-1 QA inference, "
            "install PyTorch and HuggingFace transformers (`pip install torch transformers`), "
            "or run with pre-extracted spans or custom_detector for offline rule-based analysis."
        ) from e

    if model_id.startswith("<") and model_id.endswith(">"):
        raise ValueError(
            f"Placeholder model_id '{model_id}' cannot be run. Please provide a valid "
            f"HuggingFace model hub ID (e.g. 'mrm8488/roberta-base-finetuned-cuad') "
            f"or a path to a locally trained model checkpoint."
        )

    qa = pipeline("question-answering", model=model_id)
    questions = load_cuad_questions()

    extractions = []
    for category, question in questions.items():
        result = qa(question=question, context=contract_text)
        if result["score"] >= threshold and result["answer"].strip():
            extractions.append({
                "category": category,
                "text": result["answer"],
                "confidence": round(float(result["score"]), 4),
                "detection_method": "cuad_model",
            })
    return extractions


def analyze_contract(extractions: List[Dict]) -> List[Dict]:
    """
    Layers 2-4 only (kept for backwards compatibility).
    """
    scored = score_contract(extractions)
    return build_report(scored)


def full_analysis(extractions: Optional[List[Dict]] = None,
                  raw_contract_text: Optional[str] = None,
                  contract_type: Optional[str] = None) -> Dict[str, Any]:
    """
    The complete Layer 1 -> Layer 6 pipeline.

    Parameters:
    - extractions: List of clause extraction dicts (from CUAD or custom detector)
    - raw_contract_text: Full raw text of the contract (for heuristic and missing clause scans)
    - contract_type: Optional contract type name (e.g. 'Service Agreement', 'Employment Agreement',
                     'NDA / Confidentiality Agreement', etc.). If None, general baseline checks
                     run and contract type suggestion is provided.

    Returns:
    - clauses: Per-clause scored report (Layers 2-4)
    - missing_clauses: Missing-clause findings (Layer 5)
    - contract_risk: Aggregated risk score and interactions (Layer 6)
    - contract_type: Active or suggested contract type metadata
    - contract_checklist: Comprehensive status table for all checklist items
    """
    safe_extractions = extractions if extractions is not None else []

    # Layers 2-4: Per-clause scoring, explainability, attribution
    scored_clauses = score_contract(safe_extractions)
    clause_report = build_report(scored_clauses)

    # Layer 5: Missing clause detection
    missing_clauses = detect_missing_clauses(
        safe_extractions,
        raw_contract_text=raw_contract_text,
        contract_type=contract_type,
    )

    # Layer 6: Cross-clause interaction and contract-level risk
    contract_risk = aggregate_contract_risk(scored_clauses)

    # Contract Type Identification and Checklist
    if contract_type is not None:
        type_def = get_contract_type(contract_type)
        active_type_name = type_def.name if type_def else contract_type
        type_info = {
            "selected_type": active_type_name,
            "is_user_specified": True,
            "description": type_def.description if type_def else "",
        }
        checklist_table = evaluate_contract_checklist(
            active_type_name, safe_extractions, raw_contract_text
        )
    else:
        suggestion = suggest_contract_type(raw_contract_text, safe_extractions)
        type_info = {
            "selected_type": None,
            "is_user_specified": False,
            "suggestion": suggestion,
        }
        suggested_name = suggestion.get("primary_suggestion")
        checklist_table = evaluate_contract_checklist(
            suggested_name, safe_extractions, raw_contract_text
        )

    return {
        "clauses": clause_report,
        "missing_clauses": missing_clauses,
        "contract_risk": contract_risk,
        "contract_type": type_info,
        "contract_checklist": checklist_table,
    }
