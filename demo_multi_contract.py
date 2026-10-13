"""
Multi-Contract Type Demonstration Runner
----------------------------------------
Demonstrates contract-specific risk analysis and checklist verification
across all 10 supported commercial contract types:

 1. Service Agreement
 2. Employment Agreement
 3. NDA / Confidentiality Agreement
 4. Software / IT Agreement
 5. Vendor / Supply Agreement
 6. Lease / Rental Agreement
 7. Licensing Agreement
 8. Partnership Agreement
 9. Merger / Acquisition Agreement
10. General Business Agreement

Run:
    python demo_multi_contract.py
    python demo_multi_contract.py --type nda
"""

import sys
import json
from typing import Dict, List, Any

from pipeline import full_analysis
from contract_types import (
    list_supported_contract_types,
    suggest_contract_type,
    STATUS_DETECTED,
    STATUS_NOT_DETECTED,
    STATUS_UNCERTAIN,
    RELEVANCE_EXPECTED,
    RELEVANCE_CONDITIONAL,
)

# Realistic multi-contract sample data
SAMPLE_CONTRACTS: Dict[str, Dict[str, Any]] = {
    "Service Agreement": {
        "text": """
MASTER SERVICES AGREEMENT
This Master Services Agreement is entered into by Acme Corp ("Client") and Apex Solutions LLC ("Consultant").
1. SCOPE OF SERVICES: Consultant shall provide software architecture consulting as detailed in Exhibit A Statement of Work.
2. PAYMENT TERMS: Fees shall be invoiced monthly on Net 30 days terms. Overdue amounts incur interest of 1.5% per month.
3. TERMINATION FOR CAUSE: Either party may terminate upon 30 days written notice of material breach if uncured.
4. LIMITATION OF LIABILITY: In no event shall either party's aggregate liability exceed the total fees paid in the preceding 6 months.
5. CONFIDENTIALITY: Each party agrees to protect all proprietary and confidential information of the other party with reasonable care.
6. GOVERNING LAW: This Agreement shall be governed by and construed in accordance with the laws of the State of Delaware.
        """,
        "extractions": [
            {
                "category": "Scope of Services",
                "text": "Consultant shall provide software architecture consulting as detailed in Exhibit A Statement of Work.",
                "confidence": 0.92,
            },
            {
                "category": "Payment Terms",
                "text": "Fees shall be invoiced monthly on Net 30 days terms.",
                "confidence": 0.89,
            },
            {
                "category": "Termination For Cause",
                "text": "Either party may terminate upon 30 days written notice of material breach if uncured.",
                "confidence": 0.85,
            },
            {
                "category": "Cap On Liability",
                "text": "In no event shall either party's aggregate liability exceed the total fees paid in the preceding 6 months.",
                "confidence": 0.90,
            },
            {
                "category": "Confidentiality",
                "text": "Each party agrees to protect all proprietary and confidential information of the other party with reasonable care.",
                "confidence": 0.94,
            },
            {
                "category": "Governing Law",
                "text": "This Agreement shall be governed by and construed in accordance with the laws of the State of Delaware.",
                "confidence": 0.96,
            },
        ],
    },

    "Employment Agreement": {
        "text": """
EXECUTIVE EMPLOYMENT AGREEMENT
This Agreement is between Innovatech Inc ("Employer") and Jane Doe ("Employee").
1. POSITION & DUTIES: Employee shall serve as VP of Engineering, reporting to the CEO.
2. BASE SALARY: Employer will pay an annual base salary of $190,000, payable semi-monthly.
3. BENEFITS: Employee is entitled to comprehensive health insurance, 401(k) matching, and 20 days paid time off.
4. TERMINATION: Employment is at-will. Either party may terminate with 30 days written notice. Severance of 3 months applies.
5. CONFIDENTIALITY: Employee shall strictly preserve all company trade secrets indefinitely.
6. NON-COMPETE: Employee agrees not to engage in competing enterprise within North America for 12 months post-employment.
7. GOVERNING LAW: Governed by the laws of California.
        """,
        "extractions": [
            {
                "category": "Salary and Compensation",
                "text": "Employer will pay an annual base salary of $190,000, payable semi-monthly.",
                "confidence": 0.95,
            },
            {
                "category": "Benefits",
                "text": "Employee is entitled to comprehensive health insurance, 401(k) matching, and 20 days paid time off.",
                "confidence": 0.91,
            },
            {
                "category": "Employment Termination",
                "text": "Employment is at-will. Either party may terminate with 30 days written notice.",
                "confidence": 0.88,
            },
            {
                "category": "Non-Compete",
                "text": "Employee agrees not to engage in competing enterprise within North America for 12 months post-employment.",
                "confidence": 0.84,
            },
            {
                "category": "Governing Law",
                "text": "Governed by the laws of California.",
                "confidence": 0.96,
            },
        ],
    },

    "NDA / Confidentiality Agreement": {
        "text": """
MUTUAL NON-DISCLOSURE AGREEMENT
This Mutual Non-Disclosure Agreement is entered into by Alpha Ventures and Beta Corp.
1. CONFIDENTIAL INFORMATION: Includes all non-public technical, product, and financial disclosures marked proprietary.
2. STANDARD OF CARE: Receiving Party shall use at least reasonable care to prevent unauthorized dissemination.
3. TERM & SURVIVAL: This Agreement remains in effect for 2 years; non-disclosure duties survive for 5 years thereafter.
4. GOVERNING LAW: Governed by the laws of New York, with exclusive jurisdiction in New York County courts.
        """,
        "extractions": [
            {
                "category": "Confidentiality",
                "text": "Receiving Party shall use at least reasonable care to prevent unauthorized dissemination.",
                "confidence": 0.96,
            },
            {
                "category": "Governing Law",
                "text": "Governed by the laws of New York, with exclusive jurisdiction in New York County courts.",
                "confidence": 0.95,
            },
        ],
    },

    "Software / IT Agreement": {
        "text": """
SAAS SUBSCRIPTION AND CLOUD SERVICES AGREEMENT
By and between CloudMatrix Ltd ("Provider") and Global Enterprise Inc ("Customer").
1. LICENSE GRANT: Provider grants Customer a non-exclusive, worldwide subscription license to access the CloudMatrix SaaS platform.
2. USE RESTRICTIONS: Customer shall not reverse engineer, decompile, or disassemble the platform.
3. SERVICE LEVELS: Provider guarantees a 99.9% monthly uptime commitment. In the event of breach, service credits apply.
4. DATA PROTECTION: Provider complies with GDPR and DPDP, implementing technical and organizational encryption measures.
5. LIMITATION OF LIABILITY: Aggregate liability for either party is capped at fees paid in the past 12 months.
6. UNCAPPED LIABILITY: Liability shall be unlimited without limitation for willful misconduct and IP infringement.
7. GOVERNING LAW: Governed by the laws of England and Wales.
        """,
        "extractions": [
            {
                "category": "License Grant",
                "text": "Provider grants Customer a non-exclusive, worldwide subscription license to access the CloudMatrix SaaS platform.",
                "confidence": 0.91,
            },
            {
                "category": "Licence Restrictions",
                "text": "Customer shall not reverse engineer, decompile, or disassemble the platform.",
                "confidence": 0.89,
            },
            {
                "category": "Service Levels",
                "text": "Provider guarantees a 99.9% monthly uptime commitment. In the event of breach, service credits apply.",
                "confidence": 0.88,
            },
            {
                "category": "Data Privacy",
                "text": "Provider complies with GDPR and DPDP, implementing technical and organizational encryption measures.",
                "confidence": 0.92,
            },
            {
                "category": "Cap On Liability",
                "text": "Aggregate liability for either party is capped at fees paid in the past 12 months.",
                "confidence": 0.84,
            },
            {
                "category": "Uncapped Liability",
                "text": "Liability shall be unlimited without limitation for willful misconduct and IP infringement.",
                "confidence": 0.93,
            },
            {
                "category": "Governing Law",
                "text": "Governed by the laws of England and Wales.",
                "confidence": 0.97,
            },
        ],
    },

    "Vendor / Supply Agreement": {
        "text": """
MASTER MANUFACTURING AND SUPPLY AGREEMENT
Between Precision Components Corp ("Supplier") and Delta Manufacturing Inc ("Buyer").
1. PRODUCT SPECIFICATIONS: Supplier warrants that all micro-assemblies conform strictly to Exhibit A technical tolerances.
2. DELIVERY TERMS: Delivery shall be FOB Destination. Risk of loss passes to Buyer upon physical receipt.
3. INSPECTION: Buyer has 14 days following arrival to inspect goods and issue rejection notice for non-conforming items.
4. REMEDIES: Supplier shall immediately repair or replace defective goods at Supplier's sole cost.
5. LIABILITY CAP: Aggregate liability is capped at $500,000, except for gross negligence.
6. GOVERNING LAW: Governed by the laws of the State of Ohio.
        """,
        "extractions": [
            {
                "category": "Product Specifications and Quality",
                "text": "Supplier warrants that all micro-assemblies conform strictly to Exhibit A technical tolerances.",
                "confidence": 0.90,
            },
            {
                "category": "Delivery Obligations",
                "text": "Delivery shall be FOB Destination. Risk of loss passes to Buyer upon physical receipt.",
                "confidence": 0.88,
            },
            {
                "category": "Inspection and Acceptance",
                "text": "Buyer has 14 days following arrival to inspect goods and issue rejection notice for non-conforming items.",
                "confidence": 0.86,
            },
            {
                "category": "Remedies for Non-Performance",
                "text": "Supplier shall immediately repair or replace defective goods at Supplier's sole cost.",
                "confidence": 0.89,
            },
            {
                "category": "Cap On Liability",
                "text": "Aggregate liability is capped at $500,000, except for gross negligence.",
                "confidence": 0.79,
            },
            {
                "category": "Governing Law",
                "text": "Governed by the laws of the State of Ohio.",
                "confidence": 0.95,
            },
        ],
    },

    "Lease / Rental Agreement": {
        "text": """
COMMERCIAL PROPERTY LEASE AGREEMENT
Landlord: Metro Commercial Properties LLC. Tenant: Nexus Retailers Inc.
1. PREMISES: Suite 400, 100 Main Street, Seattle, WA.
2. BASE RENT: Monthly rent shall be $8,500, payable on the first day of each calendar month.
3. SECURITY DEPOSIT: Tenant shall deposit $17,000 as a damage deposit, refundable within 30 days of surrender.
4. REPAIRS & MAINTENANCE: Tenant maintains interior non-structural elements; Landlord maintains roof, foundation, and HVAC.
5. TERMINATION: Lease term is 36 months. Surrender in good repair, ordinary wear excepted.
6. GOVERNING LAW: Governed by the laws of the State of Washington.
        """,
        "extractions": [
            {
                "category": "Rent",
                "text": "Monthly rent shall be $8,500, payable on the first day of each calendar month.",
                "confidence": 0.94,
            },
            {
                "category": "Security Deposit",
                "text": "Tenant shall deposit $17,000 as a damage deposit, refundable within 30 days of surrender.",
                "confidence": 0.91,
            },
            {
                "category": "Property Maintenance",
                "text": "Tenant maintains interior non-structural elements; Landlord maintains roof, foundation, and HVAC.",
                "confidence": 0.85,
            },
            {
                "category": "Lease Termination",
                "text": "Lease term is 36 months. Surrender in good repair, ordinary wear excepted.",
                "confidence": 0.88,
            },
            {
                "category": "Governing Law",
                "text": "Governed by the laws of the State of Washington.",
                "confidence": 0.97,
            },
        ],
    },

    "Licensing Agreement": {
        "text": """
EXCLUSIVE PATENT LICENSING AGREEMENT
Licensor: BioGen Technologies. Licensee: PharmaGlobal Corp.
1. GRANT OF LICENSE: Licensor grants Licensee an exclusive, worldwide license under the Licensed Patents.
2. ROYALTIES: Licensee shall pay a 4.5% royalty on net sales of therapeutic products.
3. LICENSE FEES: Upfront execution fee of $1,000,000 payable within 10 days of signing.
4. AUDIT RIGHTS: Licensor may inspect Licensee's books once annually upon 30 days written notice.
5. TERMINATION FOR CAUSE: Either party may terminate immediately upon material breach uncured after 60 days.
6. GOVERNING LAW: Governed by the laws of Massachusetts.
        """,
        "extractions": [
            {
                "category": "License Grant",
                "text": "Licensor grants Licensee an exclusive, worldwide license under the Licensed Patents.",
                "confidence": 0.93,
            },
            {
                "category": "Royalties",
                "text": "Licensee shall pay a 4.5% royalty on net sales of therapeutic products.",
                "confidence": 0.91,
            },
            {
                "category": "Licence Fees",
                "text": "Upfront execution fee of $1,000,000 payable within 10 days of signing.",
                "confidence": 0.89,
            },
            {
                "category": "Audit Rights",
                "text": "Licensor may inspect Licensee's books once annually upon 30 days written notice.",
                "confidence": 0.87,
            },
            {
                "category": "Termination For Cause",
                "text": "Either party may terminate immediately upon material breach uncured after 60 days.",
                "confidence": 0.85,
            },
            {
                "category": "Governing Law",
                "text": "Governed by the laws of Massachusetts.",
                "confidence": 0.96,
            },
        ],
    },

    "Partnership Agreement": {
        "text": """
GENERAL PARTNERSHIP AGREEMENT
Partners: Alice Smith and Bob Johnson forming Pioneer Ventures Partnership.
1. CAPITAL CONTRIBUTIONS: Each partner contributes $50,000 initial capital. Future capital calls require unanimous approval.
2. PROFIT & LOSS: Net profits and losses shall be shared equally (50% to Smith, 50% to Johnson).
3. MANAGEMENT RESPONSIBILITIES: Both partners have equal voting rights and authority to bind the partnership.
4. DISSOLUTION: In the event of partner withdrawal, buyout valuation shall be based on certified appraisal.
5. GOVERNING LAW: Governed by the Uniform Partnership Act as enacted in Texas.
        """,
        "extractions": [
            {
                "category": "Capital Contributions",
                "text": "Each partner contributes $50,000 initial capital. Future capital calls require unanimous approval.",
                "confidence": 0.93,
            },
            {
                "category": "Profit and Loss Sharing",
                "text": "Net profits and losses shall be shared equally (50% to Smith, 50% to Johnson).",
                "confidence": 0.92,
            },
            {
                "category": "Partner Responsibilities",
                "text": "Both partners have equal voting rights and authority to bind the partnership.",
                "confidence": 0.87,
            },
            {
                "category": "Partner Exit and Dissolution",
                "text": "In the event of partner withdrawal, buyout valuation shall be based on certified appraisal.",
                "confidence": 0.89,
            },
            {
                "category": "Governing Law",
                "text": "Governed by the Uniform Partnership Act as enacted in Texas.",
                "confidence": 0.94,
            },
        ],
    },

    "Merger / Acquisition Agreement": {
        "text": """
AGREEMENT AND PLAN OF MERGER
Between Apex Holdings Inc ("Buyer") and Target Systems Corp ("Company").
1. PURCHASE PRICE: Total purchase consideration is $45,000,000 cash, subject to working capital adjustments.
2. REPS & WARRANTIES: Company represents that financial statements are prepared in accordance with GAAP and free of material adverse effect.
3. CLOSING CONDITIONS: Closing is conditioned on antitrust clearance and shareholder majority approval.
4. POST-CLOSING COVENANTS: Founders agree to a 24-month transition and non-compete covenant.
5. GOVERNING LAW: Governed by the General Corporation Law of the State of Delaware.
        """,
        "extractions": [
            {
                "category": "Purchase Price",
                "text": "Total purchase consideration is $45,000,000 cash, subject to working capital adjustments.",
                "confidence": 0.94,
            },
            {
                "category": "Representations and Warranties",
                "text": "Company represents that financial statements are prepared in accordance with GAAP.",
                "confidence": 0.92,
            },
            {
                "category": "Closing Conditions",
                "text": "Closing is conditioned on antitrust clearance and shareholder majority approval.",
                "confidence": 0.90,
            },
            {
                "category": "Post-Closing Obligations",
                "text": "Founders agree to a 24-month transition and non-compete covenant.",
                "confidence": 0.86,
            },
            {
                "category": "Non-Compete",
                "text": "Founders agree to a 24-month non-compete covenant.",
                "confidence": 0.88,
            },
            {
                "category": "Governing Law",
                "text": "Governed by the General Corporation Law of the State of Delaware.",
                "confidence": 0.97,
            },
        ],
    },

    "General Business Agreement": {
        "text": """
COMMERCIAL COOPERATION AGREEMENT
By and between Northbridge Traders and Southgate Logistics.
1. PURPOSE & SCOPE: Parties agree to collaborate on cross-border freight distribution across North America.
2. PAYMENT: Fees payable monthly net 30 upon invoice.
3. TERMINATION: Either party may terminate with 60 days notice for convenience or immediately for cause.
4. LIMITATION OF LIABILITY: Neither party liable for consequential damages; aggregate cap is $100,000.
5. ENTIRE AGREEMENT: This document constitutes the entire agreement between the parties.
6. GOVERNING LAW: Governed by the laws of Illinois.
        """,
        "extractions": [
            {
                "category": "Scope of Services",
                "text": "Parties agree to collaborate on cross-border freight distribution across North America.",
                "confidence": 0.85,
            },
            {
                "category": "Payment Terms",
                "text": "Fees payable monthly net 30 upon invoice.",
                "confidence": 0.90,
            },
            {
                "category": "Termination For Convenience",
                "text": "Either party may terminate with 60 days notice for convenience.",
                "confidence": 0.86,
            },
            {
                "category": "Termination For Cause",
                "text": "or immediately for cause.",
                "confidence": 0.82,
            },
            {
                "category": "Cap On Liability",
                "text": "Neither party liable for consequential damages; aggregate cap is $100,000.",
                "confidence": 0.88,
            },
            {
                "category": "Entire Agreement",
                "text": "This document constitutes the entire agreement between the parties.",
                "confidence": 0.94,
            },
            {
                "category": "Governing Law",
                "text": "Governed by the laws of Illinois.",
                "confidence": 0.96,
            },
        ],
    },
}


