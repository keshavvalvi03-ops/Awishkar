"""
Contract Types Definitions, Checklists, and Suggestion Engine
-------------------------------------------------------------
Defines 10 standard commercial contract types, their respective clause checklists
(Expected, Conditional, Optional), and a transparent heuristic suggestion engine
for classifying unidentified contracts with evidence snippets.

LEGAL SCOPE DISCLAIMER:
This classification and checklist system provides heuristic operational assistance
for commercial triage. It does NOT constitute legal advice or guarantee universal
legal coverage across all jurisdictions or bespoke transactions.
"""

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any, Tuple
from custom_taxonomy import normalize_category_name

# Standard Status constants
STATUS_DETECTED = "Detected"
STATUS_NOT_DETECTED = "Not detected — verify manually"
STATUS_NOT_APPLICABLE = "Not applicable"
STATUS_UNCERTAIN = "Uncertain"

# Relevance constants
RELEVANCE_EXPECTED = "Expected"
RELEVANCE_CONDITIONAL = "Conditional"
RELEVANCE_OPTIONAL = "Optional"

# Detection method constants
METHOD_CUAD = "cuad_model"
METHOD_KEYWORD = "experimental_keyword"
METHOD_MANUAL = "manual_review"

# Support status constants
SUPPORT_CUAD = "supported_cuad"
SUPPORT_KEYWORD = "supported_keyword"
SUPPORT_MANUAL = "manual_only"


@dataclass
class ChecklistItem:
    clause_name: str
    relevance: str  # Expected, Conditional, Optional
    reason: str
    detection_method: str = METHOD_KEYWORD
    support_status: str = SUPPORT_KEYWORD
    recommended_action: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "clause_name": self.clause_name,
            "relevance": self.relevance,
            "reason": self.reason,
            "detection_method": self.detection_method,
            "support_status": self.support_status,
            "recommended_action": self.recommended_action,
        }


@dataclass
class ContractTypeDefinition:
    type_id: str
    name: str
    description: str
    aliases: List[str]
    title_patterns: List[str]
    keyword_patterns: List[str]
    checklist: List[ChecklistItem] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type_id": self.type_id,
            "name": self.name,
            "description": self.description,
            "aliases": self.aliases,
            "checklist": [item.to_dict() for item in self.checklist],
        }


# =============================================================================
# 10 CONTRACT TYPE SPECIFICATIONS AND CHECKLISTS
# =============================================================================

