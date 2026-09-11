"""
Layer 2: Risk Classification Taxonomy (rebuilt on verified CUAD data)
-----------------------------------------------------------------------
SOURCE VERIFICATION NOTE:
The category names and annotator questions below are taken from CUAD's
actual category_descriptions.csv (TheAtticusProject/cuad), cross-checked
against Stanford's LegalBench mirror of that same file
(hazyresearch.stanford.edu/legalbench/tasks/cuad_*.html), which packages
each CUAD category as a binary classification task using CUAD's own
annotator question. Category names marked VERIFIED below use the exact
question wording from that source. The rest use CUAD's real category
names (confirmed against the full 41-category list) with a description
consistent with CUAD's published category definitions.

CORRECTION FROM AN EARLIER VERSION OF THIS FILE:
An earlier draft of this taxonomy included a category called
"Indemnification". That is NOT one of CUAD's 41 categories -- it was an
error (an assumption carried over from generic contract-risk vocabulary,
not from the actual dataset). It has been removed here.

CUAD's real 41 categories are: Document Name, Parties, Agreement Date,
Effective Date, Expiration Date, Renewal Term, Notice Period To Terminate
Renewal, Governing Law, Most Favored Nation, Non-Compete, Exclusivity,
No-Solicit Of Customers, Competitive Restriction Exception, No-Solicit Of
Employees, Non-Disparagement, Termination For Convenience, Rofr/Rofo/Rofn,
Change Of Control, Anti-Assignment, Revenue/Profit Sharing, Price
Restrictions, Minimum Commitment, Volume Restriction, IP Ownership
Assignment, Joint IP Ownership, License Grant, Non-Transferable License,
Affiliate License-Licensor, Affiliate License-Licensee, Unlimited/All-
You-Can-Eat-License, Irrevocable Or Perpetual License, Source Code
Escrow, Post-Termination Services, Audit Rights, Uncapped Liability,
Cap On Liability, Liquidated Damages, Warranty Duration, Insurance,
Covenant Not To Sue, Third Party Beneficiary.

CUAD does NOT classify risk severity for any of these -- that is this
project's contribution, built on top.
"""

