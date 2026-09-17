"""
Runnable demo of the full 6-layer pipeline. Uses sample extraction output
shaped like real CUAD model output (Layer 1), plus a short synthetic
contract snippet for the Layer 5 heuristic checks.

Run: python demo.py
"""

import json
from pipeline import full_analysis

# Sample Layer-1 output (mimics what run_cuad_extraction() would return
# from a real contract, e.g. an SEC-filed vendor agreement). Deliberately
# includes Uncapped Liability + Exclusivity-style lock-in combinations so
# Layer 6's interaction rules have something to fire on.
sample_extractions = [
    {
        "category": "Uncapped Liability",
        "text": "Vendor's liability under this Agreement shall be unlimited "
                "and without limitation for breaches of confidentiality.",
        "confidence": 0.91,
    },
    {
        "category": "Cap On Liability",
        "text": "In no event shall either party's liability exceed the fees "
                "paid in the preceding 12 months.",
        "confidence": 0.62,
    },
    {
        "category": "Non-Compete",
        "text": "Client shall not engage any competing service provider for "
                "a period of 24 months following termination.",
        "confidence": 0.78,
    },
    {
        "category": "Renewal Term",
        "text": "This Agreement shall automatically renew for successive "
                "one-year terms unless either party provides 30 days notice.",
        "confidence": 0.55,
    },
    {
        "category": "Termination For Convenience",
        "text": "Either party may terminate this Agreement at any time and "
                "without notice for its sole discretion.",
        "confidence": 0.88,
    },
    {
        "category": "Parties",
        "text": "This Agreement is entered into between ABC Corp and XYZ Ltd.",
        "confidence": 0.95,
    },
]

# Raw contract text stand-in, used only by Layer 5's heuristic keyword
# checks (Confidentiality / Dispute Resolution / Force Majeure / Data
# Privacy -- none of which are CUAD categories, so Layer 1 can't detect
# them at all; these come from a plain text search instead).
sample_raw_contract_text = """
This Agreement is entered into between ABC Corp and XYZ Ltd.
Vendor's liability under this Agreement shall be unlimited and without
limitation for breaches of confidentiality. In no event shall either
party's liability exceed the fees paid in the preceding 12 months.
Client shall not engage any competing service provider for a period of
24 months following termination. This Agreement shall automatically
renew for successive one-year terms unless either party provides 30
days notice. Either party may terminate this Agreement at any time and
without notice for its sole discretion.
"""

if __name__ == "__main__":
    report = full_analysis(sample_extractions, sample_raw_contract_text)

    print("=" * 70)
    print("LAYERS 2-4: PER-CLAUSE RESULTS")
    print("=" * 70)
    print(f"{'CATEGORY':<28} {'RISK TYPE':<24} {'LEVEL':<8} {'SCORE':<6}")
    print("-" * 70)
    for row in report["clauses"]:
        print(f"{row['category']:<28} {row['risk_type']:<24} "
              f"{row['risk_level']:<8} {row['score']:<6}")

    print("\n=== Detailed explanations ===\n")
    for row in report["clauses"]:
        print(f"[{row['category']}] {row['explanation']}")
        if row["attribution"]:
            print("  Attribution breakdown:")
            print("  " + json.dumps(row["attribution"], indent=2).replace("\n", "\n  "))
        print()

    print("=" * 70)
    print("LAYER 5: MISSING CLAUSE DETECTION")
    print("=" * 70)
    if not report["missing_clauses"]:
        print("No missing essential clauses detected.")
    for finding in report["missing_clauses"]:
        print(f"[{finding['detection_method']}] {finding['clause_name']}: {finding['message']}")

    print("\n" + "=" * 70)
    print("LAYER 6: CROSS-CLAUSE INTERACTION + CONTRACT-LEVEL RISK")
    print("=" * 70)
    cr = report["contract_risk"]
    print(f"Contract-level risk score: {cr['contract_score']} / 10 ({cr['contract_level']})")
    print(f"  base weighted score: {cr['base_weighted_score']}, "
          f"interaction bonus: +{cr['interaction_bonus']}")
    print(f"  average extraction confidence: {cr['average_confidence']:.0%}")
    if cr["note"]:
        print(f"  NOTE: {cr['note']}")
    print("\nTriggered interactions:")
    if not cr["interactions"]:
        print("  None.")
    for interaction in cr["interactions"]:
        print(f"  - {interaction['name']} (+{interaction['bonus']}): {interaction['message']}")
