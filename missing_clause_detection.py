"""
Layer 5: Missing Clause Detection
-----------------------------------
None of the 4 comparison papers (Legalese Explainer, Dikmen et al.,
Anusha & Rani, Sandhya B S) check for ABSENT protections -- they all only
analyze clauses that are present in the contract. A contract missing a
liability cap or a termination clause is arguably riskier than a contract
with a mediocre one, but no per-clause scorer can ever surface that,
because there's no clause to score.

TWO DETECTION MECHANISMS, CLEARLY SEPARATED (important for honesty):

1. CUAD-CATEGORY GAPS (model-based, real Layer 1 signal):
   Your CUAD-fine-tuned model already computes this for free. When you
   ask it "Is there a cap on liability?" and it returns no answer above
   threshold, that IS a missing-clause signal -- Layer 1 just normally
   discards it. This module reports it instead of throwing it away.

2. HEURISTIC ESSENTIALS (regex-based, NOT from CUAD):
   Clauses like "Confidentiality", "Dispute Resolution", "Force Majeure",
   and "Data Privacy" are NOT among CUAD's 41 categories at all -- CUAD
   was never trained to detect them, so Layer 1 can say nothing about
   them. For these, a lightweight keyword search directly on the raw
   contract text is used instead. This is explicitly NOT machine-learned
   and should be described on your poster as a heuristic supplementary
   check, not a model prediction -- overclaiming this as "AI detection"
   would be inaccurate.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional

# Subset of CUAD's real 41 categories considered "essential protections" --
# a contract missing these is a meaningful finding, unlike categories such
# as "Affiliate License-Licensor" which simply may not apply to every deal.
ESSENTIAL_CUAD_CATEGORIES = {
    "Cap On Liability": "No cap on liability was found -- exposure may be unbounded.",
    "Governing Law": "No governing law clause was found -- jurisdiction for disputes is unclear.",
    "Termination For Convenience": "No termination-for-convenience clause was found -- exit may be difficult.",
    "Warranty Duration": "No warranty duration was specified.",
    "Insurance": "No insurance requirement was found.",
    "Audit Rights": "No audit rights clause was found.",
    "IP Ownership Assignment": "IP ownership on deliverables is not addressed.",
}

# Common contract essentials that are NOT part of CUAD's taxonomy at all.
# Detected via plain keyword search on the raw contract text, not the model.
HEURISTIC_ESSENTIAL_KEYWORDS = {
    "Confidentiality": ["confidential", "non-disclosure", "nda"],
    "Dispute Resolution": ["dispute resolution", "arbitration", "mediation", "jurisdiction of the courts"],
    "Force Majeure": ["force majeure", "act of god"],
    "Data Privacy": ["data privacy", "personal data", "gdpr", "dpdp", "data protection"],
}


@dataclass
class MissingClauseFinding:
    clause_name: str
    detection_method: str  # "cuad_model" or "heuristic_keyword"
    message: str


def detect_cuad_gaps(extractions: List[Dict]) -> List[MissingClauseFinding]:
    """
    extractions: the Layer-1 output list (same shape used by risk_scorer).
    Any essential CUAD category with no corresponding extraction (or only
    a low-confidence one already filtered out upstream) is flagged.
    """
    found_categories = {e["category"] for e in extractions}
    findings = []
    for category, message in ESSENTIAL_CUAD_CATEGORIES.items():
        if category not in found_categories:
            findings.append(MissingClauseFinding(
                clause_name=category,
                detection_method="cuad_model",
                message=message,
            ))
    return findings


def detect_heuristic_gaps(raw_contract_text: Optional[str]) -> List[MissingClauseFinding]:
    """
    raw_contract_text: the full contract text (not just extracted spans).
    If not supplied, this check is skipped entirely rather than guessed at.
    """
    if not raw_contract_text:
        return []

    text_lower = raw_contract_text.lower()
    findings = []
    for clause_name, keywords in HEURISTIC_ESSENTIAL_KEYWORDS.items():
        if not any(kw in text_lower for kw in keywords):
            findings.append(MissingClauseFinding(
                clause_name=clause_name,
                detection_method="heuristic_keyword",
                message=f"No '{clause_name}' language was found anywhere in the contract text "
                        f"(checked for: {', '.join(keywords)}).",
            ))
    return findings


def detect_missing_clauses(extractions: List[Dict],
                            raw_contract_text: Optional[str] = None) -> List[Dict]:
    """
    Combines both detection mechanisms into one report list. Each entry
    is tagged with its detection_method so the poster/report can be
    accurate about which findings are model-based vs. heuristic.
    """
    findings = detect_cuad_gaps(extractions) + detect_heuristic_gaps(raw_contract_text)
    return [
        {"clause_name": f.clause_name, "detection_method": f.detection_method, "message": f.message}
        for f in findings
    ]
