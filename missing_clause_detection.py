"""
Layer 5: Contract-Specific Missing Clause Detection
---------------------------------------------------
Detects absent contractual protections using both model-based gap signals
and heuristic keyword checks, parameterized by contract type.

TRANSPARENCY AND LEGAL LIMITATIONS:
- Missing clause detection does NOT prove that an agreement is defective or illegal.
- Relevance depends on the deal, leverage, jurisdiction, and contract type.
- A missing keyword match does NOT prove a clause is completely absent.
- A detected keyword does NOT prove a clause is legally adequate or enforceable.
- Clearly distinguishes: CUAD-based gaps, experimental keyword searches, and manual review.
"""

from dataclasses import dataclass
from typing import List, Dict, Optional, Any
from custom_taxonomy import normalize_category_name
from custom_detector import detect_clause_in_text
from contract_types import (
    get_contract_type,
    CONTRACT_TYPES,
    STATUS_DETECTED,
    STATUS_NOT_DETECTED,
    STATUS_NOT_APPLICABLE,
    STATUS_UNCERTAIN,
    RELEVANCE_EXPECTED,
    RELEVANCE_CONDITIONAL,
    RELEVANCE_OPTIONAL,
    METHOD_CUAD,
    METHOD_KEYWORD,
    METHOD_MANUAL,
    SUPPORT_CUAD,
    SUPPORT_KEYWORD,
    SUPPORT_MANUAL,
    ChecklistItem,
)

# Baseline CUAD categories considered essential for general commercial analysis
# (Preserved for 100% backward compatibility when no contract_type is specified)
ESSENTIAL_CUAD_CATEGORIES = {
    "Cap On Liability": "No cap on liability was found -- exposure may be unbounded.",
    "Governing Law": "No governing law clause was found -- jurisdiction for disputes is unclear.",
    "Termination For Convenience": "No termination-for-convenience clause was found -- exit may be difficult.",
    "Warranty Duration": "No warranty duration was specified.",
    "Insurance": "No insurance requirement was found.",
    "Audit Rights": "No audit rights clause was found.",
    "IP Ownership Assignment": "IP ownership on deliverables is not addressed.",
}

# Heuristic essentials outside CUAD's taxonomy
# (Preserved for 100% backward compatibility when no contract_type is specified)
HEURISTIC_ESSENTIAL_KEYWORDS = {
    "Confidentiality": ["confidential", "non-disclosure", "nda"],
    "Dispute Resolution": ["dispute resolution", "arbitration", "mediation", "jurisdiction of the courts"],
    "Force Majeure": ["force majeure", "act of god"],
    "Data Privacy": ["data privacy", "personal data", "gdpr", "dpdp", "data protection"],
}


@dataclass
class MissingClauseFinding:
    clause_name: str
    detection_method: str  # "cuad_model", "heuristic_keyword", "experimental_keyword", "manual_review"
    message: str
    status: str = STATUS_NOT_DETECTED
    relevance: str = RELEVANCE_EXPECTED
    reason: str = ""
    recommended_action: str = ""
    evidence: Optional[str] = None


def detect_cuad_gaps(extractions: List[Dict]) -> List[MissingClauseFinding]:
    """
    Flags baseline essential CUAD categories with no corresponding extraction.
    Preserves original Layer 5 signal logic.
    """
    found_categories = {normalize_category_name(e.get("category", "")) for e in extractions}
    findings = []
    for category, message in ESSENTIAL_CUAD_CATEGORIES.items():
        canonical = normalize_category_name(category)
        if canonical not in found_categories:
            findings.append(MissingClauseFinding(
                clause_name=category,
                detection_method="cuad_model",
                message=message,
                status=STATUS_NOT_DETECTED,
                relevance=RELEVANCE_EXPECTED,
                reason="General commercial protection expected in standard commercial contracting.",
                recommended_action=f"Review whether a {category} clause is needed for this agreement.",
            ))
    return findings