CONTRACT_TYPES: Dict[str, ContractTypeDefinition] = {
    # 1. SERVICE AGREEMENT
    "service_agreement": ContractTypeDefinition(
        type_id="service_agreement",
        name="Service Agreement",
        description="Contract governing provision of professional, consulting, or technical services.",
        aliases=["service agreement", "master services agreement", "msa", "consulting agreement", "services contract"],
        title_patterns=[
            r"\b(?:master\s+)?services?\s+agreement\b",
            r"\bconsulting\s+(?:services\s+)?agreement\b",
            r"\bprofessional\s+services\s+agreement\b",
        ],
        keyword_patterns=[
            r"\bscope\s+of\s+services\b",
            r"\bconsulting\s+services\b",
            r"\bstatement\s+of\s+work\b",
            r"\bclient\s+and\s+(?:consultant|contractor|service\s+provider)\b",
        ],
        checklist=[
            ChecklistItem("Scope of Services", RELEVANCE_EXPECTED, "Defines exact deliverables, milestones, and standard of performance.", METHOD_KEYWORD, SUPPORT_KEYWORD, "Ensure duties and specifications are unambiguous."),
            ChecklistItem("Payment Terms", RELEVANCE_EXPECTED, "Establishes fee structure, invoice schedule, and reimbursement terms.", METHOD_KEYWORD, SUPPORT_KEYWORD, "Verify payment milestones and net payment window."),
            ChecklistItem("Termination For Cause", RELEVANCE_EXPECTED, "Ensures remedy and right of exit upon material breach or non-performance.", METHOD_KEYWORD, SUPPORT_KEYWORD, "Check cure notice period (typically 15-30 days)."),
            ChecklistItem("Termination For Convenience", RELEVANCE_CONDITIONAL, "Allows client or provider to terminate early without default.", METHOD_CUAD, SUPPORT_CUAD, "Evaluate notice requirements and wind-down costs."),
            ChecklistItem("Cap On Liability", RELEVANCE_EXPECTED, "Limits financial exposure arising from performance failures or damages.", METHOD_CUAD, SUPPORT_CUAD, "Ensure aggregate cap aligns with total contract value."),
            ChecklistItem("Indemnity", RELEVANCE_CONDITIONAL, "Allocates risk for third-party claims arising from negligence or IP infringement.", METHOD_KEYWORD, SUPPORT_KEYWORD, "Review scope of indemnification and defense obligations."),
            ChecklistItem("Confidentiality", RELEVANCE_EXPECTED, "Protects client business data shared during service delivery.", METHOD_KEYWORD, SUPPORT_KEYWORD, "Confirm mutual obligations and carve-outs."),
            ChecklistItem("Governing Law", RELEVANCE_EXPECTED, "Specifies jurisdiction and applicable laws governing dispute adjudication.", METHOD_CUAD, SUPPORT_CUAD, "Confirm familiarity with chosen legal forum."),
            ChecklistItem("Dispute Resolution", RELEVANCE_EXPECTED, "Sets out escalation procedure (negotiation, mediation, arbitration).", METHOD_KEYWORD, SUPPORT_KEYWORD, "Verify whether arbitration or court litigation is preferred."),
            ChecklistItem("IP Ownership Assignment", RELEVANCE_CONDITIONAL, "Governs whether client owns deliverables as work-for-hire.", METHOD_CUAD, SUPPORT_CUAD, "Confirm IP transfer on paid deliverables vs retained background IP."),
            ChecklistItem("Warranties", RELEVANCE_CONDITIONAL, "Guarantees professional standard of workmanship and compliance.", METHOD_KEYWORD, SUPPORT_KEYWORD, "Verify warranty duration and remedy of re-performance."),
            ChecklistItem("Insurance", RELEVANCE_OPTIONAL, "Requires provider to maintain commercial general liability or E&O insurance.", METHOD_CUAD, SUPPORT_CUAD, "Verify minimum coverage limits if relevant to project scale."),
            ChecklistItem("Force Majeure", RELEVANCE_OPTIONAL, "Protects against delays caused by unforeseeable catastrophic events.", METHOD_KEYWORD, SUPPORT_KEYWORD, "Ensure notice is required upon force majeure occurrence."),
            ChecklistItem("Non-Solicitation", RELEVANCE_OPTIONAL, "Prevents poaching of key project personnel or client staff.", METHOD_KEYWORD, SUPPORT_KEYWORD, "Review duration and reasonableness of solicitation restrictions."),
        ],
    ),

    # 2. EMPLOYMENT AGREEMENT
    "employment_agreement": ContractTypeDefinition(
        type_id="employment_agreement",
        name="Employment Agreement",
        description="Contract establishing terms and conditions of individual employment.",
        aliases=["employment agreement", "employment contract", "offer letter", "executive employment agreement"],
        title_patterns=[
            r"\b(?:executive\s+)?employment\s+(?:agreement|contract)\b",
            r"\bcontract\s+of\s+employment\b",
            r"\bterms\s+of\s+employment\b",
        ],
        keyword_patterns=[
            r"\bemployer\s+and\s+employee\b",
            r"\bbase\s+salary\b",
            r"\bduties\s+and\s+responsibilities\b",
            r"\bat-will\s+employment\b",
        ],
        checklist=[
            ChecklistItem("Salary and Compensation", RELEVANCE_EXPECTED, "Defines base wage, incentive bonuses, and payment schedule.", METHOD_KEYWORD, SUPPORT_KEYWORD, "Verify compensation frequency and bonus criteria."),
            ChecklistItem("Scope of Services", RELEVANCE_EXPECTED, "Sets out job title, core responsibilities, and reporting hierarchy.", METHOD_KEYWORD, SUPPORT_KEYWORD, "Review job description clarity and modification rights."),
            ChecklistItem("Employment Termination", RELEVANCE_EXPECTED, "Specifies notice requirements, at-will status, or severance mechanics.", METHOD_KEYWORD, SUPPORT_KEYWORD, "Check required notice period and severance eligibility."),
            ChecklistItem("Governing Law", RELEVANCE_EXPECTED, "Identifies state/national labor jurisdiction governing the relationship.", METHOD_CUAD, SUPPORT_CUAD, "Confirm compliance with local mandatory labor statutes."),
            ChecklistItem("Confidentiality", RELEVANCE_EXPECTED, "Protects company trade secrets and proprietary data post-employment.", METHOD_KEYWORD, SUPPORT_KEYWORD, "Ensure confidentiality extends indefinitely for trade secrets."),
            ChecklistItem("Benefits", RELEVANCE_CONDITIONAL, "Details healthcare, paid time off, pension/401k, and fringe perks.", METHOD_KEYWORD, SUPPORT_KEYWORD, "Review vesting and eligibility timelines."),
            ChecklistItem("IP Ownership Assignment", RELEVANCE_CONDITIONAL, "Assigns inventions and works created during employment to employer.", METHOD_CUAD, SUPPORT_CUAD, "Ensure statutory carve-outs for inventions created on personal time."),
            ChecklistItem("Non-Compete", RELEVANCE_CONDITIONAL, "Restricts post-termination employment with direct competitors.", METHOD_CUAD, SUPPORT_CUAD, "Verify enforceability under governing jurisdiction's labor laws."),
            ChecklistItem("Non-Solicitation", RELEVANCE_CONDITIONAL, "Restricts soliciting coworkers or clients post-departure.", METHOD_KEYWORD, SUPPORT_KEYWORD, "Check geographic scope and duration (typically 6-12 months)."),
            ChecklistItem("Working Conditions", RELEVANCE_OPTIONAL, "Details work location, hybrid policies, and overtime eligibility.", METHOD_KEYWORD, SUPPORT_KEYWORD, "Confirm remote work or relocation stipulations."),
            ChecklistItem("Dispute Resolution", RELEVANCE_OPTIONAL, "Mandates arbitration or mediation for employment disputes.", METHOD_KEYWORD, SUPPORT_KEYWORD, "Verify legality of mandatory employee arbitration clauses."),
        ],
    ),

    # 3. NDA / CONFIDENTIALITY AGREEMENT
    "nda": ContractTypeDefinition(
        type_id="nda",
        name="NDA / Confidentiality Agreement",
        description="Agreement governing protection and non-disclosure of proprietary information.",
        aliases=["nda", "non-disclosure agreement", "confidentiality agreement", "proprietary information agreement", "mutual nda"],
        title_patterns=[
            r"\bnon-disclosure\s+agreement\b",
            r"\bconfidentiality\s+agreement\b",
            r"\b\bNDA\b\b",
            r"\bproprietary\s+information\s+agreement\b",
        ],
        keyword_patterns=[
            r"\bconfidential\s+information\b",
            r"\bdisclosing\s+party\s+and\s+receiving\s+party\b",
            r"\bnon-disclosure\b",
            r"\bstandard\s+of\s+care\b",
        ],
        checklist=[
            ChecklistItem("Confidentiality", RELEVANCE_EXPECTED, "Core definition of protected confidential information and duties of care.", METHOD_KEYWORD, SUPPORT_KEYWORD, "Confirm definition breadth and required markings."),
            ChecklistItem("Governing Law", RELEVANCE_EXPECTED, "Governing law and jurisdiction for seeking emergency injunctive relief.", METHOD_CUAD, SUPPORT_CUAD, "Confirm court jurisdiction for enforcing non-disclosure."),
            ChecklistItem("Termination For Convenience", RELEVANCE_CONDITIONAL, "Duration of the disclosure period and survival of non-disclosure duties.", METHOD_CUAD, SUPPORT_CUAD, "Check confidentiality survival term (typically 2-5 years)."),
            ChecklistItem("Dispute Resolution", RELEVANCE_CONDITIONAL, "Specifies arbitration or court venue for breach of secrecy.", METHOD_KEYWORD, SUPPORT_KEYWORD, "Ensure parties preserve right to immediate injunctive relief."),
            ChecklistItem("Notice Requirements", RELEVANCE_OPTIONAL, "Process for notifying disclosing party of subpoena or court-ordered disclosure.", METHOD_KEYWORD, SUPPORT_KEYWORD, "Check compelled disclosure notice timelines."),
            ChecklistItem("Non-Solicitation", RELEVANCE_OPTIONAL, "Restricts soliciting discussions or employees evaluated during diligence.", METHOD_KEYWORD, SUPPORT_KEYWORD, "Verify whether diligence exclusivity/non-solicit is needed."),
            ChecklistItem("Entire Agreement", RELEVANCE_OPTIONAL, "Confirms NDA stands alone for evaluation purposes.", METHOD_KEYWORD, SUPPORT_KEYWORD, "Confirm no implied license or partnership is created."),
        ],
    ),

    # 4. SOFTWARE / IT AGREEMENT
    "software_it_agreement": ContractTypeDefinition(
        type_id="software_it_agreement",
        name="Software / IT Agreement",
        description="Agreement for software licensing, SaaS access, IT implementation, or cloud hosting.",
        aliases=["software agreement", "it agreement", "saas agreement", "software license agreement", "cloud services agreement"],
        title_patterns=[
            r"\bsoftware\s+(?:license\s+)?agreement\b",
            r"\bSaaS\s+(?:services\s+)?agreement\b",
            r"\bcloud\s+services\s+agreement\b",
            r"\bsoftware-as-a-service\b",
        ],
        keyword_patterns=[
            r"\blicensed\s+software\b",
            r"\bsaas\s+platform\b",
            r"\buptime\s+commitment\b",
            r"\bdata\s+security\b",
            r"\btechnical\s+support\b",
        ],
        checklist=[
            ChecklistItem("License Grant", RELEVANCE_EXPECTED, "Authorizes use of software, scope of access (seats, cores, enterprise).", METHOD_CUAD, SUPPORT_CUAD, "Review license metric and restriction to authorized users."),
            ChecklistItem("Licence Restrictions", RELEVANCE_EXPECTED, "Prohibits reverse engineering, decompiling, benchmarking, or reselling.", METHOD_KEYWORD, SUPPORT_KEYWORD, "Verify protection against unauthorized code extraction."),
            ChecklistItem("Cap On Liability", RELEVANCE_EXPECTED, "Limits vendor or customer monetary exposure to fees paid.", METHOD_CUAD, SUPPORT_CUAD, "Check whether data breaches or IP claims have super-caps."),
            ChecklistItem("Data Privacy", RELEVANCE_EXPECTED, "Protects customer/user personal information processed on cloud systems.", METHOD_KEYWORD, SUPPORT_KEYWORD, "Ensure compliance with GDPR/DPDP/CCPA and DPA inclusion."),
            ChecklistItem("Data Protection and Security", RELEVANCE_EXPECTED, "Sets out technical controls, encryption standards, and breach notice.", METHOD_KEYWORD, SUPPORT_KEYWORD, "Review breach notification deadline (e.g. 48-72 hours)."),
            ChecklistItem("Service Levels", RELEVANCE_CONDITIONAL, "SLA metrics including uptime guarantee (e.g. 99.9%) and service credits.", METHOD_KEYWORD, SUPPORT_KEYWORD, "Ensure remedies exist for recurring downtime."),
            ChecklistItem("Support and Maintenance", RELEVANCE_CONDITIONAL, "Commitments for bug fixes, patches, helpdesk response times.", METHOD_KEYWORD, SUPPORT_KEYWORD, "Review severity levels and response time tiers."),
            ChecklistItem("Payment Terms", RELEVANCE_EXPECTED, "Subscription fee, usage tiers, and invoicing cycle.", METHOD_KEYWORD, SUPPORT_KEYWORD, "Check renewal price increase limits."),
            ChecklistItem("Termination For Cause", RELEVANCE_EXPECTED, "Right to terminate for material breach or chronic SLA failures.", METHOD_KEYWORD, SUPPORT_KEYWORD, "Check data retrieval window upon contract termination."),
            ChecklistItem("IP Ownership", RELEVANCE_EXPECTED, "Protects vendor's code and client's proprietary data inputs.", METHOD_KEYWORD, SUPPORT_KEYWORD, "Ensure client retains sole ownership of customer data."),
            ChecklistItem("Source Code Escrow", RELEVANCE_OPTIONAL, "Deposits source code with third party in case vendor dissolves.", METHOD_CUAD, SUPPORT_CUAD, "Evaluate need for mission-critical on-premise software."),
            ChecklistItem("Governing Law", RELEVANCE_EXPECTED, "Choice of jurisdiction for technology disputes.", METHOD_CUAD, SUPPORT_CUAD, "Verify neutral and appropriate forum."),
        ],
    ),

    # 5. VENDOR / SUPPLY AGREEMENT
    "vendor_supply_agreement": ContractTypeDefinition(
        type_id="vendor_supply_agreement",
        name="Vendor / Supply Agreement",
        description="Agreement for the manufacturing, purchase, and delivery of commercial goods or hardware.",
        aliases=["vendor agreement", "supply agreement", "manufacturing agreement", "purchase agreement", "supply contract"],
        title_patterns=[
            r"\b(?:master\s+)?supply\s+agreement\b",
            r"\bvendor\s+(?:supply\s+)?agreement\b",
            r"\bmanufacturing\s+(?:and\s+supply\s+)?agreement\b",
            r"\bgoods\s+purchase\s+agreement\b",
        ],
        keyword_patterns=[
            r"\bproduct\s+specifications\b",
            r"\bdelivery\s+schedule\b",
            r"\bincoterms\b",
            r"\binspection\s+and\s+acceptance\b",
            r"\bpurchase\s+orders?\b",
        ],
        checklist=[
            ChecklistItem("Product Specifications and Quality", RELEVANCE_EXPECTED, "Sets quality criteria, tolerances, and technical standards for goods.", METHOD_KEYWORD, SUPPORT_KEYWORD, "Confirm specification annexes are detailed and binding."),
            ChecklistItem("Delivery Obligations", RELEVANCE_EXPECTED, "Defines shipment schedule, Incoterms, and title/risk transfer points.", METHOD_KEYWORD, SUPPORT_KEYWORD, "Verify delivery locations and risk-of-loss transfer terms."),
            ChecklistItem("Inspection and Acceptance", RELEVANCE_EXPECTED, "Buyer's right to inspect goods and reject non-conforming batches.", METHOD_KEYWORD, SUPPORT_KEYWORD, "Ensure reasonable inspection window before deemed acceptance."),
            ChecklistItem("Remedies for Non-Performance", RELEVANCE_EXPECTED, "Provides replacement, repair, refunds, or cover for defective products.", METHOD_KEYWORD, SUPPORT_KEYWORD, "Confirm remedy choices and allocation of return shipping costs."),
            ChecklistItem("Payment Terms", RELEVANCE_EXPECTED, "Defines purchase order pricing, volume discounts, and payment terms.", METHOD_KEYWORD, SUPPORT_KEYWORD, "Verify payment terms against inspection acceptance milestones."),
            ChecklistItem("Warranties", RELEVANCE_EXPECTED, "Guarantees against defects in materials, design, and workmanship.", METHOD_KEYWORD, SUPPORT_KEYWORD, "Check warranty duration (typically 12-24 months from delivery)."),
            ChecklistItem("Cap On Liability", RELEVANCE_EXPECTED, "Caps damages while ensuring recall/defective product remedies survive.", METHOD_CUAD, SUPPORT_CUAD, "Review whether product liability claims are carved out."),
            ChecklistItem("Indemnity", RELEVANCE_CONDITIONAL, "Protects buyer against third-party patent or bodily injury claims.", METHOD_KEYWORD, SUPPORT_KEYWORD, "Ensure vendor indemnifies against intellectual property infringement."),
            ChecklistItem("Minimum Commitment", RELEVANCE_CONDITIONAL, "Obligates buyer to purchase minimum quantities or pay shortfalls.", METHOD_CUAD, SUPPORT_CUAD, "Assess financial exposure if volume forecast is missed."),
            ChecklistItem("Insurance", RELEVANCE_CONDITIONAL, "Mandates product liability and transit insurance.", METHOD_CUAD, SUPPORT_CUAD, "Review minimum policy coverage limits."),
            ChecklistItem("Force Majeure", RELEVANCE_OPTIONAL, "Excuses supply chain disruptions due to external emergencies.", METHOD_KEYWORD, SUPPORT_KEYWORD, "Ensure raw material shortages are not broadly excused."),
            ChecklistItem("Governing Law", RELEVANCE_EXPECTED, "Governing jurisdiction for commercial sales disputes.", METHOD_CUAD, SUPPORT_CUAD, "Confirm application or exclusion of CISG."),
        ],
    ),

    # 6. LEASE / RENTAL AGREEMENT
    "lease_rental_agreement": ContractTypeDefinition(
        type_id="lease_rental_agreement",
        name="Lease / Rental Agreement",
        description="Agreement for the tenancy, lease, or rental of real estate property or equipment.",
        aliases=["lease agreement", "rental agreement", "commercial lease", "tenancy agreement", "property lease"],
        title_patterns=[
            r"\b(?:commercial\s+)?lease\s+agreement\b",
            r"\brental\s+agreement\b",
            r"\btenancy\s+agreement\b",
            r"\bpremises\s+lease\b",
        ],
        keyword_patterns=[
            r"\blandlord\s+and\s+tenant\b",
            r"\bleased\s+premises\b",
            r"\bmonthly\s+rent\b",
            r"\bsecurity\s+deposit\b",
            r"\bquiet\s+enjoyment\b",
        ],
        checklist=[
            ChecklistItem("Rent", RELEVANCE_EXPECTED, "Base periodic rental amount, escalation percentage, and due date.", METHOD_KEYWORD, SUPPORT_KEYWORD, "Verify rent escalation formula and grace period."),
            ChecklistItem("Security Deposit", RELEVANCE_EXPECTED, "Deposit amount, holding terms, and refund conditions upon exit.", METHOD_KEYWORD, SUPPORT_KEYWORD, "Confirm timeline for deposit return and deduction standards."),
            ChecklistItem("Lease Termination", RELEVANCE_EXPECTED, "Lease expiration date, renewal options, and surrender standards.", METHOD_KEYWORD, SUPPORT_KEYWORD, "Verify notice window required to vacate or renew."),
            ChecklistItem("Landlord and Tenant Obligations", RELEVANCE_EXPECTED, "Permitted use, building compliance, alterations, quiet enjoyment.", METHOD_KEYWORD, SUPPORT_KEYWORD, "Review operational restrictions and landlord access rights."),
            ChecklistItem("Property Maintenance", RELEVANCE_EXPECTED, "Division of structural vs non-structural upkeep responsibilities.", METHOD_KEYWORD, SUPPORT_KEYWORD, "Ensure landlord maintains foundation, roof, and common HVAC."),
            ChecklistItem("Insurance", RELEVANCE_CONDITIONAL, "Mandates tenant property and liability insurance naming landlord.", METHOD_CUAD, SUPPORT_CUAD, "Verify required coverage amounts."),
            ChecklistItem("Renewal Term", RELEVANCE_CONDITIONAL, "Option to extend lease term upon pre-agreed terms.", METHOD_CUAD, SUPPORT_CUAD, "Check option notice deadline (typically 3-6 months prior)."),
            ChecklistItem("Governing Law", RELEVANCE_EXPECTED, "Local property jurisdiction governing the leased real estate.", METHOD_CUAD, SUPPORT_CUAD, "Must match physical jurisdiction of premises."),
            ChecklistItem("Dispute Resolution", RELEVANCE_OPTIONAL, "Mediation or local court proceedings for tenancy disputes.", METHOD_KEYWORD, SUPPORT_KEYWORD, "Confirm local tenancy board or court jurisdiction."),
        ],
    ),

    # 7. LICENSING AGREEMENT
    "licensing_agreement": ContractTypeDefinition(
        type_id="licensing_agreement",
        name="Licensing Agreement",
        description="Agreement granting commercial rights to intellectual property, patents, or trademarks.",
        aliases=["licensing agreement", "license agreement", "ip license", "patent license", "trademark license agreement"],
        title_patterns=[
            r"\b(?:patent|trademark|technology|ip)\s+licen[sc]e\s+agreement\b",
            r"\bintellectual\s+property\s+licen[sc]ing\s+agreement\b",
            r"\bexclusive\s+licen[sc]e\s+agreement\b",
        ],
        keyword_patterns=[
            r"\blicensor\s+and\s+licensee\b",
            r"\blicensed\s+(?:technology|patents?|trademarks?|ip)\b",
            r"\bgrant\s+of\s+licen[sc]e\b",
            r"\broyalt(?:y|ies)\b",
        ],
        checklist=[
            ChecklistItem("License Grant", RELEVANCE_EXPECTED, "Explicit authorization of IP rights: scope, field of use, territory.", METHOD_CUAD, SUPPORT_CUAD, "Verify exclusivity, field-of-use, and geographic territory boundaries."),
            ChecklistItem("Licence Restrictions", RELEVANCE_EXPECTED, "Limitations on sublicensing, modifying, combining, or transferring.", METHOD_KEYWORD, SUPPORT_KEYWORD, "Confirm boundaries on licensee commercial rights."),
            ChecklistItem("Royalties", RELEVANCE_CONDITIONAL, "Royalty rates, calculation basis, auditing, and reporting deadlines.", METHOD_KEYWORD, SUPPORT_KEYWORD, "Review royalty percentage and minimum annual royalty guarantees."),
            ChecklistItem("Licence Fees", RELEVANCE_CONDITIONAL, "Upfront execution fees, milestones, or annual maintenance charges.", METHOD_KEYWORD, SUPPORT_KEYWORD, "Confirm payment triggers and milestone acceptance criteria."),
            ChecklistItem("IP Ownership", RELEVANCE_EXPECTED, "Confirms licensor retains sole title to underlying IP and improvements.", METHOD_KEYWORD, SUPPORT_KEYWORD, "Ensure licensor owns derivative works and patent improvements."),
            ChecklistItem("Audit Rights", RELEVANCE_CONDITIONAL, "Right of licensor to inspect sales records and royalty accounting.", METHOD_CUAD, SUPPORT_CUAD, "Check audit frequency and shortfall threshold for cost shifting."),
            ChecklistItem("Warranties", RELEVANCE_CONDITIONAL, "Representations regarding patent validity and non-infringement.", METHOD_KEYWORD, SUPPORT_KEYWORD, "Verify whether licensor warrants against third-party infringement."),
            ChecklistItem("Indemnity", RELEVANCE_CONDITIONAL, "Defense and indemnity against third-party patent or copyright suits.", METHOD_KEYWORD, SUPPORT_KEYWORD, "Confirm indemnification cap and claim defense conduct."),
            ChecklistItem("Termination For Cause", RELEVANCE_EXPECTED, "Right to revoke license upon royalty default or infringement.", METHOD_KEYWORD, SUPPORT_KEYWORD, "Check cure period for payment defaults."),
            ChecklistItem("Governing Law", RELEVANCE_EXPECTED, "Legal system governing IP interpretation.", METHOD_CUAD, SUPPORT_CUAD, "Ensure compatibility with relevant patent/trademark offices."),
        ],
    ),

    # 8. PARTNERSHIP AGREEMENT
    "partnership_agreement": ContractTypeDefinition(
        type_id="partnership_agreement",
        name="Partnership Agreement",
        description="Agreement establishing a formal partnership, joint venture, or business association.",
        aliases=["partnership agreement", "general partnership agreement", "limited partnership agreement", "joint venture agreement", "llp agreement"],
        title_patterns=[
            r"\b(?:general\s+|limited\s+)?partnership\s+agreement\b",
            r"\bjoint\s+venture\s+agreement\b",
            r"\bLLP\s+agreement\b",
        ],
        keyword_patterns=[
            r"\bpartners?\s+of\s+the\s+partnership\b",
            r"\bcapital\s+contributions?\b",
            r"\bprofit\s+and\s+loss\b",
            r"\bmanagement\s+of\s+the\s+partnership\b",
            r"\bdissolution\b",
        ],
        checklist=[
            ChecklistItem("Capital Contributions", RELEVANCE_EXPECTED, "Initial cash/property invested and rules for future capital calls.", METHOD_KEYWORD, SUPPORT_KEYWORD, "Verify consequences of failing to meet capital calls."),
            ChecklistItem("Profit and Loss Sharing", RELEVANCE_EXPECTED, "Ratios for distributing earnings and absorbing partnership liabilities.", METHOD_KEYWORD, SUPPORT_KEYWORD, "Confirm distribution schedule and tax allocation provisions."),
            ChecklistItem("Partner Responsibilities", RELEVANCE_EXPECTED, "Decision-making authority, voting thresholds, and fiduciary duties.", METHOD_KEYWORD, SUPPORT_KEYWORD, "Verify unanimous vs majority consent requirements."),
            ChecklistItem("Partner Exit and Dissolution", RELEVANCE_EXPECTED, "Mechanisms for retirement, expulsion, buyout valuation, and winding up.", METHOD_KEYWORD, SUPPORT_KEYWORD, "Review partner valuation formula (e.g. book value vs appraisal)."),
            ChecklistItem("Non-Compete", RELEVANCE_CONDITIONAL, "Prevents partners from running rival businesses during/after membership.", METHOD_CUAD, SUPPORT_CUAD, "Confirm reasonable duration and scope."),
            ChecklistItem("Confidentiality", RELEVANCE_EXPECTED, "Protects partnership commercial records and client lists.", METHOD_KEYWORD, SUPPORT_KEYWORD, "Ensure survival after a partner departs."),
            ChecklistItem("Governing Law", RELEVANCE_EXPECTED, "Statutory partnership jurisdiction governing entity governance.", METHOD_CUAD, SUPPORT_CUAD, "Confirm entity formation jurisdiction matches agreement law."),
            ChecklistItem("Dispute Resolution", RELEVANCE_EXPECTED, "Mediation and arbitration to resolve partner deadlocks.", METHOD_KEYWORD, SUPPORT_KEYWORD, "Include tie-breaker or mediation for deadlocked votes."),
        ],
    ),

    # 9. MERGER / ACQUISITION AGREEMENT
    "merger_acquisition_agreement": ContractTypeDefinition(
        type_id="merger_acquisition_agreement",
        name="Merger / Acquisition Agreement",
        description="Contract governing purchase of stock, assets, or statutory merger of business entities.",
        aliases=["merger agreement", "acquisition agreement", "stock purchase agreement", "asset purchase agreement", "spa", "apa"],
        title_patterns=[
            r"\b(?:agreement\s+and\s+plan\s+of\s+)?merger\b",
            r"\b(?:stock|share|asset)\s+purchase\s+agreement\b",
            r"\bacquisition\s+agreement\b",
            r"\b\bSPA\b|\bAPA\b\b",
        ],
        keyword_patterns=[
            r"\bpurchase\s+price\b",
            r"\bclosing\s+conditions\b",
            r"\brepresentations\s+and\s+warranties\s+of\s+seller\b",
            r"\bshares?\s+of\s+capital\s+stock\b",
            r"\bindemnification\s+escrow\b",
        ],
        checklist=[
            ChecklistItem("Purchase Price", RELEVANCE_EXPECTED, "Total transaction consideration, cash/stock mix, working capital adjustments.", METHOD_KEYWORD, SUPPORT_KEYWORD, "Review earnout metrics and post-closing true-up mechanics."),
            ChecklistItem("Representations and Warranties", RELEVANCE_EXPECTED, "Comprehensive seller disclosures on financial health, tax, litigation, and title.", METHOD_KEYWORD, SUPPORT_KEYWORD, "Review disclosure schedules and materiality qualifiers."),
            ChecklistItem("Closing Conditions", RELEVANCE_EXPECTED, "Prerequisites to closing: regulatory approvals, third-party consents, no MAE.", METHOD_KEYWORD, SUPPORT_KEYWORD, "Verify walk-away rights if conditions are not satisfied by drop-dead date."),
            ChecklistItem("Post-Closing Obligations", RELEVANCE_EXPECTED, "Transition covenants, record access, tax cooperation, and employee transitions.", METHOD_KEYWORD, SUPPORT_KEYWORD, "Ensure post-closing covenants have enforceable remedies."),
            ChecklistItem("Indemnity", RELEVANCE_CONDITIONAL, "Indemnification for representation breaches, indemnification baskets, and caps.", METHOD_KEYWORD, SUPPORT_KEYWORD, "Check indemnity cap, tipping vs deductible basket, and escrow period."),
            ChecklistItem("Non-Compete", RELEVANCE_CONDITIONAL, "Restricts selling founders/executives from competing post-sale.", METHOD_CUAD, SUPPORT_CUAD, "Confirm duration and territorial scope."),
            ChecklistItem("Termination For Cause", RELEVANCE_CONDITIONAL, "Right to terminate pre-closing upon material breach or outside drop-dead date.", METHOD_KEYWORD, SUPPORT_KEYWORD, "Check break-up fee or reverse break-up fee provisions."),
            ChecklistItem("Governing Law", RELEVANCE_EXPECTED, "Corporate jurisdiction (e.g. Delaware or relevant state law).", METHOD_CUAD, SUPPORT_CUAD, "Ensure forum selection matches corporate incorporation law."),
            ChecklistItem("Dispute Resolution", RELEVANCE_EXPECTED, "Arbitration or specialized commercial court venue.", METHOD_KEYWORD, SUPPORT_KEYWORD, "Verify venue and waiver of jury trial."),
        ],
    ),

    # 10. GENERAL BUSINESS AGREEMENT
    "general_business_agreement": ContractTypeDefinition(
        type_id="general_business_agreement",
        name="General Business Agreement",
        description="Standard commercial contract or bilateral trade agreement.",
        aliases=["general business agreement", "commercial agreement", "business contract", "commercial contract", "agreement"],
        title_patterns=[
            r"\bcommercial\s+agreement\b",
            r"\bbusiness\s+agreement\b",
            r"\bstandard\s+terms\s+and\s+conditions\b",
        ],
        keyword_patterns=[
            r"\bthe\s+parties\s+agree\b",
            r"\bterms\s+and\s+conditions\b",
            r"\bin\s+witness\s+whereof\b",
        ],
        checklist=[
            ChecklistItem("Scope of Services", RELEVANCE_EXPECTED, "Defines commercial subject matter, commitments, and obligations.", METHOD_KEYWORD, SUPPORT_KEYWORD, "Confirm subject matter and deliverables are explicitly defined."),
            ChecklistItem("Payment Terms", RELEVANCE_EXPECTED, "Defines commercial fees, pricing, payment terms, and invoicing.", METHOD_KEYWORD, SUPPORT_KEYWORD, "Check invoicing schedule and net payment days."),
            ChecklistItem("Termination For Cause", RELEVANCE_EXPECTED, "Right of termination upon material default or insolvency.", METHOD_KEYWORD, SUPPORT_KEYWORD, "Review cure notice timeline."),
            ChecklistItem("Termination For Convenience", RELEVANCE_CONDITIONAL, "Right of early termination without cause upon notice.", METHOD_CUAD, SUPPORT_CUAD, "Evaluate notice requirements and financial impacts."),
            ChecklistItem("Cap On Liability", RELEVANCE_EXPECTED, "Protects parties against unbounded financial loss.", METHOD_CUAD, SUPPORT_CUAD, "Ensure cap is balanced and reciprocal."),
            ChecklistItem("Confidentiality", RELEVANCE_CONDITIONAL, "Protects sensitive business information exchanged.", METHOD_KEYWORD, SUPPORT_KEYWORD, "Verify non-disclosure duties."),
            ChecklistItem("Governing Law", RELEVANCE_EXPECTED, "Identifies applicable legal forum and statute.", METHOD_CUAD, SUPPORT_CUAD, "Confirm mutually acceptable jurisdiction."),
            ChecklistItem("Dispute Resolution", RELEVANCE_CONDITIONAL, "Mandates dispute negotiation or formal arbitration.", METHOD_KEYWORD, SUPPORT_KEYWORD, "Review dispute resolution process."),
            ChecklistItem("Entire Agreement", RELEVANCE_OPTIONAL, "Merger clause superseding prior representations.", METHOD_KEYWORD, SUPPORT_KEYWORD, "Confirm standard boilerplate integration."),
            ChecklistItem("Force Majeure", RELEVANCE_OPTIONAL, "Excuses delays caused by extraordinary events.", METHOD_KEYWORD, SUPPORT_KEYWORD, "Ensure prompt notice is required."),
        ],
    ),
}

