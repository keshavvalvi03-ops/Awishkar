"""
Layer 4: Explainability
-------------------------
CUAD already gives you evidence highlighting for free (the extracted span
IS the evidence). What's missing — and what your topic explicitly promises
— is a human-readable REASON, plus a transparent breakdown of what drove
the risk score.

Two things are produced per clause:
  1. A natural-language justification string (for the end user).
  2. A feature-attribution breakdown (for the "explainable AI" claim) —
     since the scorer is rule-based and fully transparent, the attribution
     is exact rather than approximate (unlike SHAP/LIME on a black-box
     model, which only estimate contributions).
"""

from risk_scorer import ScoredClause


def generate_explanation(clause: ScoredClause) -> str:
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

    return (
        f"Flagged as {clause.risk_level} risk (score {clause.final_score}/10). "
        f"This clause is {'; '.join(reason_parts)}."
    )


def attribution_breakdown(clause: ScoredClause) -> dict:
    """
    Exact contribution of each factor to the final score. This is the
    'explainable AI' artifact for your poster/report — every point in the
    final score can be traced to a specific cause.
    """
    if clause.risk_level == "Not Applicable":
        return {}

    confidence_adjustment = round(
        clause.final_score - clause.confidence * clause.raw_score, 2
    )
    return {
        "category": clause.category,
        "base_severity_contribution": clause.base_severity,
        "keyword_contributions": {
            kw: __import__("risk_taxonomy").KEYWORD_MODIFIERS[kw]
            for kw in clause.matched_keywords
        },
        "keyword_total_contribution": clause.keyword_bonus,
        "raw_score_before_confidence": clause.raw_score,
        "confidence_weighting_adjustment": confidence_adjustment,
        "final_score": clause.final_score,
        "final_level": clause.risk_level,
    }


def build_report(scored_clauses):
    """Combine explanation + attribution for every scored clause into one report."""
    report = []
    for c in scored_clauses:
        report.append({
            "category": c.category,
            "clause_text": c.clause_text,
            "risk_type": c.risk_type,
            "risk_level": c.risk_level,
            "score": c.final_score,
            "explanation": generate_explanation(c),
            "attribution": attribution_breakdown(c),
        })
    return report
