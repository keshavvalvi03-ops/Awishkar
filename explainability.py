"""
Layer 4: Explainability
-------------------------
Generates human-readable justifications and feature-attribution breakdowns
for scored contract clauses.
"""

from typing import List, Dict, Any
from risk_scorer import ScoredClause
from risk_taxonomy import KEYWORD_MODIFIERS


def generate_explanation(clause: ScoredClause) -> str:
    """
    Generates transparent, human-readable justification for the clause score.
    Preserves exact phrasing for verified categories.
    """
    if clause.risk_level == "Not Applicable":
        return f"'{clause.category}' is not treated as a risk-bearing clause category."

    reason_parts = [
        f"classified under {clause.risk_type} (base severity {clause.base_severity}/10)"
    ]

    if clause.matched_keywords:
        kw_list = ", ".join(f"'{k}'" for k in clause.matched_keywords)
        reason_parts.append(f"contains risk-modifying language: {kw_list}")

    if clause.confidence < 0.7:
        reason_parts.append(
            f"extraction confidence is only {clause.confidence:.0%}, so this "
            f"flag should be manually verified"
        )

    if clause.provisional:
        reason_parts.append("provisional baseline -- not expert-validated")

    return (
        f"Flagged as {clause.risk_level} risk (score {clause.final_score}/10). "
        f"This clause is {'; '.join(reason_parts)}."
    )


def attribution_breakdown(clause: ScoredClause) -> Dict[str, Any]:
    """
    Exact contribution of each factor to the final score.
    Rule-based and inspectable for explainable AI requirements.
    """
    if clause.risk_level == "Not Applicable":
        return {}

    confidence_adjustment = round(
        clause.final_score - clause.confidence * clause.raw_score, 2
    )

    kw_contribs = {}
    for kw in clause.matched_keywords:
        kw_contribs[kw] = KEYWORD_MODIFIERS.get(kw, 0)

    breakdown = {
        "category": clause.category,
        "base_severity_contribution": clause.base_severity,
        "keyword_contributions": kw_contribs,
        "keyword_total_contribution": clause.keyword_bonus,
        "raw_score_before_confidence": clause.raw_score,
        "confidence_weighting_adjustment": confidence_adjustment,
        "final_score": clause.final_score,
        "final_level": clause.risk_level,
    }

    if clause.provisional:
        breakdown["provisional_note"] = "Severity rating is a provisional heuristic not expert-validated."

    return breakdown


def build_report(scored_clauses: List[ScoredClause]) -> List[Dict[str, Any]]:
    """Combines explanation + attribution for every scored clause into one report."""
    report = []
    for c in scored_clauses:
        report.append({
            "category": c.category,
            "clause_text": c.clause_text,
            "risk_type": c.risk_type,
            "risk_level": c.risk_level,
            "score": c.final_score,
            "confidence": c.confidence,
            "explanation": generate_explanation(c),
            "attribution": attribution_breakdown(c),
        })
    return report
