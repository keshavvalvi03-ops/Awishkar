"""
Layer 6: Cross-Clause Interaction Risk + Confidence-Calibrated Aggregation
-----------------------------------------------------------------------------
Identifies compounding risk interactions across multiple detected clauses,
and computes a confidence-calibrated contract-level risk score.

Bugs fixed:
- Handles empty input gracefully without missing contract_score fields (KeyError fix).
- Protects against ZeroDivisionError when all clause confidences are zero.
- Fixes Exclusive Lock-In logic: verifies whether renewal is actually automatic/evergreen
  rather than assuming any general renewal clause triggers lock-in.
- Prevents misleading interaction alerts when clauses are not detected.
"""

import re
from dataclasses import dataclass
from typing import List, Dict, Optional, Any, Set
from risk_scorer import ScoredClause
from custom_taxonomy import normalize_category_name


@dataclass
class InteractionFinding:
    name: str
    bonus: float
    message: str


def _is_automatic_renewal(clause: ScoredClause) -> bool:
    """
    Checks whether a Renewal Term clause specifically contains automatic
    or evergreen renewal language, rather than requiring mutual agreement.
    """
    if "automatically renew" in clause.matched_keywords:
        return True
    text = clause.clause_text.lower()
    auto_patterns = [
        r"\bautomatic(?:ally)?\s+renew\b",
        r"\bauto-renew\b",
        r"\bevergreen\b",
        r"\brenew(?:s)?\s+automatically\b",
        r"\bsuccessive\s+(?:one-year|annual|monthly|\d+-year)\s+terms?\s+unless\b",
    ]
    for pat in auto_patterns:
        if re.search(pat, text):
            return True
    return False


def detect_interactions(scored_clauses: List[ScoredClause]) -> List[InteractionFinding]:
    """
    Detects known compounding clause combinations with context verification.
    """
    # Index applicable clauses by canonical category
    clause_map: Dict[str, ScoredClause] = {}
    for c in scored_clauses:
        if c.risk_level != "Not Applicable":
            canonical = normalize_category_name(c.category)
            clause_map[canonical] = c

    present_categories = set(clause_map.keys())
    findings = []

    # 1. Uncapped Financial Exposure (+2.0)
    # Liability is uncapped, and neither a liability cap nor insurance exists to mitigate
    if "Uncapped Liability" in present_categories:
        if "Cap On Liability" not in present_categories and "Insurance" not in present_categories:
            findings.append(InteractionFinding(
                name="Uncapped Financial Exposure",
                bonus=2.0,
                message=(
                    "Liability is uncapped and there is neither a liability cap nor an "
                    "insurance requirement to offset it -- financial exposure compounds "
                    "rather than being contained."
                ),
            ))

    # 2. Exclusive Lock-In Trap (+1.5)
    # Exclusivity + auto-renewal, and no exit via termination for convenience.
    # Fixed: checks that renewal is genuinely automatic, not mutual agreement.
    if "Exclusivity" in present_categories and "Renewal Term" in present_categories:
        if "Termination For Convenience" not in present_categories:
            renewal_clause = clause_map["Renewal Term"]
            if _is_automatic_renewal(renewal_clause):
                findings.append(InteractionFinding(
                    name="Exclusive Lock-In Trap",
                    bonus=1.5,
                    message=(
                        "An exclusive dealing commitment auto-renews and there is no "
                        "termination-for-convenience clause -- the counterparty may be "
                        "locked into an exclusive arrangement with no easy exit."
                    ),
                ))

    # 3. Abrupt Walkaway Risk (+1.0)
    # Convenience termination exists, but no post-termination services/transition obligations
    if "Termination For Convenience" in present_categories:
        if "Post-Termination Services" not in present_categories:
            findings.append(InteractionFinding(
                name="Abrupt Walkaway Risk",
                bonus=1.0,
                message=(
                    "Either party can terminate without cause, but no post-termination "
                    "obligations (wind-down, transition, hand-back) are defined -- "
                    "termination could leave the counterparty without support."
                ),
            ))

    # 4. Unbounded IP Grant (+1.5)
    # Perpetual/irrevocable license combined with all-you-can-eat scope
    if ("Irrevocable Or Perpetual License" in present_categories and
            "Unlimited/All-You-Can-Eat-License" in present_categories):
        findings.append(InteractionFinding(
            name="Unbounded IP Grant",
            bonus=1.5,
            message=(
                "The license granted is both perpetual/irrevocable AND unlimited in "
                "usage scope -- these two clauses compound into a permanent, "
                "unrestricted grant that is very hard to claw back later."
            ),
        ))

    # 5. Pricing Power Asymmetry (+1.0)
    # MFN clause combined with price restrictions
    if "Most Favored Nation" in present_categories and "Price Restrictions" in present_categories:
        findings.append(InteractionFinding(
            name="Pricing Power Asymmetry",
            bonus=1.0,
            message=(
                "A Most Favored Nation clause combines with price restrictions -- "
                "the counterparty's pricing flexibility is doubly constrained."
            ),
        ))

    return findings


def aggregate_contract_risk(scored_clauses: List[ScoredClause]) -> Dict[str, Any]:
    """
    Computes a confidence-calibrated contract-level risk score.

    Method:
      1. Confidence-weighted average of applicable clause scores.
      2. Plus sum of triggered interaction-rule bonuses.
      3. Clamped to [0, 10] and mapped to Low/Medium/High.

    Safe against empty lists, missing fields, and zero-weight confidence division.
    """
    applicable = [c for c in scored_clauses if c.risk_level != "Not Applicable"]

    # Handle empty or zero-risk input gracefully with complete field structure
    if not applicable:
        return {
            "contract_score": 0.0,
            "contract_level": "Low",
            "base_weighted_score": 0.0,
            "interaction_bonus": 0.0,
            "interactions": [],
            "average_confidence": 0.0,
            "note": "No risk-relevant clauses were detected.",
        }

    total_weight = sum(c.confidence for c in applicable)
    if total_weight > 0:
        weighted_score = sum(c.final_score * c.confidence for c in applicable) / total_weight
        avg_confidence = total_weight / len(applicable)
    else:
        # Avoid ZeroDivisionError if all confidences are 0.0
        weighted_score = sum(c.final_score for c in applicable) / len(applicable)
        avg_confidence = 0.0

    interactions = detect_interactions(applicable)
    interaction_bonus = sum(f.bonus for f in interactions)

    contract_score = min(10.0, round(weighted_score + interaction_bonus, 2))

    from risk_taxonomy import get_risk_level
    contract_level = get_risk_level(contract_score)

    note = None
    if avg_confidence < 0.6:
        note = (
            f"Average extraction confidence is only {avg_confidence:.0%} -- this "
            f"contract-level score should be treated as provisional pending manual review."
        )

    return {
        "contract_score": contract_score,
        "contract_level": contract_level,
        "base_weighted_score": round(weighted_score, 2),
        "interaction_bonus": round(interaction_bonus, 2),
        "interactions": [
            {"name": f.name, "bonus": f.bonus, "message": f.message} for f in interactions
        ],
        "average_confidence": round(avg_confidence, 2),
        "note": note,
    }
