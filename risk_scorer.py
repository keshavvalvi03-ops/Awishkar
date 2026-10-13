"""
Layer 3: Risk Scoring Engine
-----------------------------
Takes the output of CUAD's clause-extraction model (Layer 1: category +
extracted text span + model confidence) or custom detector and produces
a numeric risk score and a Low/Medium/High level.

Transparent, rule-based scorer:
  score = base_severity + sum of keyword modifiers, weighted by confidence.
"""

import re
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Union

from risk_taxonomy import KEYWORD_MODIFIERS, get_risk_level
from custom_taxonomy import (
    EXTENDED_TAXONOMY,
    normalize_category_name,
    get_category_info,
)


@dataclass
class ScoredClause:
    category: str
    clause_text: str
    confidence: float
    risk_type: str
    base_severity: Union[int, float]
    matched_keywords: List[str] = field(default_factory=list)
    keyword_bonus: Union[int, float] = 0
    raw_score: Union[int, float] = 0
    final_score: Union[int, float] = 0.0
    risk_level: str = "Low"
    provisional: bool = False
    original_category: str = ""


# Compile word-bounded regex patterns for keyword modifiers to avoid false positives
_COMPILED_MODIFIERS = {
    kw: re.compile(r"\b" + re.escape(kw) + r"\b", re.IGNORECASE)
    for kw in KEYWORD_MODIFIERS.keys()
}


def score_clause(category: str,
                 clause_text: Optional[str] = "",
                 confidence: Optional[float] = 1.0) -> ScoredClause:
    """
    Scores a single extracted clause with safe input handling.

    Bugs fixed:
    - Handles confidence=None gracefully (defaults to 1.0).
    - Handles clause_text=None or non-string inputs safely.
    - Uses category alias normalization and case insensitivity.
    - Uses regex word-boundary matching to prevent false-positive substring matches.
    - Handles unrecognized/informational categories without crashing.
    """
    safe_text = str(clause_text or "").strip()
    safe_conf = 1.0 if confidence is None else float(confidence)
    safe_conf = max(0.0, min(1.0, safe_conf))  # clamp to [0, 1]

    canonical = normalize_category_name(category)
    cat_info = get_category_info(canonical)

    if cat_info is None:
        # Category is not a risk-bearing clause (e.g. "Parties", "Agreement Date")
        # or completely unrecognized
        return ScoredClause(
            category=canonical if canonical != "Unknown" else str(category),
            clause_text=safe_text,
            confidence=safe_conf,
            risk_type="N/A",
            base_severity=0,
            raw_score=0,
            final_score=0,
            risk_level="Not Applicable",
            provisional=False,
            original_category=str(category),
        )

    base = cat_info["base_severity"]
    risk_type = str(cat_info["risk_type"])
    is_prov = cat_info.get("provisional", False)

    # Word-bounded keyword matching to prevent false positives
    matched = []
    bonus = 0
    for kw, pattern in _COMPILED_MODIFIERS.items():
        if pattern.search(safe_text):
            matched.append(kw)
            bonus += KEYWORD_MODIFIERS[kw]

    raw_score = base + bonus

    # Confidence weighting: pull toward neutral 5.0 for low-confidence detections
    final_score = safe_conf * raw_score + (1.0 - safe_conf) * 5
    final_score = max(0, min(10, final_score))  # clamp to [0, 10]
    final_score = round(final_score, 2)

    return ScoredClause(
        category=canonical,
        clause_text=safe_text,
        confidence=safe_conf,
        risk_type=risk_type,
        base_severity=base,
        matched_keywords=matched,
        keyword_bonus=bonus,
        raw_score=raw_score,
        final_score=final_score,
        risk_level=get_risk_level(final_score),
        provisional=is_prov,
        original_category=str(category),
    )


def score_contract(extractions: Optional[List[Dict[str, Any]]]) -> List[ScoredClause]:
    """
    Scores all extractions in a contract.
    Safely handles empty extractions, missing keys, or None values.
    """
    if not extractions:
        return []

    scored_list = []
    for e in extractions:
        if not isinstance(e, dict):
            continue
        cat = e.get("category", "")
        txt = e.get("text", "")
        conf = e.get("confidence", 1.0)
        scored_list.append(score_clause(cat, txt, conf))

    return scored_list
