"""
Custom and Extended Clause Risk Taxonomy
-----------------------------------------
Extends the original CUAD-based taxonomy with additional commercial, software/IT,
employment, lease, partnership, M&A, and vendor clause categories required for
multi-contract type risk analysis.

REUSES EXISTING CATEGORIES:
Where CUAD already provides a category (e.g. Cap On Liability, License Grant,
IP Ownership Assignment, Joint IP Ownership, Source Code Escrow, Insurance,
Warranty Duration, Non-Compete, Termination For Convenience, Change Of Control),
aliases are normalized to the existing canonical category rather than creating duplicates.

IMPORTANT NOTE ON SEVERITY RATINGS:
Provisional severity ratings in this module are preliminary heuristic baselines
established for commercial review workflows and have NOT been validated by an
expert panel of legal practitioners unless explicitly marked 'expert_validated: True'.
They should be calibrated against specific jurisdictional and deal-specific contexts.
"""

import re
from typing import Dict, List, Optional, Any
from risk_taxonomy import RISK_TAXONOMY

# Extended clause categories mapping (only non-duplicate new categories)
CUSTOM_TAXONOMY: Dict[str, Dict[str, Any]] = {
    # =========================================================================
    # GENERAL COMMERCIAL CATEGORIES
    # =========================================================================
    "Indemnity": {
        "risk_type": "Financial Risk",
        "base_severity": 7,
        "provisional": True,
        "expert_validated": False,
        "source": "EXTENDED_COMMERCIAL",
        "description": "Obligation to defend, hold harmless, and compensate the counterparty for third-party claims or specified losses.",
        "detection_method": "experimental_keyword",
        "cuad_question": "Does the clause require a party to indemnify, defend, or hold harmless the other party against specified claims or liabilities?",
        "aliases": [
            "indemnity", "indemnification", "indemnify", "hold harmless",
            "defend and indemnify", "indemnities"
        ],
    },
    "Scope of Services": {
        "risk_type": "Operational Risk",
        "base_severity": 3,
        "provisional": True,
        "expert_validated": False,
        "source": "EXTENDED_COMMERCIAL",
        "description": "Defines the deliverables, work tasks, and performance expectations. Vague scopes increase dispute exposure.",
        "detection_method": "experimental_keyword",
        "cuad_question": "Does the clause define the scope of services, work duties, statement of work, or deliverables?",
        "aliases": [
            "scope of services", "scope of work", "statement of work", "sow",
            "services description", "deliverables", "work scope"
        ],
    },
    "Payment Terms": {
        "risk_type": "Commercial Risk",
        "base_severity": 4,
        "provisional": True,
        "expert_validated": False,
        "source": "EXTENDED_COMMERCIAL",
        "description": "Payment milestones, invoicing schedule, net payment days, and billing procedures.",
        "detection_method": "experimental_keyword",
        "cuad_question": "What are the payment terms, invoicing schedules, net payment days, or fee amounts under the contract?",
        "aliases": [
            "payment terms", "payment", "fees and payment", "invoicing",
            "payment schedule", "billing terms", "remittance"
        ],
    },
    "Late Fees": {
        "risk_type": "Financial Risk",
        "base_severity": 4,
        "provisional": True,
        "expert_validated": False,
        "source": "EXTENDED_COMMERCIAL",
        "description": "Interest charges or statutory penalties on overdue payments.",
        "detection_method": "experimental_keyword",
        "cuad_question": "Does the clause specify late fees, interest, or penalties on overdue payments?",
        "aliases": [
            "late fees", "interest on late payment", "late payment fee",
            "overdue interest", "late payment penalty", "delinquent account"
        ],
    },
    "Termination For Cause": {
        "risk_type": "Termination Risk",
        "base_severity": 4,
        "provisional": True,
        "expert_validated": False,
        "source": "EXTENDED_COMMERCIAL",
        "description": "Right to cancel the agreement upon material breach, insolvency, or failure to cure within a notice period.",
        "detection_method": "experimental_keyword",
        "cuad_question": "Does the clause specify grounds for terminating the agreement for cause, default, or material breach?",
        "aliases": [
            "termination for cause", "termination for default", "termination for breach",
            "material breach termination", "immediate termination"
        ],
    },
    "Governing Law": {
        "risk_type": "Legal/Compliance Risk",
        "base_severity": 3,
        "provisional": True,
        "expert_validated": False,
        "source": "CUAD_CATEGORY",
        "description": "Specifies which jurisdiction's statutory and substantive laws interpret the contract.",
        "detection_method": "cuad_model",
        "cuad_question": "Which state/country's law governs the interpretation of the contract?",
        "aliases": [
            "governing law", "choice of law", "applicable law", "governing legislation",
            "jurisdiction and governing law"
        ],
    },
    "Dispute Resolution": {
        "risk_type": "Legal/Compliance Risk",
        "base_severity": 4,
        "provisional": True,
        "expert_validated": False,
        "source": "EXTENDED_COMMERCIAL",
        "description": "Mandatory process for disputes: escalation, mediation, binding arbitration, or exclusive court jurisdiction.",
        "detection_method": "experimental_keyword",
        "cuad_question": "Does the clause specify dispute resolution mechanisms such as arbitration, mediation, or court jurisdiction?",
        "aliases": [
            "dispute resolution", "arbitration", "mediation", "resolution of disputes",
            "dispute escalation", "jurisdiction of courts", "litigation"
        ],
    },
    "Confidentiality": {
        "risk_type": "Commercial Risk",
        "base_severity": 4,
        "provisional": True,
        "expert_validated": False,
        "source": "EXTENDED_COMMERCIAL",
        "description": "Restricts disclosure and unauthorized use of non-public commercial and technical information.",
        "detection_method": "experimental_keyword",
        "cuad_question": "Does the clause restrict the disclosure or use of confidential or proprietary information?",
        "aliases": [
            "confidentiality", "confidential information", "non-disclosure", "nda",
            "proprietary information", "protection of confidential information"
        ],
    },
    "Warranties": {
        "risk_type": "Operational Risk",
        "base_severity": 4,
        "provisional": True,
        "expert_validated": False,
        "source": "EXTENDED_COMMERCIAL",
        "description": "Express promises regarding standard of performance, merchantability, or freedom from defects.",
        "detection_method": "experimental_keyword",
        "cuad_question": "Does the clause contain warranties, express representations of performance, or warranty disclaimers?",
        "aliases": [
            "warranties", "warranty", "representations and warranties", "express warranties",
            "performance warranty", "limited warranty"
        ],
    },
    "Force Majeure": {
        "risk_type": "Operational Risk",
        "base_severity": 3,
        "provisional": True,
        "expert_validated": False,
        "source": "EXTENDED_COMMERCIAL",
        "description": "Suspends performance obligations due to unforeseeable events beyond reasonable control (natural disasters, war, embargoes).",
        "detection_method": "experimental_keyword",
        "cuad_question": "Does the clause excuse performance due to force majeure, acts of God, or events beyond reasonable control?",
        "aliases": [
            "force majeure", "act of god", "acts of god", "unforeseen events",
            "excused performance"
        ],
    },
    "Data Privacy": {
        "risk_type": "Legal/Compliance Risk",
        "base_severity": 6,
        "provisional": True,
        "expert_validated": False,
        "source": "EXTENDED_COMMERCIAL",
        "description": "Compliance with personal data protection laws (GDPR, CCPA/CPRA, DPDP) and privacy rights.",
        "detection_method": "experimental_keyword",
        "cuad_question": "Does the clause address data privacy, processing of personal data, GDPR, or privacy compliance?",
        "aliases": [
            "data privacy", "personal data", "gdpr", "dpdp", "privacy compliance",
            "processing of personal data"
        ],
    },
    "Data Protection and Security": {
        "risk_type": "Legal/Compliance Risk",
        "base_severity": 6,
        "provisional": True,
        "expert_validated": False,
        "source": "EXTENDED_COMMERCIAL",
        "description": "Technical and organizational security measures to protect confidential or customer data against breaches.",
        "detection_method": "experimental_keyword",
        "cuad_question": "Does the clause mandate information security measures, encryption, cybersecurity, or data breach notification?",
        "aliases": [
            "data protection and security", "data security", "information security",
            "cybersecurity", "security measures", "technical and organizational measures"
        ],
    },
    "Entire Agreement": {
        "risk_type": "Legal/Compliance Risk",
        "base_severity": 2,
        "provisional": True,
        "expert_validated": False,
        "source": "EXTENDED_COMMERCIAL",
        "description": "Merger/integration clause stating that the written document supersedes all prior agreements and understandings.",
        "detection_method": "experimental_keyword",
        "cuad_question": "Does the clause state that the contract constitutes the entire agreement superseding prior understandings?",
        "aliases": [
            "entire agreement", "integration clause", "merger clause", "complete agreement",
            "whole agreement"
        ],
    },
    "Notice Requirements": {
        "risk_type": "Legal/Compliance Risk",
        "base_severity": 2,
        "provisional": True,
        "expert_validated": False,
        "source": "EXTENDED_COMMERCIAL",
        "description": "Required methods (certified mail, email), timing, and addresses for serving legal notices.",
        "detection_method": "experimental_keyword",
        "cuad_question": "Does the clause specify how formal written notices must be served under the contract?",
        "aliases": [
            "notice requirements", "notices", "giving of notice", "notice procedure",
            "formal notice"
        ],
    },
    "Assignment": {
        "risk_type": "Legal/Compliance Risk",
        "base_severity": 4,
        "provisional": True,
        "expert_validated": False,
        "source": "EXTENDED_COMMERCIAL",
        "description": "Governs whether a party may transfer its contractual rights or delegate obligations to a third party.",
        "detection_method": "experimental_keyword",
        "cuad_question": "Does the clause govern or restrict assignment of rights or delegation of duties?",
        "aliases": [
            "assignment", "transfer of rights", "assignment and delegation",
            "subcontracting and assignment", "successors and assigns"
        ],
    },
    "Non-Solicitation": {
        "risk_type": "Restrictive Covenant Risk",
        "base_severity": 5,
        "provisional": True,
        "expert_validated": False,
        "source": "EXTENDED_COMMERCIAL",
        "description": "General restriction against soliciting customers, clients, contractors, or staff of the counterparty.",
        "detection_method": "experimental_keyword",
        "cuad_question": "Does the clause restrict a party from soliciting customers, clients, or personnel of the counterparty?",
        "aliases": [
            "non-solicitation", "no-solicit", "non solicitation", "solicitation restriction",
            "customer non-solicit", "employee non-solicit"
        ],
    },

    # =========================================================================
    # SOFTWARE AND INTELLECTUAL PROPERTY CATEGORIES
    # (Note: IP Ownership and IP Assignment normalize to CUAD's IP Ownership Assignment;
    # Licence Grant normalizes to License Grant)
    # =========================================================================
    "Licence Restrictions": {
        "risk_type": "IP Risk",
        "base_severity": 5,
        "provisional": True,
        "expert_validated": False,
        "source": "EXTENDED_IP",
        "description": "Limitations on licensed software usage, prohibiting reverse engineering, decompilation, or sublicensing.",
        "detection_method": "experimental_keyword",
        "cuad_question": "Does the clause impose restrictions on the software license such as prohibiting reverse engineering?",
        "aliases": [
            "licence restrictions", "license restrictions", "restrictions on use",
            "prohibited uses", "use restrictions", "scope of license restrictions"
        ],
    },
    "Royalties": {
        "risk_type": "Financial Risk",
        "base_severity": 5,
        "provisional": True,
        "expert_validated": False,
        "source": "EXTENDED_IP",
        "description": "Ongoing usage-based or sales-based payments calculated as percentages or per-unit fees.",
        "detection_method": "experimental_keyword",
        "cuad_question": "Does the clause specify royalty rates, calculations, or payments for licensed property?",
        "aliases": [
            "royalties", "royalty", "royalty payments", "royalty fees", "royalty rate"
        ],
    },
    "Licence Fees": {
        "risk_type": "Commercial Risk",
        "base_severity": 4,
        "provisional": True,
        "expert_validated": False,
        "source": "EXTENDED_IP",
        "description": "Fixed or recurring subscription/license charges for authorized software or technology access.",
        "detection_method": "experimental_keyword",
        "cuad_question": "Does the clause specify license fees, subscription charges, or upfront licensing payments?",
        "aliases": [
            "licence fees", "license fees", "software fees", "subscription fees",
            "licensing fee"
        ],
    },
    "Support and Maintenance": {
        "risk_type": "Operational Risk",
        "base_severity": 3,
        "provisional": True,
        "expert_validated": False,
        "source": "EXTENDED_IP",
        "description": "Vendor commitments for technical assistance, error corrections, bug fixes, updates, and releases.",
        "detection_method": "experimental_keyword",
        "cuad_question": "Does the clause require technical support, maintenance services, bug fixes, or software updates?",
        "aliases": [
            "support and maintenance", "technical support", "maintenance and support",
            "software maintenance", "maintenance services", "updates and support"
        ],
    },
    "Service Levels": {
        "risk_type": "Operational Risk",
        "base_severity": 5,
        "provisional": True,
        "expert_validated": False,
        "source": "EXTENDED_IP",
        "description": "Service Level Agreement (SLA) metrics including uptime percentages, response times, and service credits.",
        "detection_method": "experimental_keyword",
        "cuad_question": "Does the clause define service levels, uptime guarantees, response times, or SLA credits?",
        "aliases": [
            "service levels", "sla", "service level agreement", "uptime commitment",
            "availability guarantee", "service level credits"
        ],
    },
    "Delivery and Acceptance": {
        "risk_type": "Operational Risk",
        "base_severity": 4,
        "provisional": True,
        "expert_validated": False,
        "source": "EXTENDED_IP",
        "description": "Procedures, timelines, and objective testing criteria for formal acceptance or rejection of deliverables.",
        "detection_method": "experimental_keyword",
        "cuad_question": "Does the clause specify delivery timelines and testing or acceptance procedures for deliverables?",
        "aliases": [
            "delivery and acceptance", "acceptance testing", "acceptance criteria",
            "inspection and acceptance of deliverables", "rejection of deliverables"
        ],
    },

    # =========================================================================
    # LEASE / RENTAL CATEGORIES
    # =========================================================================
    "Rent": {
        "risk_type": "Financial Risk",
        "base_severity": 5,
        "provisional": True,
        "expert_validated": False,
        "source": "EXTENDED_REAL_ESTATE",
        "description": "Base periodic rental amount, escalation clauses, and payment due dates.",
        "detection_method": "experimental_keyword",
        "cuad_question": "Does the clause specify rent, periodic rental amounts, or rent escalation?",
        "aliases": [
            "rent", "rental payment", "base rent", "monthly rent", "lease payments",
            "rent escalation"
        ],
    },
    "Security Deposit": {
        "risk_type": "Financial Risk",
        "base_severity": 4,
        "provisional": True,
        "expert_validated": False,
        "source": "EXTENDED_REAL_ESTATE",
        "description": "Upfront refundable deposit held against property damage, default, or unpaid rent.",
        "detection_method": "experimental_keyword",
        "cuad_question": "Does the clause require a security deposit or damage deposit?",
        "aliases": [
            "security deposit", "rental deposit", "damage deposit", "deposit refund",
            "holding deposit"
        ],
    },
    "Property Maintenance": {
        "risk_type": "Operational Risk",
        "base_severity": 4,
        "provisional": True,
        "expert_validated": False,
        "source": "EXTENDED_REAL_ESTATE",
        "description": "Allocation of repair, maintenance, and structural upkeep obligations between landlord and tenant.",
        "detection_method": "experimental_keyword",
        "cuad_question": "Does the clause allocate repair and maintenance duties for the leased property?",
        "aliases": [
            "property maintenance", "premises repair", "repairs and maintenance",
            "upkeep of premises", "landlord repairs", "tenant repairs"
        ],
    },
    "Landlord and Tenant Obligations": {
        "risk_type": "Legal/Compliance Risk",
        "base_severity": 4,
        "provisional": True,
        "expert_validated": False,
        "source": "EXTENDED_REAL_ESTATE",
        "description": "General duties regarding permitted premises use, quiet enjoyment, statutory compliance, and alterations.",
        "detection_method": "experimental_keyword",
        "cuad_question": "Does the clause outline the obligations of landlord or tenant regarding use of premises or quiet enjoyment?",
        "aliases": [
            "landlord and tenant obligations", "tenant covenants", "landlord obligations",
            "permitted use", "rules and regulations", "quiet enjoyment"
        ],
    },
    "Lease Termination": {
        "risk_type": "Termination Risk",
        "base_severity": 5,
        "provisional": True,
        "expert_validated": False,
        "source": "EXTENDED_REAL_ESTATE",
        "description": "Conditions for ending the lease, surrender of premises, holdover penalties, and forfeiture.",
        "detection_method": "experimental_keyword",
        "cuad_question": "Does the clause govern lease termination, surrender of premises, or holdover tenancy?",
        "aliases": [
            "lease termination", "termination of lease", "surrender of premises",
            "lease forfeiture", "holdover tenancy", "end of tenancy"
        ],
    },

    # =========================================================================
    # EMPLOYMENT CATEGORIES
    # =========================================================================
    "Salary and Compensation": {
        "risk_type": "Employment Risk",
        "base_severity": 4,
        "provisional": True,
        "expert_validated": False,
        "source": "EXTENDED_EMPLOYMENT",
        "description": "Base salary, hourly rate, overtime eligibility, bonuses, commissions, and payroll frequency.",
        "detection_method": "experimental_keyword",
        "cuad_question": "Does the clause specify employee salary, base wage, or compensation structure?",
        "aliases": [
            "salary and compensation", "salary", "base salary", "compensation",
            "remuneration", "wages", "employee compensation", "bonus structure"
        ],
    },
    "Benefits": {
        "risk_type": "Employment Risk",
        "base_severity": 3,
        "provisional": True,
        "expert_validated": False,
        "source": "EXTENDED_EMPLOYMENT",
        "description": "Health insurance, retirement plan, paid time off (PTO), sick leave, and fringe benefits.",
        "detection_method": "experimental_keyword",
        "cuad_question": "Does the clause detail employee benefits such as healthcare, paid time off, or retirement plans?",
        "aliases": [
            "benefits", "employee benefits", "paid time off", "pto", "vacation policy",
            "health insurance benefit", "pension and benefits"
        ],
    },
    "Working Conditions": {
        "risk_type": "Employment Risk",
        "base_severity": 3,
        "provisional": True,
        "expert_validated": False,
        "source": "EXTENDED_EMPLOYMENT",
        "description": "Work hours, remote/hybrid arrangements, workplace safety, travel expectations, and policies.",
        "detection_method": "experimental_keyword",
        "cuad_question": "Does the clause specify working hours, work location, remote work policies, or working conditions?",
        "aliases": [
            "working conditions", "hours of work", "work schedule", "working hours",
            "remote work policy", "workplace health and safety"
        ],
    },
    "Employment Termination": {
        "risk_type": "Termination Risk",
        "base_severity": 6,
        "provisional": True,
        "expert_validated": False,
        "source": "EXTENDED_EMPLOYMENT",
        "description": "At-will employment terms, notice periods, severance pay, termination for misconduct, and exit procedures.",
        "detection_method": "experimental_keyword",
        "cuad_question": "Does the clause specify grounds or notice requirements for termination of employment or severance?",
        "aliases": [
            "employment termination", "termination of employment", "severance",
            "dismissal", "resignation notice", "severance pay", "at-will employment"
        ],
    },

    # =========================================================================
    # PARTNERSHIP CATEGORIES
    # =========================================================================
    "Capital Contributions": {
        "risk_type": "Financial Risk",
        "base_severity": 6,
        "provisional": True,
        "expert_validated": False,
        "source": "EXTENDED_CORPORATE",
        "description": "Initial capital invested, capital accounts, mandatory future capital calls, and failure to contribute penalties.",
        "detection_method": "experimental_keyword",
        "cuad_question": "Does the clause detail capital contributions, capital calls, or capital accounts of partners?",
        "aliases": [
            "capital contributions", "initial capital", "capital calls", "capital account",
            "partner contribution", "equity contribution"
        ],
    },
    "Profit and Loss Sharing": {
        "risk_type": "Financial Risk",
        "base_severity": 5,
        "provisional": True,
        "expert_validated": False,
        "source": "EXTENDED_CORPORATE",
        "description": "Ratios and timing for allocating partnership net profits, losses, and cash distributions.",
        "detection_method": "experimental_keyword",
        "cuad_question": "Does the clause specify profit and loss allocation ratios or distribution schedules for partners?",
        "aliases": [
            "profit and loss sharing", "p&l sharing", "distribution of profits",
            "allocation of losses", "partnership distributions", "profit sharing ratio"
        ],
    },
    "Partner Responsibilities": {
        "risk_type": "Operational Risk",
        "base_severity": 4,
        "provisional": True,
        "expert_validated": False,
        "source": "EXTENDED_CORPORATE",
        "description": "Managerial duties, voting powers, authority to bind the partnership, and fiduciary obligations.",
        "detection_method": "experimental_keyword",
        "cuad_question": "Does the clause delineate managerial responsibilities, voting rights, or fiduciary duties of partners?",
        "aliases": [
            "partner responsibilities", "management duties", "partner authority",
            "fiduciary duties", "voting rights of partners", "decision-making authority"
        ],
    },
    "Partner Exit and Dissolution": {
        "risk_type": "Termination Risk",
        "base_severity": 7,
        "provisional": True,
        "expert_validated": False,
        "source": "EXTENDED_CORPORATE",
        "description": "Voluntary withdrawal, expulsion of a partner, buyout mechanics, valuation, and partnership winding-up.",
        "detection_method": "experimental_keyword",
        "cuad_question": "Does the clause govern partner withdrawal, buyout, expulsion, or dissolution of the partnership?",
        "aliases": [
            "partner exit and dissolution", "partnership dissolution", "withdrawal of partner",
            "buyout of partner", "expulsion of partner", "winding up and liquidation"
        ],
    },

    # =========================================================================
    # MERGER / ACQUISITION CATEGORIES
    # =========================================================================
    "Representations and Warranties": {
        "risk_type": "Legal/Compliance Risk",
        "base_severity": 6,
        "provisional": True,
        "expert_validated": False,
        "source": "EXTENDED_TRANSACTION",
        "description": "Formal assertions of fact regarding corporate standing, financial statements, liabilities, and title to assets.",
        "detection_method": "experimental_keyword",
        "cuad_question": "Does the clause contain seller or buyer representations and warranties concerning company affairs?",
        "aliases": [
            "representations and warranties", "seller representations", "buyer representations",
            "reps and warranties", "fundamental representations"
        ],
    },
    "Purchase Price": {
        "risk_type": "Financial Risk",
        "base_severity": 5,
        "provisional": True,
        "expert_validated": False,
        "source": "EXTENDED_TRANSACTION",
        "description": "Total acquisition consideration, cash/equity components, earnout formulas, and working capital adjustments.",
        "detection_method": "experimental_keyword",
        "cuad_question": "Does the clause specify the purchase price, consideration, earnouts, or working capital adjustment?",
        "aliases": [
            "purchase price", "purchase consideration", "acquisition price",
            "earnout", "working capital adjustment", "escrow holdback"
        ],
    },
    "Closing Conditions": {
        "risk_type": "Operational Risk",
        "base_severity": 6,
        "provisional": True,
        "expert_validated": False,
        "source": "EXTENDED_TRANSACTION",
        "description": "Conditions precedent that must be satisfied or waived prior to completion of the transaction.",
        "detection_method": "experimental_keyword",
        "cuad_question": "Does the clause state conditions precedent to closing or required regulatory and shareholder approvals?",
        "aliases": [
            "closing conditions", "conditions precedent", "conditions to closing",
            "closing deliverables", "regulatory approvals condition"
        ],
    },
    "Post-Closing Obligations": {
        "risk_type": "Operational Risk",
        "base_severity": 5,
        "provisional": True,
        "expert_validated": False,
        "source": "EXTENDED_TRANSACTION",
        "description": "Post-closing covenants, transition services, access to records, and indemnification survival periods.",
        "detection_method": "experimental_keyword",
        "cuad_question": "Does the clause impose post-closing covenants, transition services, or cooperation duties?",
        "aliases": [
            "post-closing obligations", "post-closing covenants", "transition obligations",
            "indemnification survival", "post-closing cooperation"
        ],
    },

    # =========================================================================
    # VENDOR / SUPPLY CATEGORIES
    # =========================================================================
    "Product Specifications and Quality": {
        "risk_type": "Operational Risk",
        "base_severity": 5,
        "provisional": True,
        "expert_validated": False,
        "source": "EXTENDED_SUPPLY",
        "description": "Technical standards, tolerances, quality assurance requirements, and regulatory manufacturing compliance.",
        "detection_method": "experimental_keyword",
        "cuad_question": "Does the clause define technical product specifications, quality standards, or manufacturing tolerances?",
        "aliases": [
            "product specifications and quality", "specifications", "product quality",
            "quality standards", "manufacturing standards", "conformance to specifications"
        ],
    },
    "Inspection and Acceptance": {
        "risk_type": "Operational Risk",
        "base_severity": 4,
        "provisional": True,
        "expert_validated": False,
        "source": "EXTENDED_SUPPLY",
        "description": "Buyer's right to inspect delivered goods, rejection timelines, and non-conforming goods notifications.",
        "detection_method": "experimental_keyword",
        "cuad_question": "Does the clause specify inspection procedures, rejection notice deadlines, or acceptance of goods?",
        "aliases": [
            "inspection and acceptance", "incoming inspection", "goods inspection",
            "rejection of goods", "acceptance of products", "non-conforming goods"
        ],
    },
    "Delivery Obligations": {
        "risk_type": "Operational Risk",
        "base_severity": 5,
        "provisional": True,
        "expert_validated": False,
        "source": "EXTENDED_SUPPLY",
        "description": "Shipment schedules, lead times, Incoterms, transfer of title, and allocation of transit risk.",
        "detection_method": "experimental_keyword",
        "cuad_question": "Does the clause define delivery schedules, Incoterms, shipping obligations, or risk of loss?",
        "aliases": [
            "delivery obligations", "shipping terms", "delivery schedule", "incoterms",
            "transit risk", "lead times", "risk of loss"
        ],
    },
    "Remedies for Non-Performance": {
        "risk_type": "Commercial Risk",
        "base_severity": 6,
        "provisional": True,
        "expert_validated": False,
        "source": "EXTENDED_SUPPLY",
        "description": "Rights upon delivery default or defective products, including repair, replacement, refund, or cover damages.",
        "detection_method": "experimental_keyword",
        "cuad_question": "Does the clause provide remedies for default or defective delivery such as repair, replacement, or cover?",
        "aliases": [
            "remedies for non-performance", "remedies for breach", "default remedies",
            "service credits", "replacement of goods", "cover damages"
        ],
    },
}

