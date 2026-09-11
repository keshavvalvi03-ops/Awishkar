"""
Runnable demo. Uses sample extraction output shaped exactly like what a
real CUAD-fine-tuned model would return for Layer 1, so you can demo
Layers 2/3/4 right now without needing model checkpoints or network access.

Run: python demo.py
"""

import json
from pipeline import analyze_contract

# Sample Layer-1 output (mimics what run_cuad_extraction() would return
# from a real contract, e.g. an SEC-filed vendor agreement)
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

if __name__ == "__main__":
    report = analyze_contract(sample_extractions)

    print(f"{'CATEGORY':<28} {'RISK TYPE':<24} {'LEVEL':<8} {'SCORE':<6}")
    print("-" * 70)
    for row in report:
        print(f"{row['category']:<28} {row['risk_type']:<24} "
              f"{row['risk_level']:<8} {row['score']:<6}")

    print("\n=== Detailed explanations ===\n")
    for row in report:
        print(f"[{row['category']}] {row['explanation']}")
        if row["attribution"]:
            print("  Attribution breakdown:")
            print("  " + json.dumps(row["attribution"], indent=2).replace("\n", "\n  "))
        print()