def run_contract_demo(contract_type_name: str) -> None:
    data = SAMPLE_CONTRACTS.get(contract_type_name)
    if not data:
        print(f"Unknown contract type '{contract_type_name}'.")
        return

    text = data["text"]
    extractions = data["extractions"]

    print("=" * 76)
    print(f"ANALYSIS REPORT: {contract_type_name.upper()}")
    print("=" * 76)

    # 1. Automatic Suggestion Verification
    suggestion = suggest_contract_type(text, extractions)
    print(f"[Contract Type Identification]")
    print(f"  Suggested: {suggestion['primary_suggestion']} (Confidence: {suggestion['confidence']:.0%})")
    print(f"  Uncertainty flag: {suggestion['is_uncertain']}")
    print(f"  Evidence: {suggestion['explanation']}")
    print()

    # 2. Run Full 6-Layer Pipeline with Contract-Specific Checklist
    report = full_analysis(extractions, raw_contract_text=text, contract_type=contract_type_name)

    print(f"{'CATEGORY':<28} {'RISK TYPE':<24} {'LEVEL':<8} {'SCORE':<6}")
    print("-" * 76)
    for row in report["clauses"]:
        print(f"{row['category']:<28} {row['risk_type']:<24} {row['risk_level']:<8} {row['score']:<6}")

    print("\n[Contract-Specific Checklist Summary]")
    detected_count = sum(1 for c in report["contract_checklist"] if c["status"] == STATUS_DETECTED)
    missing_expected = [
        c for c in report["contract_checklist"]
        if c["status"] == STATUS_NOT_DETECTED and c["relevance"] == RELEVANCE_EXPECTED
    ]
    missing_cond = [
        c for c in report["contract_checklist"]
        if c["status"] == STATUS_NOT_DETECTED and c["relevance"] == RELEVANCE_CONDITIONAL
    ]

    print(f"  Detected Clauses: {detected_count}/{len(report['contract_checklist'])}")
    if missing_expected:
        print(f"  Expected Clauses Not Detected ({len(missing_expected)}):")
        for m in missing_expected:
            print(f"    - [{m['clause_name']}]: {m['reason']}")
            print(f"      Action: {m['recommended_action']}")
    else:
        print("  All Expected clauses detected.")

    if missing_cond:
        print(f"  Conditional Clauses Not Detected ({len(missing_cond)}):")
        for m in missing_cond[:3]:
            print(f"    - [{m['clause_name']}]: {m['reason']}")

    # 3. Contract Risk Summary
    cr = report["contract_risk"]
    print("\n[Contract-Level Risk & Interactions]")
    print(f"  Risk Score: {cr['contract_score']}/10 ({cr['contract_level']})")
    print(f"  Base Weighted Score: {cr['base_weighted_score']}, Bonus: +{cr['interaction_bonus']}")
    print(f"  Average Extraction Confidence: {cr['average_confidence']:.0%}")
    if cr["interactions"]:
        print("  Triggered Interactions:")
        for inter in cr["interactions"]:
            print(f"    * {inter['name']} (+{inter['bonus']}): {inter['message']}")
    else:
        print("  Triggered Interactions: None")
    print()


def main():
    target_type = None
    if len(sys.argv) > 1:
        if sys.argv[1] == "--type" and len(sys.argv) > 2:
            arg = sys.argv[2].lower()
            for ct_name in SAMPLE_CONTRACTS.keys():
                if arg in ct_name.lower():
                    target_type = ct_name
                    break

    if target_type:
        run_contract_demo(target_type)
    else:
        print(f"Running multi-contract demo across all {len(SAMPLE_CONTRACTS)} supported contract types...\n")
        for ct_name in SAMPLE_CONTRACTS.keys():
            run_contract_demo(ct_name)


if __name__ == "__main__":
    main()