# Pre-computed alias mapping for fast case-insensitive lookup
_ALIAS_MAP: Dict[str, str] = {}

def _build_alias_map():
    # 1. Populate aliases from original 41 CUAD categories
    for cat in RISK_TAXONOMY.keys():
        norm = cat.strip().lower()
        _ALIAS_MAP[norm] = cat
        _ALIAS_MAP[norm.replace("-", " ")] = cat
        _ALIAS_MAP[norm.replace(" ", "")] = cat

    # Special aliases mapping to existing CUAD categories (NO DUPLICATES)
    _ALIAS_MAP["limitation of liability"] = "Cap On Liability"
    _ALIAS_MAP["liability cap"] = "Cap On Liability"
    _ALIAS_MAP["cap on liability"] = "Cap On Liability"
    _ALIAS_MAP["uncapped liability"] = "Uncapped Liability"
    _ALIAS_MAP["unlimited liability"] = "Uncapped Liability"
    _ALIAS_MAP["licence grant"] = "License Grant"
    _ALIAS_MAP["license grant"] = "License Grant"
    _ALIAS_MAP["ip assignment"] = "IP Ownership Assignment"
    _ALIAS_MAP["ip ownership"] = "IP Ownership Assignment"
    _ALIAS_MAP["intellectual property ownership"] = "IP Ownership Assignment"
    _ALIAS_MAP["ownership of deliverables"] = "IP Ownership Assignment"
    _ALIAS_MAP["anti assignment"] = "Anti-Assignment"
    _ALIAS_MAP["no solicit of customers"] = "No-Solicit Of Customers"
    _ALIAS_MAP["no solicit of employees"] = "No-Solicit Of Employees"
    _ALIAS_MAP["post termination services"] = "Post-Termination Services"
    _ALIAS_MAP["notice period to terminate renewal"] = "Notice Period To Terminate Renewal"
    _ALIAS_MAP["covenant not to sue"] = "Covenant Not To Sue"

    # 2. Populate aliases from custom extended categories
    for cat, info in CUSTOM_TAXONOMY.items():
        norm = cat.strip().lower()
        _ALIAS_MAP[norm] = cat
        _ALIAS_MAP[norm.replace("-", " ")] = cat
        _ALIAS_MAP[norm.replace(" ", "")] = cat
        for alias in info.get("aliases", []):
            a_norm = alias.strip().lower()
            _ALIAS_MAP[a_norm] = cat
            _ALIAS_MAP[a_norm.replace("-", " ")] = cat
            _ALIAS_MAP[a_norm.replace(" ", "")] = cat