def detect_heuristic_gaps(raw_contract_text: Optional[str]) -> List[MissingClauseFinding]:
    """
    Checks for general commercial essentials outside CUAD using keyword scan.
    Skips if raw_contract_text is empty or not provided.
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
                status=STATUS_NOT_DETECTED,
                relevance=RELEVANCE_EXPECTED,
                reason=f"Standard protection for commercial operations; not detected in plain text scan.",
                recommended_action=f"Verify manually whether {clause_name} is covered in an unextracted section.",
            ))
    return findings


def evaluate_contract_checklist(contract_type_name: str,
                                extractions: List[Dict],
                                raw_contract_text: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Evaluates the complete contract-specific checklist for a given contract type.
    Returns status for EVERY checklist item (Detected, Not detected, Uncertain, etc.)
    with evidence snippets, relevance, detection method, and recommended action.
    """
    ct_def = get_contract_type(contract_type_name)
    if not ct_def:
        ct_def = CONTRACT_TYPES["general_business_agreement"]

    # Pre-index normalized extracted categories
    extraction_map = {}
    for e in extractions:
        c_norm = normalize_category_name(e.get("category", ""))
        extraction_map[c_norm] = e

    checklist_results = []

    for item in ct_def.checklist:
        c_norm = normalize_category_name(item.clause_name)
        status = STATUS_NOT_DETECTED
        detection_method = item.detection_method
        evidence = None
        message = ""

        # 1. Check extractions first
        if c_norm in extraction_map:
            ext = extraction_map[c_norm]
            conf = ext.get("confidence")
            evidence = ext.get("text", "")
            # Check confidence calibration
            if conf is not None and conf < 0.50:
                status = STATUS_UNCERTAIN
                detection_method = ext.get("detection_method", METHOD_CUAD)
                message = f"Detected in extractions but with low confidence ({conf:.0%}); manual verification recommended."
            else:
                status = STATUS_DETECTED
                detection_method = ext.get("detection_method", METHOD_CUAD)
                message = f"Clause detected in contract extractions."

        # 2. If not in extractions, check raw text using custom detector
        elif raw_contract_text:
            match_res = detect_clause_in_text(item.clause_name, raw_contract_text)
            if match_res:
                status = STATUS_DETECTED
                detection_method = METHOD_KEYWORD
                evidence = match_res.get("text")
                message = f"Detected via experimental keyword pattern matching ('{match_res.get('matched_text', '')}')."

        # 3. If still not detected, formulate clear contextual message
        if status == STATUS_NOT_DETECTED:
            if item.relevance == RELEVANCE_EXPECTED:
                message = f"Expected clause not detected: {item.reason}"
            elif item.relevance == RELEVANCE_CONDITIONAL:
                message = f"Conditional clause not detected: {item.reason}"
            else:
                message = f"Optional clause not detected: {item.reason}"

        checklist_results.append({
            "clause_name": item.clause_name,
            "status": status,
            "relevance": item.relevance,
            "reason": item.reason,
            "detection_method": detection_method,
            "support_status": item.support_status,
            "recommended_action": item.recommended_action,
            "evidence": evidence,
            "message": message,
        })

    return checklist_results


def detect_missing_clauses(extractions: List[Dict],
                           raw_contract_text: Optional[str] = None,
                           contract_type: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Main Layer 5 entry point.
    - If `contract_type` is None: Runs baseline general commercial missing clause checks
      (100% backward compatible with original Layer 5 findings and demo.py).
    - If `contract_type` is specified: Runs contract-specific checklist and returns
      findings for absent or uncertain clauses.
    """
    if contract_type is None:
        # Backward compatibility mode
        findings = detect_cuad_gaps(extractions) + detect_heuristic_gaps(raw_contract_text)
        return [
            {
                "clause_name": f.clause_name,
                "detection_method": f.detection_method,
                "message": f.message,
                "status": f.status,
                "relevance": f.relevance,
                "reason": f.reason,
                "recommended_action": f.recommended_action,
            }
            for f in findings
        ]

    # Contract-specific mode: evaluate against contract type checklist
    full_checklist = evaluate_contract_checklist(contract_type, extractions, raw_contract_text)
    # Return missing and uncertain items
    missing_findings = []
    for item in full_checklist:
        if item["status"] in (STATUS_NOT_DETECTED, STATUS_UNCERTAIN):
            missing_findings.append({
                "clause_name": item["clause_name"],
                "detection_method": item["detection_method"],
                "message": item["message"],
                "status": item["status"],
                "relevance": item["relevance"],
                "reason": item["reason"],
                "recommended_action": item["recommended_action"],
            })
    return missing_findings