# Lookup by alias or name
_TYPE_LOOKUP: Dict[str, ContractTypeDefinition] = {}

def _init_type_lookup():
    for ct in CONTRACT_TYPES.values():
        _TYPE_LOOKUP[ct.type_id.lower()] = ct
        _TYPE_LOOKUP[ct.name.lower()] = ct
        for alias in ct.aliases:
            _TYPE_LOOKUP[alias.lower()] = ct

_init_type_lookup()


def get_contract_type(type_name_or_alias: Optional[str]) -> Optional[ContractTypeDefinition]:
    """Retrieves ContractTypeDefinition by canonical ID, name, or alias."""
    if not type_name_or_alias:
        return None
    cleaned = type_name_or_alias.strip().lower()
    return _TYPE_LOOKUP.get(cleaned)


def list_supported_contract_types() -> List[str]:
    """Returns canonical list of the 10 supported contract type names."""
    return [ct.name for ct in CONTRACT_TYPES.values()]


# =============================================================================
# CONTRACT TYPE SUGGESTION ENGINE
# =============================================================================

def suggest_contract_type(contract_text: Optional[str],
                          extractions: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
    """
    Transparently analyzes contract text (and optional extractions) to suggest
    the most likely contract type from the 10 supported types.

    Features:
    - Analyzes title and preamble with high weighting.
    - Evaluates substantive body terminology.
    - Factors in present clause categories.
    - Returns evidence snippets.
    - Explicitly sets `is_uncertain: True` when confidence is low (< 0.45)
      or when the top candidates are too close to call.
    """
    if not contract_text or not contract_text.strip():
        return {
            "primary_suggestion": None,
            "confidence": 0.0,
            "is_uncertain": True,
            "suggestions": [],
            "explanation": "No contract text provided to determine contract type.",
        }

    header_text = contract_text[:1200]  # First ~1200 chars usually contain title and preamble
    full_text = contract_text

    scores: Dict[str, float] = {ct.type_id: 0.0 for ct in CONTRACT_TYPES.values()}
    evidence_map: Dict[str, List[str]] = {ct.type_id: [] for ct in CONTRACT_TYPES.values()}

    # 1. Check title and preamble patterns (heavy weight: +10)
    for ct_id, ct in CONTRACT_TYPES.items():
        for pat in ct.title_patterns:
            m = re.search(pat, header_text, re.IGNORECASE)
            if m:
                scores[ct_id] += 10.0
                evidence_map[ct_id].append(f"Header match: '{m.group(0)}'")

    # 2. Check substantive body keywords (medium weight: +2 per unique match)
    for ct_id, ct in CONTRACT_TYPES.items():
        for pat in ct.keyword_patterns:
            m = re.search(pat, full_text, re.IGNORECASE)
            if m:
                scores[ct_id] += 2.0
                evidence_map[ct_id].append(f"Keyword match: '{m.group(0)}'")

    # 3. Factor in extracted categories (if provided)
    if extractions:
        extracted_cats = {normalize_category_name(e.get("category", "")) for e in extractions}
        for ct_id, ct in CONTRACT_TYPES.items():
            expected_cats = {
                normalize_category_name(item.clause_name)
                for item in ct.checklist
                if item.relevance == RELEVANCE_EXPECTED
            }
            overlap = extracted_cats.intersection(expected_cats)
            if overlap:
                scores[ct_id] += len(overlap) * 1.5
                evidence_map[ct_id].append(f"Expected categories present: {', '.join(sorted(overlap))}")

    # Rank suggestions
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    total_score = sum(scores.values())

    suggestions = []
    for ct_id, score in ranked:
        if score > 0:
            ct = CONTRACT_TYPES[ct_id]
            suggestions.append({
                "type_id": ct.type_id,
                "name": ct.name,
                "score": round(score, 1),
                "evidence": evidence_map[ct_id],
            })

    if not suggestions or suggestions[0]["score"] == 0:
        return {
            "primary_suggestion": "General Business Agreement",
            "confidence": 0.2,
            "is_uncertain": True,
            "suggestions": [],
            "explanation": "No distinct contract type patterns detected; defaulting to General Business Agreement with high uncertainty.",
        }

    top_item = suggestions[0]
    top_score = top_item["score"]
    second_score = suggestions[1]["score"] if len(suggestions) > 1 else 0.0

    # Calibrate heuristic confidence ratio
    confidence = min(0.95, round(top_score / (top_score + second_score + 5.0), 2)) if top_score > 0 else 0.1

    # Uncertainty flag: low score or margin between top 2 is narrow (< 3.0)
    is_uncertain = (confidence < 0.50) or (len(suggestions) > 1 and (top_score - second_score) < 3.0)

    if is_uncertain:
        explanation = (
            f"Suggested '{top_item['name']}' based on matches, but result is uncertain "
            f"(margin to next candidate is narrow or signals are weak). Please confirm manually."
        )
    else:
        explanation = f"Detected '{top_item['name']}' with strong evidence ({', '.join(top_item['evidence'][:2])})."

    return {
        "primary_suggestion": top_item["name"],
        "confidence": confidence,
        "is_uncertain": is_uncertain,
        "suggestions": suggestions[:4],
        "explanation": explanation,
    }
