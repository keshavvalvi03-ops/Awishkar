"""
Custom Detector: Experimental Keyword and Pattern Clause Detection
-------------------------------------------------------------------
Provides lightweight regex-based detection for clause categories not covered
by CUAD, or when running offline without heavy transformer weights.

TRANSPARENCY AND LIMITATIONS DISCLAIMER:
- This is a HEURISTIC RULE ENGINE based on regex patterns with word boundaries.
- It is EXPLICITLY NOT a trained neural network or machine-learned AI model.
- It returns an EVIDENCE SNIPPET of the matched text.
- It does NOT invent pseudo-confidence scores (confidence is set to None).
- A missing match does NOT prove the clause is legally absent.
- A detected pattern does NOT prove the clause is legally adequate, enforceable, or favorable.
- All detections should be verified by legal counsel.
"""

import re
from typing import Dict, List, Optional, Any, Tuple
from custom_taxonomy import normalize_category_name

# Category -> List of regex patterns (compiled with re.IGNORECASE)
# Word boundaries \\b are strictly enforced to avoid substring false positives.
CLAUSE_PATTERNS: Dict[str, List[str]] = {
    # Commercial
    "Indemnity": [
        r"\b(?:indemnif(?:y|ies|ication)|hold\s+harmless|defend\s+and\s+indemnify)\b",
        r"\bagrees?\s+to\s+(?:defend,\s*)?indemnify\b",
    ],
    "Scope of Services": [
        r"\b(?:scope\s+of\s+(?:services|work)|statement\s+of\s+work|\bSOW\b|services?\s+to\s+be\s+performed|deliverables\s+described\s+in)\b",
        r"\b(?:contractor|vendor|service\s+provider)\s+shall\s+provide\s+the\s+following\s+services\b",
    ],
    "Payment Terms": [
        r"\b(?:payment\s+terms|invoic(?:ing|es?)|net\s+(?:15|30|45|60)\s+days|fees?\s+shall\s+be\s+paid|payable\s+within\s+\d+\s+days)\b",
        r"\b(?:consideration|remittance|payment\s+schedule)\b",
    ],
    "Late Fees": [
        r"\b(?:late\s+(?:fee|charge|penalty|payment)|interest\s+on\s+(?:late|overdue|delinquent)|past\s+due\s+balance|delinquent\s+amounts?)\b",
        r"\b\d+(?:\.\d+)?%\s+per\s+month\s+(?:on\s+overdue|interest)\b",
    ],
    "Termination For Cause": [
        r"\b(?:terminat(?:e|ion)\s+for\s+(?:cause|default|material\s+breach)|immediate(?:ly)?\s+terminat(?:e|ion)|in\s+the\s+event\s+of\s+(?:a\s+)?material\s+breach)\b",
        r"\bfail(?:ure|s)\s+to\s+cure\s+(?:such\s+)?breach\s+within\s+\d+\s+days\b",
    ],
    "Governing Law": [
        r"\b(?:governed\s+by(?:\s+and\s+construed\s+in\s+accordance\s+with)?|laws\s+of\s+(?:the\s+state\s+of|the\s+country\s+of)?|choice\s+of\s+law|applicable\s+law)\b",
        r"\bjurisdiction\s+of\s+the\s+courts\s+of\b",
    ],
    "Dispute Resolution": [
        r"\b(?:dispute\s+resolution|arbitrat(?:ion|or)|mediat(?:ion|or)|amicable\s+settlement|binding\s+arbitration)\b",
        r"\bdisputes?\s+arising\s+(?:under|out\s+of)\s+this\s+agreement\s+shall\s+be\s+(?:resolved|submitted|settled)\b",
    ],
    "Confidentiality": [
        r"\b(?:confidential\s+information|non-disclosure|keep\s+confidential|proprietary\s+information|confidentiality\s+obligations?)\b",
        r"\bshall\s+not\s+disclose\s+(?:any\s+)?confidential\b",
    ],
    "Warranties": [
        r"\b(?:warrants?\s+(?:that|and\s+represents)|representations?\s+and\s+warranties|express\s+warranty|as-is\s+basis|disclaims?\s+all\s+warranties)\b",
        r"\bwarrants?\s+that\s+the\s+(?:services|products?|software)\s+will\b",
    ],
    "Force Majeure": [
        r"\b(?:force\s+majeure|act(?:s)?\s+of\s+god|unforeseen\s+(?:circumstances|events)|beyond\s+(?:the\s+)?reasonable\s+control\s+of\s+(?:either|such)\s+party)\b",
        r"\bneither\s+party\s+shall\s+be\s+liable\s+for\s+(?:any\s+)?delay\s+or\s+failure.*?(?:acts\s+of\s+god|war|disaster)\b",
    ],
    "Data Privacy": [
        r"\b(?:data\s+privacy|personal\s+data|personally\s+identifiable\s+information|\bPII\b|\bGDPR\b|\bCCPA\b|\bDPDP\b|privacy\s+(?:laws|policy))\b",
        r"\bprocessing\s+of\s+personal\s+data\b",
    ],
    "Data Protection and Security": [
        r"\b(?:data\s+protection\s+and\s+security|data\s+security|information\s+security|cybersecurity|security\s+measures|technical\s+and\s+organizational\s+measures|data\s+breach)\b",
        r"\bsafeguard\s+(?:against\s+)?(?:unauthorized\s+access|data\s+loss)\b",
    ],
    "Entire Agreement": [
        r"\b(?:entire\s+agreement|complete\s+agreement|integration\s+clause|supersedes?\s+all\s+prior\s+(?:agreements|understandings|representations)|whole\s+agreement)\b",
    ],
    "Notice Requirements": [
        r"\b(?:notices?\s+(?:under\s+this\s+agreement|shall\s+be\s+in\s+writing)|written\s+notice|served\s+by\s+(?:certified\s+mail|email|courier)|notice\s+address)\b",
    ],
    "Assignment": [
        r"\b(?:neither\s+party\s+may\s+assign|assignment\s+and\s+delegation|transfer\s+(?:of\s+)?rights|successors\s+and\s+permitted\s+assigns|consent\s+to\s+assign)\b",
    ],
    "Non-Solicitation": [
        r"\b(?:non-solicit(?:ation)?|shall\s+not\s+solicit|not\s+entice\s+away|refrain\s+from\s+soliciting\s+(?:employees|customers|clients))\b",
    ],
    "Cap On Liability": [
        r"\b(?:cap\s+on\s+liability|limitation\s+of\s+liability|aggregate\s+liability\s+shall\s+(?:not\s+exceed|be\s+limited)|maximum\s+(?:cumulative\s+)?liability)\b",
        r"\bin\s+no\s+event\s+shall\s+(?:either\s+party's\s+)?liability\s+exceed\b",
    ],
    "Uncapped Liability": [
        r"\b(?:liability\s+shall\s+be\s+unlimited|without\s+limitation\s+(?:for|as\s+to)|uncapped\s+liability|no\s+limitation\s+shall\s+apply)\b",
    ],
    "Termination For Convenience": [
        r"\b(?:terminat(?:e|ion)\s+for\s+convenience|terminat(?:e|ion)\s+without\s+cause|terminate\s+at\s+any\s+time\s+(?:upon|with|without)\s+notice)\b",
        r"\bsole\s+discretion\s+to\s+terminate\b",
    ],

    # Software and IP (using canonical taxonomy categories)
    "IP Ownership Assignment": [
        r"\b(?:intellectual\s+property\s+rights|ownership\s+of\s+(?:ip|intellectual\s+property|deliverables|work\s+product)|work\s+(?:made\s+)?for\s+hire|sole\s+and\s+exclusive\s+property)\b",
        r"\b(?:hereby\s+assigns?|assignment\s+of\s+(?:inventions|intellectual\s+property|copyrights?)|transfers\s+and\s+assigns\s+all\s+right,\s*title)\b",
    ],
    "License Grant": [
        r"\b(?:grants?\s+(?:to\s+licensee\s+)?a\s+(?:non-exclusive|exclusive|limited|worldwide|revocable|irrevocable)?\s*licen[sc]e|licen[sc]e\s+grant)\b",
    ],
    "Licence Restrictions": [
        r"\b(?:licen[sc]e\s+restrictions?|shall\s+not\s+(?:decompile|disassemble|reverse\s+engineer)|prohibited\s+(?:from\s+)?sublicensing|restrictions\s+on\s+use)\b",
    ],
    "Royalties": [
        r"\b(?:royalt(?:y|ies)|royalty\s+(?:fee|rate|payment)|percentage\s+of\s+net\s+(?:sales|revenue))\b",
    ],
    "Licence Fees": [
        r"\b(?:licen[sc]e\s+fees?|subscription\s+fees?|software\s+fees?|annual\s+licen[sc]e\s+fee)\b",
    ],
    "Support and Maintenance": [
        r"\b(?:support\s+and\s+maintenance|technical\s+support|maintenance\s+services|bug\s+fixes|updates\s+and\s+upgrades|helpdesk\s+support)\b",
    ],
    "Service Levels": [
        r"\b(?:service\s+level\s+agreement|\bSLA\b|uptime\s+(?:commitment|guarantee)|service\s+credits?|monthly\s+uptime\s+percentage)\b",
        r"\b\d+(?:\.\d+)?%\s+uptime\b",
    ],
    "Delivery and Acceptance": [
        r"\b(?:acceptance\s+testing|acceptance\s+criteria|written\s+acceptance|rejection\s+of\s+deliverables|delivery\s+and\s+acceptance|deemed\s+accepted)\b",
    ],

    # Lease and Rental
    "Rent": [
        r"\b(?:monthly\s+rent|base\s+rent|rental\s+payments?|rent\s+shall\s+be\s+\$?\d+|payable\s+on\s+the\s+first\s+day\s+of\s+each\s+month)\b",
    ],
    "Security Deposit": [
        r"\b(?:security\s+deposit|damage\s+deposit|deposit\s+amount|refund\s+of\s+security\s+deposit)\b",
    ],
    "Property Maintenance": [
        r"\b(?:maintenance\s+and\s+repairs?|tenant\s+shall\s+maintain|landlord\s+shall\s+repair|keep\s+in\s+good\s+repair|structural\s+repairs)\b",
    ],
    "Landlord and Tenant Obligations": [
        r"\b(?:tenant\s+covenants|landlord\s+covenants|quiet\s+enjoyment|use\s+of\s+premises|rules\s+and\s+regulations\s+of\s+the\s+building)\b",
    ],
    "Lease Termination": [
        r"\b(?:termination\s+of\s+lease|surrender\s+(?:of\s+)?premises|holdover\s+tenant|forfeiture\s+of\s+lease|vacate\s+the\s+premises)\b",
    ],

    # Employment
    "Salary and Compensation": [
        r"\b(?:base\s+salary|annual\s+salary|hourly\s+rate|compensation\s+shall\s+be|payroll|wages?\s+paid\s+(?:bi-weekly|monthly|semi-monthly))\b",
    ],
    "Benefits": [
        r"\b(?:employee\s+benefits|health\s+insurance|paid\s+time\s+off|\bPTO\b|retirement\s+plan|\b401\(?k\)?\b|vacation\s+days|sick\s+leave)\b",
    ],
    "Working Conditions": [
        r"\b(?:hours\s+of\s+work|work\s+schedule|remote\s+work|hybrid\s+work|working\s+hours|overtime\s+policy)\b",
    ],
    "Employment Termination": [
        r"\b(?:employment\s+at-will|at-will\s+employment|termination\s+of\s+employment|severance\s+pay|resignation\s+notice|grounds\s+for\s+dismissal)\b",
    ],

    # Partnership
    "Capital Contributions": [
        r"\b(?:capital\s+contributions?|initial\s+capital|capital\s+calls?|capital\s+account|partner\s+shall\s+contribute)\b",
    ],
    "Profit and Loss Sharing": [
        r"\b(?:profit\s+and\s+loss\s+sharing|allocation\s+of\s+profits?|net\s+losses?\s+shall\s+be\s+shared|distribution\s+of\s+profits|p&l\s+distribution)\b",
    ],
    "Partner Responsibilities": [
        r"\b(?:management\s+of\s+the\s+partnership|partner\s+responsibilities|voting\s+rights\s+of\s+partners|authority\s+to\s+bind|fiduciary\s+duty)\b",
    ],
    "Partner Exit and Dissolution": [
        r"\b(?:dissolution\s+of\s+(?:the\s+)?partnership|withdrawal\s+of\s+(?:a\s+)?partner|buyout\s+of\s+partner|winding\s+up|liquidation\s+of\s+partnership)\b",
    ],

    # M&A
    "Representations and Warranties": [
        r"\b(?:representations\s+and\s+warranties\s+of\s+seller|reps\s+and\s+warranties|material\s+adverse\s+effect|\bMAE\b|title\s+to\s+assets)\b",
    ],
    "Purchase Price": [
        r"\b(?:purchase\s+price|purchase\s+consideration|aggregate\s+consideration|earnout|closing\s+cash|working\s+capital\s+adjustment)\b",
    ],
    "Closing Conditions": [
        r"\b(?:conditions\s+precedent|conditions\s+to\s+closing|closing\s+deliverables|satisfaction\s+of\s+conditions|regulatory\s+clearance)\b",
    ],
    "Post-Closing Obligations": [
        r"\b(?:post-closing\s+covenants|post-closing\s+obligations|transition\s+services|indemnification\s+survival\s+period|post-closing\s+adjustment)\b",
    ],

    # Vendor and Supply
    "Product Specifications and Quality": [
        r"\b(?:product\s+specifications|conformance\s+to\s+specifications|quality\s+standards|manufacturing\s+standards|defective\s+products)\b",
    ],
    "Inspection and Acceptance": [
        r"\b(?:incoming\s+inspection|right\s+to\s+inspect\s+goods|rejection\s+of\s+defective|non-conforming\s+goods|notice\s+of\s+defect)\b",
    ],
    "Delivery Obligations": [
        r"\b(?:delivery\s+schedule|shipping\s+terms|\bIncoterms\b|\bFOB\b|\bDDP\b|\bCIF\b|lead\s+times|risk\s+of\s+loss\s+shall\s+pass)\b",
    ],
    "Remedies for Non-Performance": [
        r"\b(?:remedies\s+for\s+breach|remedies\s+for\s+non-performance|cover\s+damages|repair\s+or\s+replacement\s+of\s+defective|service\s+failure\s+credits)\b",
    ],
}


