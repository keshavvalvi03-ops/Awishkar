"""
Layer 6: Cross-Clause Interaction Risk + Confidence-Calibrated Aggregation
-----------------------------------------------------------------------------
None of the 4 comparison papers model how clauses interact -- every one of
them scores clauses independently and (at most) sums/averages them. A
contract with Uncapped Liability AND no Cap on Liability AND no Insurance
is not "three separate medium findings" -- it's one compounding financial
trap, and a lawyer would flag it as worse than the sum of its parts.

This also directly answers a gap named in Paper 4 (Sandhya B S) itself:
"confidence calibration is seldom addressed... Few frameworks achieve both
transparency and adaptability" (Section 2.9). The aggregate contract-level
score below is explicitly weighted by extraction confidence, not just
severity, so a document isn't rated "high risk" on the strength of shaky,
low-confidence clause detections.
"""

from dataclasses import dataclass
from typing import List, Dict
from risk_scorer import ScoredClause

# Each rule: which CUAD categories must ALL be present (or, for negative
# conditions, absent) for the interaction to fire, a severity bonus added
# to the contract-level score, and a plain-language explanation.
INTERACTION_RULES = [
    {
        "name": "Uncapped Financial Exposure",
        "requires_present": {"Uncapped Liability"},
        "requires_absent": {"Cap On Liability", "Insurance"},
        "bonus": 2.0,
        "message": ("Liability is uncapped and there is neither a liability cap nor an "
                    "insurance requirement to offset it -- financial exposure compounds "
                    "rather than being contained."),
    },
    {
        "name": "Exclusive Lock-In Trap",
        "requires_present": {"Exclusivity", "Renewal Term"},
        "requires_absent": {"Termination For Convenience"},
        "bonus": 1.5,
        "message": ("An exclusive dealing commitment auto-renews and there is no "
                     "termination-for-convenience clause -- the counterparty may be "
                     "locked into an exclusive arrangement with no easy exit."),
    },
    {
        "name": "Abrupt Walkaway Risk",
        "requires_present": {"Termination For Convenience"},
        "requires_absent": {"Post-Termination Services"},
        "bonus": 1.0,
        "message": ("Either party can terminate without cause, but no post-termination "
                     "obligations (wind-down, transition, hand-back) are defined -- "
                     "termination could leave the counterparty without support."),
    },
    {
        "name": "Unbounded IP Grant",
        "requires_present": {"Irrevocable Or Perpetual License", "Unlimited/All-You-Can-Eat-License"},
        "requires_absent": set(),
        "bonus": 1.5,
        "message": ("The license granted is both perpetual/irrevocable AND unlimited in "
                    "usage scope -- these two clauses compound into a permanent, "
                    "unrestricted grant that is very hard to claw back later."),
    },
    {
        "name": "Pricing Power Asymmetry",
        "requires_present": {"Most Favored Nation", "Price Restrictions"},
        "requires_absent": set(),
        "bonus": 1.0,
        "message": ("A Most Favored Nation clause combines with price restrictions -- "
                    "the counterparty's pricing flexibility is doubly constrained."),
    },
]


@dataclass
class InteractionFinding:
    name: str
    bonus: float
    message: str


def detect_interactions(scored_clauses: List[ScoredClause]) -> List[InteractionFinding]:
    present_categories = {c.category for c in scored_clauses if c.risk_level != "Not Applicable"}
    findings = []
    for rule in INTERACTION_RULES:
        present_ok = rule["requires_present"].issubset(present_categories)
        absent_ok = rule["requires_absent"].isdisjoint(present_categories)
        if present_ok and absent_ok:
            findings.append(InteractionFinding(
                name=rule["name"], bonus=rule["bonus"], message=rule["message"],
            ))
    return findings


def aggregate_contract_risk(scored_clauses: List[ScoredClause]) -> Dict:
    """
    Produces ONE contract-level risk score -- something none of the 4
    comparison papers output (they all stop at clause-level results).

    Method:
      1. base = confidence-weighted average of all applicable clause scores
         (a clause detected at 40% confidence contributes less to the
         contract-level score than one detected at 95% confidence --
         this is the confidence-calibration piece).
      2. + sum of triggered interaction-rule bonuses (Layer 6's core idea).
      3. clamped to [0, 10], mapped to a document risk level.
    """
    applicable = [c for c in scored_clauses if c.risk_level != "Not Applicable"]
    if not applicable:
        return {
            "contract_score": 0, "contract_level": "Low",
            "interactions": [], "average_confidence": 0,
            "note": "No risk-relevant clauses were detected.",
        }

    total_weight = sum(c.confidence for c in applicable)
    weighted_score = sum(c.final_score * c.confidence for c in applicable) / total_weight
    avg_confidence = total_weight / len(applicable)

    interactions = detect_interactions(applicable)
    interaction_bonus = sum(f.bonus for f in interactions)

    contract_score = min(10, round(weighted_score + interaction_bonus, 2))

    from risk_taxonomy import get_risk_level
    contract_level = get_risk_level(contract_score)

    note = None
    if avg_confidence < 0.6:
        note = (f"Average extraction confidence is only {avg_confidence:.0%} -- this "
                f"contract-level score should be treated as provisional pending manual review.")

    return {
        "contract_score": contract_score,
        "contract_level": contract_level,
        "base_weighted_score": round(weighted_score, 2),
        "interaction_bonus": interaction_bonus,
        "interactions": [
            {"name": f.name, "bonus": f.bonus, "message": f.message} for f in interactions
        ],
        "average_confidence": round(avg_confidence, 2),
        "note": note,
    }