# category name -> {risk_type, base_severity (0-10), source, cuad_question}
# source: "VERIFIED" = exact CUAD annotator question text (see citations
#         below); "CUAD_CATEGORY" = real CUAD category, description
#         consistent with the dataset's published category definition.
RISK_TAXONOMY = {

    # --- Financial Risk ---
    "Uncapped Liability": {
        "risk_type": "Financial Risk",
        "base_severity": 9,
        "source": "VERIFIED",
        "cuad_question": (
            "Does the clause specify that a party's liability is uncapped "
            "upon the breach of its obligation in the contract? This also "
            "includes uncap liability for a particular type of breach such "
            "as IP infringement or breach of confidentiality obligation."
        ),
    },
    "Cap On Liability": {
        "risk_type": "Financial Risk",
        "base_severity": 3,
        "source": "VERIFIED",
        "cuad_question": (
            "Does the clause specify a cap on liability upon the breach of "
            "a party's obligation? This includes time limitation for the "
            "counterparty to bring claims or maximum amount for recovery."
        ),
    },
    "Liquidated Damages": {
        "risk_type": "Financial Risk",
        "base_severity": 6,
        "source": "CUAD_CATEGORY",
        "cuad_question": (
            "Does the clause specify liquidated damages, i.e. a predefined "
            "amount payable upon a specified type of breach?"
        ),
    },
    "Insurance": {
        "risk_type": "Financial Risk",
        "base_severity": 4,
        "source": "CUAD_CATEGORY",
        "cuad_question": (
            "Does the clause create a requirement for insurance that must "
            "be maintained by one party for the benefit of the counterparty?"
        ),
    },

    # --- Restrictive Covenant Risk ---
    "Non-Compete": {
        "risk_type": "Restrictive Covenant Risk",
        "base_severity": 7,
        "source": "VERIFIED",
        "cuad_question": (
            "Does the clause restrict the ability of a party to compete "
            "with the counterparty or operate in a certain geography or "
            "business or technology sector?"
        ),
    },
    "Exclusivity": {
        "risk_type": "Restrictive Covenant Risk",
        "base_severity": 6,
        "source": "CUAD_CATEGORY",
        "cuad_question": (
            "Is there an exclusive dealing commitment with the counterparty? "
            "This includes a commitment to procure goods or services only "
            "from the counterparty."
        ),
    },
    "No-Solicit Of Customers": {
        "risk_type": "Restrictive Covenant Risk",
        "base_severity": 5,
        "source": "CUAD_CATEGORY",
        "cuad_question": (
            "Does the clause restrict a party from contracting or "
            "soliciting customers of the counterparty?"
        ),
    },
    "No-Solicit Of Employees": {
        "risk_type": "Restrictive Covenant Risk",
        "base_severity": 5,
        "source": "CUAD_CATEGORY",
        "cuad_question": (
            "Does the clause restrict a party's soliciting or hiring "
            "employees or contractors of the counterparty?"
        ),
    },
    "Competitive Restriction Exception": {
        "risk_type": "Restrictive Covenant Risk",
        "base_severity": -3,  # this category REDUCES risk (it's a carve-out)
        "source": "VERIFIED",
        "cuad_question": (
            "Does the clause mention exceptions or carveouts to Non-Compete, "
            "Exclusivity and No-Solicit of Customers?"
        ),
    },
    "Non-Disparagement": {
        "risk_type": "Restrictive Covenant Risk",
        "base_severity": 3,
        "source": "CUAD_CATEGORY",
        "cuad_question": (
            "Does the clause require a party not to disparage the "
            "counterparty?"
        ),
    },
    "Most Favored Nation": {
        "risk_type": "Restrictive Covenant Risk",
        "base_severity": 6,
        "source": "VERIFIED",
        "cuad_question": (
            "Does the clause state that if a third party gets better terms "
            "on the licensing or sale of technology/goods/services described "
            "in the contract, the buyer of such technology/goods/services "
            "under the contract shall be entitled to those better terms?"
        ),
    },

    # --- Termination Risk ---
    "Termination For Convenience": {
        "risk_type": "Termination Risk",
        "base_severity": 5,
        "source": "CUAD_CATEGORY",
        "cuad_question": (
            "Can a party terminate this contract without cause (solely by "
            "giving a prior notice)?"
        ),
    },
    "Change Of Control": {
        "risk_type": "Termination Risk",
        "base_severity": 5,
        "source": "CUAD_CATEGORY",
        "cuad_question": (
            "Does one party have the right to terminate or is consent or "
            "notice required of the counterparty if such party undergoes a "
            "change of control, such as a merger, stock sale, transfer of "
            "all/substantially all assets, or reorganization?"
        ),
    },
    "Anti-Assignment": {
        "risk_type": "Termination Risk",
        "base_severity": 4,
        "source": "VERIFIED",
        "cuad_question": (
            "Does the clause require consent or notice of a party if the "
            "contract is assigned to a third party?"
        ),
    },
    "Rofr/Rofo/Rofn": {
        "risk_type": "Termination Risk",
        "base_severity": 4,
        "source": "CUAD_CATEGORY",
        "cuad_question": (
            "Is there a right of first refusal, right of first offer, or "
            "right of first negotiation applicable to some assets of one "
            "party to the counterparty?"
        ),
    },

    # --- Renewal Risk ---
    "Renewal Term": {
        "risk_type": "Renewal Risk",
        "base_severity": 4,
        "source": "CUAD_CATEGORY",
        "cuad_question": (
            "Does the contract automatically renew for an additional period "
            "if neither party terminates? What is the renewal term?"
        ),
    },
    "Notice Period To Terminate Renewal": {
        "risk_type": "Renewal Risk",
        "base_severity": 3,
        "source": "CUAD_CATEGORY",
        "cuad_question": (
            "What is the notice period required to terminate renewal?"
        ),
    },

    # --- Commercial Risk ---
    "Revenue/Profit Sharing": {
        "risk_type": "Commercial Risk",
        "base_severity": 5,
        "source": "CUAD_CATEGORY",
        "cuad_question": (
            "Is one party required to share revenue or profit with the "
            "counterparty for any technology, goods, or services?"
        ),
    },
    "Price Restrictions": {
        "risk_type": "Commercial Risk",
        "base_severity": 5,
        "source": "CUAD_CATEGORY",
        "cuad_question": (
            "Is there a restriction on the ability of a party to raise or "
            "reduce prices of technology, goods, or services provided?"
        ),
    },
    "Minimum Commitment": {
        "risk_type": "Commercial Risk",
        "base_severity": 6,
        "source": "CUAD_CATEGORY",
        "cuad_question": (
            "Is there a minimum order size or minimum amount or units per "
            "time period that one party must buy from the counterparty?"
        ),
    },
    "Volume Restriction": {
        "risk_type": "Commercial Risk",
        "base_severity": 4,
        "source": "CUAD_CATEGORY",
        "cuad_question": (
            "Is there a fee increase or consent requirement if one party's "
            "use of the product/services exceeds certain threshold?"
        ),
    },

    # --- IP Risk ---
    "IP Ownership Assignment": {
        "risk_type": "IP Risk",
        "base_severity": 7,
        "source": "CUAD_CATEGORY",
        "cuad_question": (
            "Does intellectual property created by one party become the "
            "property of the counterparty, either per the terms of the "
            "contract or upon the occurrence of certain events?"
        ),
    },
    "Joint IP Ownership": {
        "risk_type": "IP Risk",
        "base_severity": 5,
        "source": "CUAD_CATEGORY",
        "cuad_question": (
            "Is there any clause providing for joint or shared ownership of "
            "intellectual property between the parties to the contract?"
        ),
    },
    "License Grant": {
        "risk_type": "IP Risk",
        "base_severity": 2,  # neutral by default; risk depends on scope
        "source": "CUAD_CATEGORY",
        "cuad_question": (
            "Does the clause contain a license granted by one party to its "
            "counterparty?"
        ),
    },
    "Non-Transferable License": {
        "risk_type": "IP Risk",
        "base_severity": 3,
        "source": "CUAD_CATEGORY",
        "cuad_question": (
            "Does the clause limit the ability of a party to transfer the "
            "license being granted to a third party?"
        ),
    },
    "Affiliate License-Licensor": {
        "risk_type": "IP Risk",
        "base_severity": 3,
        "source": "VERIFIED",
        "cuad_question": (
            "Does the clause describe a license grant by affiliates of the "
            "licensor or that includes intellectual property of affiliates "
            "of the licensor?"
        ),
    },
    "Affiliate License-Licensee": {
        "risk_type": "IP Risk",
        "base_severity": 3,
        "source": "VERIFIED",
        "cuad_question": (
            "Does the clause describe a license grant to a licensee (incl. "
            "sublicensor) and the affiliates of such licensee/sublicensor?"
        ),
    },
    "Unlimited/All-You-Can-Eat-License": {
        "risk_type": "IP Risk",
        "base_severity": 6,
        "source": "CUAD_CATEGORY",
        "cuad_question": (
            "Is there a clause granting one party an 'enterprise,' "
            "'all you can eat,' or unlimited usage license?"
        ),
    },
    "Irrevocable Or Perpetual License": {
        "risk_type": "IP Risk",
        "base_severity": 6,
        "source": "CUAD_CATEGORY",
        "cuad_question": (
            "Does the contract contain a license grant that is irrevocable "
            "or perpetual?"
        ),
    },
    "Source Code Escrow": {
        "risk_type": "IP Risk",
        "base_severity": 4,
        "source": "CUAD_CATEGORY",
        "cuad_question": (
            "Is source code escrow required to be deposited for a licensed "
            "technology, e.g. in case the licensor becomes insolvent?"
        ),
    },

    # --- Legal / Compliance Risk ---
    "Covenant Not To Sue": {
        "risk_type": "Legal/Compliance Risk",
        "base_severity": 5,
        "source": "CUAD_CATEGORY",
        "cuad_question": (
            "Is a party restricted from contesting the validity of the "
            "counterparty's ownership of intellectual property or "
            "otherwise bringing a claim against the counterparty for "
            "matters unrelated to the contract?"
        ),
    },
    "Third Party Beneficiary": {
        "risk_type": "Legal/Compliance Risk",
        "base_severity": 3,
        "source": "CUAD_CATEGORY",
        "cuad_question": (
            "Is there a non-contracting party who is a beneficiary to some "
            "or all of the clauses in the contract, and therefore able to "
            "enforce its rights against a contracting party?"
        ),
    },
    "Audit Rights": {
        "risk_type": "Legal/Compliance Risk",
        "base_severity": 3,
        "source": "CUAD_CATEGORY",
        "cuad_question": (
            "Does a party have the right to audit the books, records, or "
            "physical locations of the counterparty to ensure compliance "
            "with the contract?"
        ),
    },
    "Warranty Duration": {
        "risk_type": "Legal/Compliance Risk",
        "base_severity": 3,
        "source": "CUAD_CATEGORY",
        "cuad_question": (
            "What is the duration of any warranty against defects or "
            "errors in technology, products, or services provided under "
            "the contract?"
        ),
    },
    "Post-Termination Services": {
        "risk_type": "Termination Risk",
        "base_severity": 3,
        "source": "CUAD_CATEGORY",
        "cuad_question": (
            "Is a party subject to obligations after the termination or "
            "expiration of the contract, including any post-termination "
            "transition, payment, transfer of IP, wind-down, last-buy, or "
            "similar commitments?"
        ),
    },
}

# Keyword modifiers: words/phrases inside the extracted clause span that
# increase (or, for exculpatory language, decrease) severity beyond the
# category's base score. Weights are additive.
KEYWORD_MODIFIERS = {
    "unlimited": 2,
    "uncapped": 2,
    "sole discretion": 2,
    "perpetual": 2,
    "irrevocable": 2,
    "without limitation": 2,
    "in perpetuity": 2,
    "without notice": 1,
    "at any time": 1,
    "any and all": 1,
    "automatically renew": 1,
    "not liable": -1,     # exculpatory language can reduce exposure
    "limited to": -2,     # explicit cap language reduces severity
    "except": -1,         # carve-out language typically narrows exposure
}

RISK_LEVEL_THRESHOLDS = {
    "High": 7,
    "Medium": 4,
    # anything below "Medium" threshold is "Low"
}


def get_risk_level(score: float) -> str:
    """Convert a 0-10 severity score into a Low/Medium/High label."""
    if score >= RISK_LEVEL_THRESHOLDS["High"]:
        return "High"
    if score >= RISK_LEVEL_THRESHOLDS["Medium"]:
        return "Medium"
    return "Low"
