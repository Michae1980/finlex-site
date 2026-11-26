#!/usr/bin/env python3
"""
补全剩余全部现行国际准则、审计/审阅/鉴证/相关服务准则与 IFRIC/SIC 解释的段落号索引深度技术精要，
实现国际准则全板块 100% 深度覆盖。
"""

from __future__ import annotations

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INTL_DATA_DIR = PROJECT_ROOT / "intl_data"


REMAINING_ENRICHMENTS: dict[str, dict[str, list[tuple[str, str, str]]]] = {
    "ifrs_accounting.json": {
        "IFRS 1": [
            ("IFRS 1.6–21", "First-Time Adoption: Opening IFRS Statement & Exemptions", "Prepare an opening IFRS statement of financial position at the date of transition applying IFRS policies retrospectively (IFRS 1.7–10), subject to mandatory exceptions (estimates, derecognition, hedge accounting, NCI, IFRS 1.B1–B12) and optional exemptions (deemed cost for PPE, cumulative translation differences, leases, IFRS 1.C–D); present equity and profit reconciliations from previous GAAP (IFRS 1.24, converged with China CAS 38)."),
        ],
        "IFRS 6": [
            ("IFRS 6.6–21", "Exploration & Evaluation Assets and Impairment Triggers", "Permits entities to retain existing accounting policies for exploration and evaluation (E&E) expenditures pending comprehensive IASB review (IFRS 6.9); requires testing E&E assets for impairment whenever facts and circumstances indicate carrying amount may exceed recoverable amount (IFRS 6.18–20, e.g., expiring rights, no budgeted further exploration)."),
        ],
        "IFRS 12": [
            ("IFRS 12.7–31", "Disclosures of Interests in Subsidiaries, JVs, Associates & Structured Entities", "Requires disclosure of significant judgements in determining control, joint control, or significant influence (IFRS 12.7–9), summarised financial information for material NCI, joint ventures, and associates (IFRS 12.12, 21), and nature/risks of interests in unconsolidated structured entities (IFRS 12.24–31, converged with China CAS 41)."),
        ],
        "IAS 1": [
            ("IAS 1.10–138", "Complete Set of Financial Statements & Going Concern (Superseded by IFRS 18 in 2027)", "Prescribes overall requirements for complete financial statements, fair presentation, going concern (IAS 1.25–26), current vs. non-current liability classification including covenant conditions (IAS 1.69–76, amended 2020/2022), and material accounting policy disclosures (IAS 1.117). Replaced by IFRS 18 for annual periods beginning on or after 1 January 2027."),
        ],
        "IAS 26": [
            ("IAS 26.13–36", "Defined Contribution vs. Defined Benefit Retirement Plan Reporting", "Specifies reporting by retirement benefit plans themselves: defined contribution plans report net assets available for benefits and funding policy (IAS 26.13); defined benefit plans additionally report the actuarial present value of promised retirement benefits, distinguishing vested and non-vested benefits (IAS 26.17–26, aligned with China CAS 10)."),
        ],
        "IAS 27": [
            ("IAS 27.10–17", "Separate Financial Statements: Investment Measurement Options", "In separate financial statements, account for investments in subsidiaries, joint ventures, and associates at: (a) cost, (b) in accordance with IFRS 9 (fair value), or (c) using the equity method under IAS 28 — applied consistently per category (IAS 27.10). Dividends are recognised in P&L when right to receive is established (IAS 27.12)."),
        ],
        "IAS 29": [
            ("IAS 29.3–38", "Hyperinflationary Economies: Constant Purchasing Power Restatement", "Applies when functional currency is hyperinflationary (indicators include cumulative 3-year inflation approaching or exceeding 100%, IAS 29.3). Restate non-monetary items and all P&L items using a general price index to the measuring unit current at the reporting date; recognise net monetary position gain/loss in P&L (IAS 29.27)."),
        ],
        "IAS 34": [
            ("IAS 34.8–41", "Interim Financial Reporting: Condensed Statements & Discrete-Period Approach", "Minimum content comprises condensed balance sheet, P&L/OCI, changes in equity, cash flows, and selected explanatory notes covering significant events/transactions since last annual report (IAS 34.8–15C). Apply the same accounting policies as annual statements on a discrete-period basis (e.g., do not smooth seasonal costs, IAS 34.28–39, converged with China CAS 32)."),
        ],
        "IAS 41": [
            ("IAS 41.10–33", "Biological Assets & Agricultural Produce at Fair Value Less Costs to Sell", "Measure biological assets (excluding bearer plants accounted for under IAS 16) and agricultural produce at harvest at Fair Value Less Costs to Sell, with changes recognised in P&L (IAS 41.12–13, 26). Cost model permitted only if fair value is clearly unreliable on initial recognition (IAS 41.30). Note: China CAS 5 uses Cost Model as default."),
        ],
        "IFRS for SMEs": [
            ("IFRS for SMEs (3rd Ed.)", "Standalone Simplified Standard for Non-Publicly Accountable Entities", "Self-contained 35-section standard tailored for entities without public accountability: omits EPS/segment/interim reporting, simplifies financial instruments and revenue/leases alignment (updated in 2025 Third Edition), and cuts disclosure volume by >85% compared with full IFRS."),
        ],
        # 20 Active IFRIC & SIC Interpretations
        "IFRIC 1": [("IFRIC 1.4–8", "Changes in Decommissioning Liabilities", "Under Cost Model, add/deduct changes in decommissioning/restoration liabilities (IAS 37) to/from the related PPE asset cost (IAS 16) and depreciate prospectively; unwinding of discount is always recognised in P&L as finance cost.")],
        "IFRIC 2": [("IFRIC 2.5–11", "Members' Shares in Co-operative Entities", "Members' shares are equity ONLY if the entity has an unconditional right to refuse redemption, or local law/charter prohibits redemption; otherwise classify as financial liabilities under IAS 32.")],
        "IFRIC 5": [("IFRIC 5.7–13", "Decommissioning & Rehabilitation Funds", "Recognise contributor's obligation to pay decommissioning costs as a liability and interest in the fund separately as a reimbursement right (IAS 37) unless contributor is not liable if the fund fails to pay.")],
        "IFRIC 6": [("IFRIC 6.8–9", "Waste Electrical & Electronic Equipment (WEEE) Liabilities", "Participation in the market during the measurement period is the obligating event under IAS 37.14 triggering recognition of a liability for historical household WEEE waste management.")],
        "IFRIC 7": [("IFRIC 7.3–5", "Restatement Approach under IAS 29", "When an entity's economy becomes hyperinflationary, apply IAS 29 as if the economy had always been hyperinflationary and remeasure deferred tax items under IAS 12 after restating non-monetary carrying amounts.")],
        "IFRIC 10": [("IFRIC 10.8–9", "Interim Reporting & Impairment Reversal Prohibition", "An entity shall NOT reverse an impairment loss recognised in a previous interim period in respect of goodwill (IAS 36) at a subsequent annual or interim reporting date.")],
        "IFRIC 12": [("IFRIC 12.11–27", "Service Concession Arrangements (BOT / PPP Models)", "Infrastructure within scope is NOT recognised as operator's PPE; recognise a financial asset (unconditional contractual right to receive cash from grantor, IFRS 9) or an intangible asset (right to charge public users, IAS 38), with construction/upgrade revenue under IFRS 15 (aligned with China MOF Interpretation No. 14).")],
        "IFRIC 14": [("IFRIC 14.7–24", "IAS 19 Defined Benefit Asset Ceiling & Minimum Funding", "Clarifies when refunds or reductions in future contributions are 'available' to support recognising a defined benefit surplus, and when minimum funding requirements create an additional onerous liability.")],
        "IFRIC 16": [("IFRIC 16.10–17", "Hedges of a Net Investment in a Foreign Operation", "Net investment hedge accounting applies only to FX differences between functional currency of the foreign operation and functional currency of any parent entity (not presentation currency); hedging instrument may be held by any entity within the group.")],
        "IFRIC 17": [("IFRIC 17.10–16", "Distributions of Non-Cash Assets to Owners", "Measure dividend payable at fair value of non-cash assets to be distributed; remeasure at each reporting date through equity; on settlement recognise difference between carrying amount of assets distributed and dividend payable in P&L.")],
        "IFRIC 19": [("IFRIC 19.5–11", "Extinguishing Financial Liabilities with Equity Instruments", "Debt-for-equity swaps: measure equity instruments issued at their fair value (or fair value of liability extinguished if more reliable) and recognise the difference against the carrying amount of the liability in P&L.")],
        "IFRIC 20": [("IFRIC 20.7–16", "Stripping Costs in Surface Mine Production Phase", "Capitalise production-phase waste-removal stripping costs as a 'stripping activity asset' (part of existing mine PPE/intangible) when providing improved access to an identified ore body; depreciate over expected useful life of that ore component.")],
        "IFRIC 21": [("IFRIC 21.8–14", "Levies: Obligating Event Recognition", "Recognise a liability for a government levy ONLY when the activity triggering payment (as identified by legislation) occurs; do NOT accrue progressively before a minimum threshold is reached.")],
        "IFRIC 22": [("IFRIC 22.8–9", "Foreign Currency Advance Consideration", "For determining the spot exchange rate on initial recognition of the related asset, expense, or income, the date of the transaction is the date on which the entity initially recognises the non-monetary prepayment asset or deferred income liability (no retranslation later).")],
        "IFRIC 23": [("IFRIC 23.9–14", "Uncertainty over Income Tax Treatments", "Assume tax authorities will examine with full knowledge of all relevant information. If probable (>50%) that the authority will accept the treatment, reflect it consistently; otherwise reflect uncertainty using the most likely amount or expected value (IAS 12).")],
        "SIC-7": [("SIC-7.3–4", "Introduction of the Euro", "Clarifies that IAS 21 requirements apply strictly to the changeover to the Euro, with FX differences on monetary items recognised in P&L and cumulative translation reserves preserved until disposal.")],
        "SIC-10": [("SIC-10.3", "Government Assistance — No Specific Operating Relation", "Government assistance aimed at encouraging long-term business activity in specific regions or sectors qualifies as a government grant under IAS 20 and must NOT be credited directly to shareholders' equity.")],
        "SIC-25": [("SIC-25.4", "Income Taxes — Changes in Tax Status", "Include current and deferred tax consequences of a change in tax status of an entity or its shareholders in P&L unless related to transactions/events recognised directly in OCI or equity.")],
        "SIC-29": [("SIC-29.6–7", "Service Concession Arrangements: Disclosures", "Requires operators and grantors to disclose arrangement descriptions, significant terms affecting cash flows, renewal/termination rights, and obligations to acquire/build/hand back concession assets.")],
        "SIC-32": [("SIC-32.7–10", "Intangible Assets — Web Site Costs", "Planning stage costs are expensed; application/infrastructure development and graphical design costs are capitalised under IAS 38.57 ONLY if probable future economic benefits (e.g., direct online ordering revenue) are demonstrated; purely promotional websites are expensed.")],
    },
    "iaasb_auditing.json": {
        "ISA 210": [("ISA 210.6–17", "Preconditions for an Audit & Engagement Letter", "Establish whether the financial reporting framework is acceptable and obtain management's agreement on its responsibilities (FS preparation, internal control, unrestricted access to information) in a written engagement letter (ISA 210.6, 10).")],
        "ISA 220 (Revised)": [("ISA 220.13–41", "Engagement-Level Quality Management", "Engagement partner takes overall responsibility for managing and achieving audit quality, including ethical/independence compliance, sufficient appropriate resources, direction/supervision/review, consultation on difficult matters, and stand-back before dating the report.")],
        "ISA 230": [("ISA 230.7–16", "Audit Documentation & 60-Day Assembly Rule", "Prepare timely documentation sufficient for an experienced auditor with no prior connection to understand procedures, evidence, and significant judgements (ISA 230.8). Assemble the final audit file on a timely basis — ordinarily not more than 60 days after the auditor's report date (ISA 230.A21).")],
        "ISA 250 (Revised)": [("ISA 250.13–29", "Consideration of Laws & Regulations (Direct vs. Indirect Effect)", "Distinguish laws with direct effect on material financial statement amounts (e.g., tax/pension laws — obtain sufficient appropriate evidence) from other laws where non-compliance could result in material fines/cessation (perform specified inquiry and inspection procedures; report NOCLAR to TCWG/regulators).")],
        "ISA 260 (Revised)": [("ISA 260.11–22", "Two-Way Communication with Those Charged with Governance", "Communicate auditor responsibilities, planned scope and timing (including significant risks), significant findings (accounting policies, estimates, difficulties, uncorrected misstatements), and independence statement for listed entities (ISA 260.14–17).")],
        "ISA 265": [("ISA 265.7–11", "Communicating Internal Control Deficiencies", "Determine whether identified deficiencies individually or in combination constitute Significant Deficiencies; communicate Significant Deficiencies in writing on a timely basis to TCWG and management (ISA 265.9–10).")],
        "ISA 300": [("ISA 300.7–12", "Overall Audit Strategy & Detailed Audit Plan", "Establish an overall audit strategy setting scope, timing, and direction (resources, materiality, key risk areas) and develop a detailed audit plan specifying nature, timing, and extent of risk assessment and further audit procedures.")],
        "ISA 402": [("ISA 402.9–22", "Auditing Entities Using Service Organizations", "Understand services provided by the service organization; obtain Type 1 (design) or Type 2 (design + operating effectiveness) assurance report under ISAE 3402, or perform direct procedures at the service organization when relying on its controls.")],
        "ISA 450": [("ISA 450.5–15", "Accumulation & Evaluation of Misstatements", "Accumulate all misstatements other than those clearly trivial (ISA 450.5), request management to correct all misstatements, evaluate whether uncorrected misstatements are material individually or in aggregate (including qualitative factors), and obtain written representation on uncorrected items.")],
        "ISA 501": [("ISA 501.4–13", "Specific Evidence: Inventory, Litigation & Segments", "Mandatory physical inventory counting attendance if inventory is material (unless impracticable, perform alternative procedures, ISA 501.4–8); inquiry of management/external legal counsel for litigation and claims (ISA 501.9–12); evaluate segment disclosures (ISA 501.13).")],
        "ISA 505": [("ISA 505.7–16", "External Confirmations (Positive vs. Negative)", "Maintain full auditor control over selection, dispatch, and receipt of confirmations (ISA 505.7). Investigate all exceptions and non-responses via alternative procedures; negative confirmations provide less persuasive evidence and are rarely sufficient alone (ISA 505.15).")],
        "ISA 510": [("ISA 510.6–13", "Initial Audit Engagements — Opening Balances", "Obtain sufficient appropriate evidence whether opening balances contain misstatements materially affecting current period and whether accounting policies are consistently applied (review predecessor auditor's workpapers or perform current-period/specific procedures).")],
        "ISA 520": [("ISA 520.5–7", "Substantive Analytical Procedures & Overall Review", "Design substantive analytical procedures by evaluating data reliability, developing a sufficiently precise expectation, and investigating differences exceeding threshold (ISA 520.5); mandatory analytical procedures near the end of the audit to corroborate overall conclusions (ISA 520.6).")],
        "ISA 530": [("ISA 530.6–15", "Audit Sampling Design, Projection & Evaluation", "Select sample items so each sampling unit has a chance of selection (statistical or non-statistical); project monetary misstatements found in substantive samples to the entire population (ISA 530.14) and evaluate sampling risk.")],
        "ISA 550": [("ISA 550.11–28", "Related Party Relationships & Transactions", "Remain alert for undisclosed related parties throughout the audit; treat significant related party transactions outside the normal course of business as Significant Risks (ISA 550.18), inspecting underlying contracts for business rationale and fraud indicators.")],
        "ISA 560": [("ISA 560.6–17", "Subsequent Events (Three Time Periods)", "Active duty to obtain evidence for events between period-end and auditor's report date (ISA 560.6–9); no obligation to perform procedures after report date, but if material facts become known before or after FS issuance, discuss amendment/reissuance with management (ISA 560.10–17).")],
        "ISA 580": [("ISA 580.9–20", "Written Representations from Management", "Obtain written representations confirming fulfilment of management's responsibilities for FS preparation and completeness of information provided (dated as near as practicable to, but not after, the auditor's report date, ISA 580.14). Refusal triggers Disclaimer of Opinion (ISA 580.20).")],
        "ISA 610 (Revised 2013)": [("ISA 610.15–35", "Using the Work of Internal Auditors", "Evaluate internal audit objectivity, competence, and systematic/disciplined approach before using its work; external auditor remains solely responsible for the audit opinion and cannot use direct assistance where prohibited by law/regulation.")],
        "ISA 620": [("ISA 620.8–15", "Using the Work of an Auditor's Expert", "Evaluate competence, capabilities, and objectivity of the auditor's expert (including IESBA 2026 external expert ethics amendments), agree scope in writing, and evaluate adequacy of the expert's findings and assumptions; do not reference the expert in an unmodified report unless required by law.")],
        "ISA 706 (Revised)": [("ISA 706.8–12", "Emphasis of Matter & Other Matter Paragraphs", "Emphasis of Matter (EoM) highlights a matter appropriately presented/disclosed in the FS that is fundamental to users' understanding (without modifying the opinion); Other Matter (OM) communicates a matter relevant to understanding the audit/auditor's responsibilities. Neither replaces KAM (ISA 701) or Going Concern (ISA 570).")],
        "ISA 710": [("ISA 710.7–19", "Comparative Information (Corresponding Figures vs. Comparative FS)", "Under Corresponding Figures, opinion refers only to current period (unless prior period was modified/misstated/unaudited); under Comparative Financial Statements, opinion refers to each period presented.")],
        "ISA 720 (Revised)": [("ISA 720.13–24", "Auditor's Responsibilities Relating to Other Information", "Read and consider all other information in the annual report (MD&A, chairman's statement) for material inconsistency with the FS or auditor's knowledge; include a dedicated 'Other Information' section in the auditor's report (ISA 720.21).")],
        "ISA 800 (Revised)": [("ISA 800.8–14", "Special Purpose Framework Audits", "Determine acceptability of special purpose framework (tax, cash-receipts, regulatory, contractual) and include an Emphasis of Matter paragraph alerting users that the FS are prepared under a special purpose framework and may not be suitable for another purpose (ISA 800.14).")],
        "ISA 805 (Revised)": [("ISA 805.7–17", "Single Financial Statement or Specific Element Audits", "Apply all relevant ISAs adapted to the single statement/element; evaluate whether auditing an isolated element without auditing the complete FS is practicable and consider interrelated items.")],
        "ISA 810 (Revised)": [("ISA 810.6–26", "Engagements to Report on Summary Financial Statements", "Accept engagement ONLY when also engaged to audit the complete FS from which summary FS are derived (ISA 810.5); opine on whether summary FS are consistent in all material respects with, or a fair summary of, the audited FS.")],
        "ISA for LCE": [("ISA for LCE Parts 1–10", "Proportionate Standalone Audit Standard for Less Complex Entities", "Effective for periods beginning on or after 15 Dec 2025; prohibits use for listed entities, public interest entities (PIEs), or complex groups; delivers the same 'reasonable assurance' level as full ISAs through streamlined, self-contained risk-based requirements.")],
        "ISRE 2400 (Revised)": [("ISRE 2400.43–92", "Limited Assurance Review of Historical Financial Statements", "Practitioner performs primarily inquiry and analytical procedures to obtain limited assurance and express a negative-assurance conclusion ('nothing has come to our attention that causes us to believe...').")],
        "ISRE 2410": [("ISRE 2410.12–43", "Interim Financial Information Review by the Entity's Auditor", "Leverages the auditor's existing understanding of the entity and internal control to perform targeted inquiries and analytical procedures on interim statements (e.g., IAS 34 condensed interims), issuing a limited-assurance review conclusion.")],
        "ISAE 3000 (Revised)": [("ISAE 3000.24–69", "Assurance Engagements Other than Audits/Reviews", "Establishes preconditions (suitable criteria, appropriate underlying subject matter, rational purpose), distinguishes reasonable vs. limited assurance work effort, and specifies assurance report elements.")],
        "ISAE 3400": [("ISAE 3400.8–27", "Examination of Prospective Financial Information", "Obtain sufficient appropriate evidence whether management's best-estimate assumptions are not unreasonable (forecasts) or hypothetical assumptions are consistent with purpose (projections), and express negative assurance on assumptions plus positive assurance on proper preparation.")],
        "ISAE 3402": [("ISAE 3402.13–53", "Service Organization Controls Reports (Type 1 & Type 2)", "Type 1 reports on fairness of system description and suitability of control design as of a point in time; Type 2 additionally tests and reports on operating effectiveness of controls over a specified period (used by user auditors under ISA 402).")],
        "ISAE 3410": [("ISAE 3410.17–76", "Assurance on Greenhouse Gas (GHG) Statements", "Covers organizational/operational boundaries, quantification methods, emission factors, Scope 1–3 uncertainty, and site-level verification for standalone GHG statements (complementing ISSA 5000).")],
        "ISAE 3420": [("ISAE 3420.13–35", "Assurance on Pro Forma Financial Information in a Prospectus", "Reasonable assurance engagement testing whether pro forma financial information has been properly compiled on the basis of applicable criteria (e.g., acquisition adjustments) — does not re-audit the underlying historical FS.")],
        "ISRS 4400 (Revised)": [("ISRS 4400.19–32", "Agreed-Upon Procedures (AUP) Engagements", "Practitioner performs specific procedures agreed with engaging party and reports ONLY factual findings — NO assurance or opinion is expressed; independence is not mandatory unless required by law/engagement terms (must disclose whether independent).")],
        "ISRS 4410 (Revised)": [("ISRS 4410.24–41", "Compilation Engagements", "Applies accounting/financial reporting expertise to assist management in preparing and presenting historical financial information; NO assurance is obtained or expressed, and the compilation report explicitly states neither an audit nor a review was performed.")],
    },
}


def main() -> int:
    total_docs = 0
    total_secs = 0
    for fname, mapping in REMAINING_ENRICHMENTS.items():
        path = INTL_DATA_DIR / fname
        if not path.exists():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        f_docs = 0
        f_secs = 0
        for d in data["documents"]:
            code = d.get("code", "")
            if code not in mapping:
                continue
            modules = mapping[code]
            mod_nos = {m[0] for m in modules}
            base_arts = [a for a in d.get("articles", []) if a.get("no") not in mod_nos]
            ov = [a for a in base_arts if a.get("no") == "Overview"]
            rest = [a for a in base_arts if a.get("no") != "Overview"]
            new_arts = [{"no": no, "heading": hd, "text": txt, "seq": 0} for no, hd, txt in modules]
            merged = ov + new_arts + rest
            for idx, a in enumerate(merged):
                a["seq"] = idx
            d["articles"] = merged
            f_docs += 1
            f_secs += len(new_arts)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"{fname}: enriched {f_docs} remaining standards/interpretations with {f_secs} sections")
        total_docs += f_docs
        total_secs += f_secs
    print(f"Total remaining enriched: {total_docs} docs / {total_secs} sections.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