_build_alias_map()


def normalize_category_name(raw_name: Optional[str]) -> str:
    """
    Normalizes a category string to its canonical taxonomy name.
    Handles case variations, whitespace, hyphens, and legal synonyms.
    If no match is found, returns the cleaned input string.
    """
    if not raw_name:
        return "Unknown"
    cleaned = raw_name.strip()
    norm = cleaned.lower()

    if norm in _ALIAS_MAP:
        return _ALIAS_MAP[norm]

    # Try removing extra internal whitespace
    condensed = re.sub(r"\s+", " ", norm)
    if condensed in _ALIAS_MAP:
        return _ALIAS_MAP[condensed]

    # Try punctuation removal
    no_punct = re.sub(r"[^\w\s]", " ", norm)
    condensed_no_punct = re.sub(r"\s+", " ", no_punct).strip()
    if condensed_no_punct in _ALIAS_MAP:
        return _ALIAS_MAP[condensed_no_punct]

    return cleaned


def get_category_info(category_name: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves metadata for a category from either the baseline CUAD taxonomy
    or the custom extended taxonomy. Returns None if unknown.
    """
    canonical = normalize_category_name(category_name)
    if canonical in RISK_TAXONOMY:
        entry = dict(RISK_TAXONOMY[canonical])
        entry["provisional"] = False
        entry["expert_validated"] = (entry.get("source") == "VERIFIED")
        entry["canonical_name"] = canonical
        return entry
    if canonical in CUSTOM_TAXONOMY:
        entry = dict(CUSTOM_TAXONOMY[canonical])
        entry["canonical_name"] = canonical
        return entry
    return None


def is_provisional_category(category_name: str) -> bool:
    """Returns True if the category's severity is provisional / unvalidated."""
    info = get_category_info(category_name)
    if info:
        return info.get("provisional", True)
    return True


def get_all_categories() -> Dict[str, Dict[str, Any]]:
    """
    Returns unified dictionary of all categories across both taxonomies.
    Original CUAD entries take precedence in case of key overlap.
    """
    unified = {}
    for k, v in CUSTOM_TAXONOMY.items():
        unified[k] = dict(v)
    for k, v in RISK_TAXONOMY.items():
        unified[k] = dict(v)
        unified[k]["provisional"] = False
        unified[k]["expert_validated"] = (v.get("source") == "VERIFIED")
    return unified


# Unified exportable dictionary
EXTENDED_TAXONOMY = get_all_categories()
