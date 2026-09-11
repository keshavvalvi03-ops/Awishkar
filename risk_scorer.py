"""
Layer 3: Risk Scoring Engine
-----------------------------
Takes the output of CUAD's clause-extraction model (Layer 1: category +
extracted text span + model confidence) and produces a numeric risk score
and a Low/Medium/High level.

This is a transparent, rule-based scorer: score = base_severity (from the
taxonomy) + sum of keyword modifiers found in the clause text, scaled by
the model's extraction confidence. Being rule-based (rather than a black
box) is itself a deliberate explainability design choice, and every
component of the score is inspectable (see explainability.py).
"""

from dataclasses import dataclass, field
from typing import List

from risk_taxonomy import RISK_TAXONOMY, KEYWORD_MODIFIERS, get_risk_level


@dataclass
class ScoredClause:
    category: str
    clause_text: str
    confidence: float
    risk_type: str
    base_severity: float
    matched_keywords: List[str] = field(default_factory=list)
    keyword_bonus: float = 0.0
    raw_score: float = 0.0
    final_score: float = 0.0
    risk_level: str = "Low"


def score_clause(category: str, clause_text: str, confidence: float = 1.0) -> ScoredClause:
    """
    Score a single extracted clause.

    category:    one of the CUAD category names (e.g. "Uncapped Liability")
    clause_text: the extracted span/answer text from the CUAD model
    confidence:  the CUAD model's extraction confidence (0-1); low-confidence
                 extractions are down-weighted so weak detections don't get
                 flagged as confidently "High risk"
    """
    taxonomy_entry = RISK_TAXONOMY.get(category)
    if taxonomy_entry is None:
        # Category isn't in our risk-relevant taxonomy (e.g. "Parties",
        # "Agreement Date") -> not a risk clause, skip scoring.
        return ScoredClause(
            category=category, clause_text=clause_text, confidence=confidence,
            risk_type="N/A", base_severity=0, raw_score=0, final_score=0,
            risk_level="Not Applicable",
        )

    base = taxonomy_entry["base_severity"]
    risk_type = taxonomy_entry["risk_type"]

    text_lower = clause_text.lower()
    matched = [kw for kw in KEYWORD_MODIFIERS if kw in text_lower]
    bonus = sum(KEYWORD_MODIFIERS[kw] for kw in matched)

    raw_score = base + bonus
    # confidence weighting: a shaky extraction shouldn't produce a confident
    # high-risk flag. Confidence < 1.0 pulls the score toward a neutral 5.
    final_score = confidence * raw_score + (1 - confidence) * 5
    final_score = max(0, min(10, final_score))  # clamp to [0, 10]

    return ScoredClause(
        category=category,
        clause_text=clause_text,
        confidence=confidence,
        risk_type=risk_type,
        base_severity=base,
        matched_keywords=matched,
        keyword_bonus=bonus,
        raw_score=raw_score,
        final_score=round(final_score, 2),
        risk_level=get_risk_level(final_score),
    )


def score_contract(extractions: List[dict]) -> List[ScoredClause]:
    """
    extractions: list of dicts shaped like CUAD model output, e.g.
        {"category": "Uncapped Liability",
         "text": "...clause span...",
         "confidence": 0.87}
    Returns a list of ScoredClause, one per input extraction.
    """
    return [
        score_clause(e["category"], e["text"], e.get("confidence", 1.0))
        for e in extractions
    ]