def _extract_snippet(text: str, match_start: int, match_end: int, window: int = 80) -> str:
    """Extracts a readable context snippet around a match, snapped to word boundaries."""
    start = max(0, match_start - window)
    end = min(len(text), match_end + window)

    if start > 0:
        prev_space = text.rfind(" ", 0, start)
        if prev_space != -1 and (start - prev_space) < 20:
            start = prev_space + 1
    if end < len(text):
        next_space = text.find(" ", end)
        if next_space != -1 and (next_space - end) < 20:
            end = next_space

    snippet = text[start:end].strip()
    cleaned = re.sub(r"\s+", " ", snippet)
    if start > 0:
        cleaned = "..." + cleaned
    if end < len(text):
        cleaned = cleaned + "..."
    return cleaned


def detect_clause_in_text(category_name: str, raw_text: Optional[str]) -> Optional[Dict[str, Any]]:
    """
    Scans raw text for patterns corresponding to category_name.
    Returns detection dictionary or None if no match.
    """
    if not raw_text or not raw_text.strip():
        return None

    canonical = normalize_category_name(category_name)
    patterns = CLAUSE_PATTERNS.get(canonical, [])
    if not patterns:
        return None

    for pattern_str in patterns:
        match = re.search(pattern_str, raw_text, re.IGNORECASE)
        if match:
            snippet = _extract_snippet(raw_text, match.start(), match.end())
            return {
                "category": canonical,
                "text": snippet,
                "confidence": None,  # Transparently uncalibrated: heuristic, not neural
                "detection_method": "experimental_keyword",
                "matched_pattern": pattern_str,
                "matched_text": match.group(0),
                "is_heuristic": True,
                "provisional": True,
            }
    return None


def scan_all_clauses(raw_text: Optional[str],
                     target_categories: Optional[List[str]] = None) -> List[Dict[str, Any]]:
    """
    Scans text across all or specified target categories.
    Returns list of detected clause records with evidence snippets.
    """
    if not raw_text or not raw_text.strip():
        return []

    cats_to_check = target_categories if target_categories else list(CLAUSE_PATTERNS.keys())
    detections = []
    seen_categories = set()

    for cat in cats_to_check:
        canonical = normalize_category_name(cat)
        if canonical in seen_categories:
            continue
        res = detect_clause_in_text(canonical, raw_text)
        if res:
            detections.append(res)
            seen_categories.add(canonical)

    return detections
