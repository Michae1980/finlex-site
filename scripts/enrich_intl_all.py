#!/usr/bin/env python3
"""
为其余高频国际会计准则（IFRS/IAS）、ISSB 可持续披露、IAASB 国际审计与质量管理、
IESBA 职业道德守则及 OECD 国际税收规则批量补充「官方段落号/条款号索引的深度技术精要」。

说明：
- 严格遵循公开合规边界：全部为原创英文结构化技术精要，标注官方真实段落/章节号，不搬运付费全文；
- 幂等写入 intl_data/*.json（插在 Overview 之后、保留原有 History/Support/References/Official Access）。
"""

from __future__ import annotations

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INTL_DATA_DIR = PROJECT_ROOT / "intl_data"


ENRICHMENTS_BY_FILE: dict[str, dict[str, list[tuple[str, str, str]]]] = {
    "ifrs_accounting.json": {
        "IFRS 2": [
            (
                "IFRS 2.10–33",
                "Equity-Settled vs. Cash-Settled Share-Based Payments",
                "• Equity-settled (IFRS 2.10–29): for employees, measure at grant-date fair value of equity instruments and expense over the vesting period with a credit to equity (no subsequent remeasurement for fair value changes).\n"
                "• Vesting conditions (IFRS 2.19–21A): service conditions and non-market performance conditions affect the NUMBER of awards expected to vest (trued up each period); market conditions (e.g., TSR/share price target) and non-vesting conditions are factored into grant-date fair value and NOT trued up if unmet.\n"
                "• Cash-settled (IFRS 2.30–33): recognise a liability remeasured to fair value at each reporting date through P&L until settled (e.g., SARs).\n"
                "• Modifications & cancellations (IFRS 2.26–29): incremental fair value is expensed over remaining vesting period; cancellation is accounted for as an acceleration of vesting (converged with China CAS 11).",
            ),
        ],
        "IFRS 5": [
            (
                "IFRS 5.6–36",
                "Held for Sale Criteria, Measurement & Discontinued Operations",
                "• Classification criteria (IFRS 5.6–8): carrying amount will be recovered principally through a sale transaction rather than continuing use; asset/disposal group must be available for immediate sale in its present condition and sale must be highly probable (management committed, active marketing, sale expected within 1 year).\n"
                "• Measurement (IFRS 5.15–25): measure at the lower of carrying amount and Fair Value Less Costs to Sell (FVLCD); cease depreciation/amortisation once classified as held for sale.\n"
                "• Discontinued operations (IFRS 5.31–36): a component that has been disposed of or classified as held for sale and represents a separate major line of business or geographical area; present a single post-tax amount in P&L with comparative restatement (converged with China CAS 42).",
            ),
        ],
        "IFRS 7": [
            (
                "IFRS 7.6–42",
                "Financial Instruments: Significance & Nature/Extent of Risks",
                "• Balance-sheet & P&L significance (IFRS 7.8–30): carrying amounts by IFRS 9 category, collateral, allowance roll-forwards, hedge accounting disclosures, and fair value comparisons.\n"
                "• Qualitative & quantitative risk disclosures (IFRS 7.31–42): credit risk (maximum exposure, ECL staging/credit rating grades, concentration), liquidity risk (undiscounted contractual maturity analysis of financial liabilities), and market risk (interest rate, currency, and price sensitivity analyses).\n"
                "• Supplier finance arrangements (IFRS 7.B11F, amended 2023) & ESG-linked contractual terms (amended 2024, effective 1 Jan 2026).",
            ),
        ],
        "IFRS 8": [
            (
                "IFRS 8.5–28",
                "Management Approach, CODM & Reportable Segment Thresholds",
                "• Chief Operating Decision Maker — CODM (IFRS 8.5–10): identify operating segments based on internal reports regularly reviewed by the CODM to allocate resources and assess performance.\n"
                "• Quantitative thresholds (IFRS 8.13–15): report separately any operating segment (or aggregated similar segments under 8.12) meeting ≥10% of combined revenue, ≥10% of absolute profit/loss, or ≥10% of combined assets; total external revenue of reportable segments must reach at least 75% of entity revenue.\n"
                "• Entity-wide disclosures (IFRS 8.31–34): products/services, geographical areas, and major customers representing ≥10% of total revenue (converged with China CAS 35).",
            ),
        ],
        "IFRS 11": [
            (
                "IFRS 11.4–25",
                "Joint Control, Joint Operations vs. Joint Ventures",
                "• Joint control (IFRS 11.7–13): contractually agreed sharing of control requiring unanimous consent of parties sharing control for decisions about relevant activities.\n"
                "• Joint Operation (IFRS 11.15, 20): parties have rights to the assets and obligations for the liabilities; recognise share of assets, liabilities, revenues, and expenses line-by-line.\n"
                "• Joint Venture (IFRS 11.16, 24): parties have rights to the net assets of a separate vehicle; account for investment using the equity method under IAS 28 (converged with China CAS 40).",
            ),
        ],
        "IFRS 13": [
            (
                "IFRS 13.9–99",
                "Exit Price, Principal Market & Fair Value Hierarchy (Levels 1–3)",
                "• Definition (IFRS 13.9): the price that would be received to sell an asset or paid to transfer a liability in an orderly transaction between market participants at the measurement date (exit price, not entry price).\n"
                "• Principal or most advantageous market (IFRS 13.16–20): measure using the principal market (greatest volume/level of activity), or in its absence the most advantageous market; for non-financial assets, apply 'highest and best use' (IFRS 13.27–33).\n"
                "• Three-level Fair Value Hierarchy (IFRS 13.72–90): Level 1 (unadjusted quoted prices in active markets), Level 2 (observable inputs other than Level 1), Level 3 (unobservable inputs requiring sensitivity and roll-forward disclosures, converged with China CAS 39).",
            ),
        ],
        "IFRS 17": [
            (
                "IFRS 17.29–71",
                "Insurance Measurement Models (GMM, PAA, VFA) & CSM",
                "• General Measurement Model — GMM / Building Block Approach (IFRS 17.30–52): fulfilment cash flows (probability-weighted future cash flows + discounting + risk adjustment for non-financial risk) PLUS Contractual Service Margin (CSM) representing unearned profit released over the coverage period. Onerous contracts recognise losses immediately in P&L (IFRS 17.47).\n"
                "• Premium Allocation Approach — PAA (IFRS 17.53–59): simplified model permitted for short-duration contracts (coverage ≤1 year or where PAA approximates GMM).\n"
                "• Variable Fee Approach — VFA (IFRS 17.45, B101–B118): mandatory modification for insurance contracts with direct participation features (converged with China CAS 25, 2020 Revision).",
            ),
        ],
        "IFRS 19": [
            (
                "IFRS 19.7–19",
                "Eligible Subsidiaries & Reduced Disclosure Framework (Effective 2027)",
                "• Eligibility (IFRS 19.7): voluntary standard available to a subsidiary that (a) does NOT have public accountability (not listed, not a financial institution holding assets in a fiduciary capacity) AND (b) has an ultimate or intermediate parent producing consolidated financial statements available for public use that comply with IFRS Accounting Standards.\n"
                "• Core benefit: apply FULL recognition, measurement, and presentation requirements of other IFRS standards, while replacing their disclosure sections with IFRS 19's streamlined disclosure requirements (effective 1 Jan 2027).",
            ),
        ],
        "IFRS 20": [
            (
                "IFRS 20 (2026)",
                "Regulatory Assets & Regulatory Liabilities (Issued May 2026)",
                "Issued by the IASB in May 2026 (replacing interim IFRS 14), IFRS 20 establishes a comprehensive accounting model for entities subject to rate regulation that creates enforceable rights to add amounts to future regulated rates (regulatory assets) or enforceable obligations to deduct amounts from future rates (regulatory liabilities).\n"
                "• Recognise regulatory assets and regulatory liabilities on the balance sheet and regulatory income/expense in profit or loss to reflect total allowed compensation for goods or services supplied in the period.",
            ),
        ],
        "IAS 2": [
            (
                "IAS 2.9–34",
                "Inventory Cost, NRV Write-Downs & Reversals",
                "• Measurement (IAS 2.9): lower of cost and Net Realisable Value (NRV — estimated selling price minus estimated costs of completion and costs necessary to make the sale).\n"
                "• Cost formulas (IAS 2.23–27): specific identification for non-interchangeable items; FIFO or weighted average cost for interchangeable items. LIFO is PROHIBITED.\n"
                "• Write-down reversal (IAS 2.33): reverse prior NRV write-downs through P&L when circumstances change, capped at original cost (converged with China CAS 1).",
            ),
        ],
        "IAS 7": [
            (
                "IAS 7.10–45",
                "Cash Flow Classification & IFRS 18 Consequential Amendments",
                "• Three activities (IAS 7.10–21): Operating (direct or indirect method), Investing, and Financing; cash equivalents are short-term, highly liquid investments readily convertible to known cash with insignificant risk of value change (generally maturity ≤3 months).\n"
                "• IFRS 18 consequential amendments (effective 1 Jan 2027): (1) indirect operating cash flows MUST start from Operating Profit (not Profit before Tax); (2) for non-financial entities, interest paid and dividends paid are classified strictly as Financing, and interest/dividends received strictly as Investing (removing IAS 7's prior classification choices).",
            ),
        ],
        "IAS 8": [
            (
                "IAS 8.7–49",
                "Accounting Policies, Changes in Estimates & Prior Period Errors",
                "• Renamed 'Basis of Preparation of Financial Statements' by IFRS 18 (incorporating going concern, accrual basis, and material accounting policy disclosures).\n"
                "• Changes in accounting policy (IAS 8.14–27): applied retrospectively unless transitional rules state otherwise.\n"
                "• Changes in accounting estimates (IAS 8.32–38): monetary amounts subject to measurement uncertainty (clarified 2021); applied prospectively.\n"
                "• Prior period material errors (IAS 8.41–49): corrected retrospectively by restating comparative periods (converged with China CAS 28).",
            ),
        ],
        "IAS 10": [
            (
                "IAS 10.8–21",
                "Adjusting vs. Non-Adjusting Events & Going Concern",
                "• Adjusting events (IAS 10.8–9): provide evidence of conditions existing at the reporting date (e.g., bankruptcy of a customer confirming credit loss, settlement of a court case) — adjust financial statements.\n"
                "• Non-adjusting events (IAS 10.10–13, 21): indicative of conditions arising after the reporting date (e.g., post-year-end dividend declaration, major acquisition, natural disaster) — do NOT adjust, disclose if material.\n"
                "• Going concern exception (IAS 10.14): do not prepare financial statements on a going concern basis if management determines after the reporting date to liquidate or cease trading (converged with China CAS 29).",
            ),
        ],
        "IAS 16": [
            (
                "IAS 16.7–72 & CAS 4",
                "PPE Recognition, Component Depreciation & Revaluation Model (vs. CAS 4)",
                "• Initial cost (IAS 16.16–22): purchase price, directly attributable bringing-to-condition costs, and initial estimate of dismantling/restoration costs (IAS 37); net proceeds from selling items produced while testing an asset are recognised in P&L (2020 amendment, IAS 16.20A).\n"
                "• Component depreciation (IAS 16.43–47): depreciate each part of an item of PPE with a cost significant in relation to total cost separately over its useful life.\n"
                "• Subsequent measurement (IAS 16.29–42): Cost Model OR Revaluation Model (revaluation surplus recognised in OCI, decreases in P&L).\n"
                "• Major CAS 4 vs. IAS 16 difference: China CAS 4 only permits the Cost Model for fixed assets (no Revaluation Model).",
            ),
        ],
        "IAS 19": [
            (
                "IAS 19.11–134",
                "Short-Term Benefits, Defined Contribution vs. Defined Benefit Plans",
                "• Short-term benefits & defined contribution plans (IAS 19.11, 51): recognise undiscounted expense as employee renders service.\n"
                "• Defined benefit plans (IAS 19.55–134): measure net defined benefit liability/asset using the Projected Unit Credit Method; recognise service cost and net interest in P&L, and remeasurements (actuarial gains/losses, return on plan assets excluding net interest) in OCI with NO subsequent recycling to P&L (converged with China CAS 9).",
            ),
        ],
        "IAS 20": [
            (
                "IAS 20.7–31",
                "Government Grants: Recognition & Asset vs. Income Presentation",
                "• Recognition (IAS 20.7): recognise only when reasonable assurance exists that the entity will comply with conditions and the grant will be received.\n"
                "• Income approach (IAS 20.12): recognise in P&L on a systematic basis over the periods in which the related costs are expensed.\n"
                "• Grants related to assets (IAS 20.24–27): present EITHER as deferred income (gross) OR by deducting the grant from the asset's carrying amount (net) — aligned with China CAS 16 (2017 Revision).",
            ),
        ],
        "IAS 21": [
            (
                "IAS 21.8–49",
                "Functional Currency, Translation & Lack of Exchangeability",
                "• Functional currency (IAS 21.9–14): currency of the primary economic environment in which the entity operates.\n"
                "• Foreign currency transactions (IAS 21.21–32): translate initially at spot rate; at reporting date retranslate monetary items at closing rate (FX differences in P&L), while historical-cost non-monetary items stay at historical rate.\n"
                "• Foreign operation translation (IAS 21.39): assets/liabilities at closing rate, income/expenses at transaction/average rates, exchange differences in OCI (recycled to P&L on disposal).\n"
                "• Lack of Exchangeability (IAS 21.8A–8B, 19A, effective 1 Jan 2025): specifies how to assess exchangeability and estimate a spot exchange rate when a currency is not exchangeable (converged with China CAS 19).",
            ),
        ],
        "IAS 23": [
            (
                "IAS 23.8–25",
                "Capitalisation of Borrowing Costs on Qualifying Assets",
                "• Core rule (IAS 23.8): capitalise borrowing costs directly attributable to the acquisition, construction, or production of a qualifying asset (takes a substantial period of time to get ready for intended use/sale).\n"
                "• Specific vs. general borrowings (IAS 23.12–14): specific borrowings = actual borrowing costs minus temporary investment income; general borrowings = weighted-average capitalisation rate applied to asset expenditures.\n"
                "• Commencement, suspension & cessation (IAS 23.17–25): start when expenditures, borrowing costs, and preparation activities are all underway; suspend during extended interruptions; cease when substantially all activities are complete (converged with China CAS 17).",
            ),
        ],
        "IAS 24": [
            (
                "IAS 24.9–27",
                "Related Party Definition, KMP Compensation & Disclosures",
                "• Related parties (IAS 24.9): covers control, joint control, significant influence, key management personnel (KMP) and their close family members, and post-employment benefit plans.\n"
                "• Mandatory disclosures (IAS 24.13–24): parent-subsidiary relationships (even without transactions), KMP compensation by category, and nature/amounts/outstanding balances/provisions of related party transactions.\n"
                "• Government-related entities exemption (IAS 24.25–27): simplified qualitative/significant transaction disclosures for state-owned enterprises (converged with China CAS 36).",
            ),
        ],
        "IAS 28": [
            (
                "IAS 28.5–45",
                "Significant Influence & Equity Method Accounting",
                "• Significant influence (IAS 28.5–9): power to participate in financial and operating policy decisions without control or joint control; rebuttable presumption at ≥20% voting power.\n"
                "• Equity method (IAS 28.10–39): recognise initially at cost, adjust subsequently for investor's share of post-acquisition profit/loss (in P&L) and OCI, eliminate unrealised upstream/downstream profits to the extent of investor's interest, and test net investment for impairment under IAS 36 after applying IFRS 9 to long-term interests (converged with China CAS 2).",
            ),
        ],
        "IAS 32": [
            (
                "IAS 32.11–42",
                "Liability vs. Equity Classification, Fixed-for-Fixed & Offsetting",
                "• Core distinction (IAS 32.16): an instrument is a financial liability if the issuer has a contractual obligation to deliver cash/another financial asset, or to exchange financial instruments under potentially unfavourable conditions.\n"
                "• 'Fixed-for-Fixed' rule (IAS 32.16(b)(ii)): a derivative settled in the issuer's own equity is classified as equity ONLY if it exchanges a fixed amount of cash for a fixed number of own equity instruments.\n"
                "• Compound instruments (IAS 32.28–32): split convertible bonds into liability component (fair value of similar straight debt) and residual equity component.\n"
                "• Offsetting (IAS 32.42): requires BOTH a currently enforceable legal right to set off AND intention to settle net or simultaneously (converged with China CAS 37).",
            ),
        ],
        "IAS 33": [
            (
                "IAS 33.9–65",
                "Basic & Diluted Earnings Per Share (EPS)",
                "• Basic EPS (IAS 33.10–29): profit/loss attributable to ordinary equity holders of the parent divided by weighted-average number of ordinary shares outstanding (retrospectively adjusted for bonus issues/share splits).\n"
                "• Diluted EPS (IAS 33.30–63): adjust numerator and denominator for all dilutive potential ordinary shares (convertible debt, options/warrants via treasury stock method); exclude anti-dilutive instruments; test dilution based on profit from continuing operations (converged with China CAS 34).",
            ),
        ],
        "IAS 40": [
            (
                "IAS 40.5–65 & CAS 3",
                "Investment Property: Cost vs. Fair Value Model (vs. CAS 3)",
                "• Scope (IAS 40.5–15): land or building held to earn rentals or for capital appreciation (not owner-occupied under IAS 16 or held for sale in ordinary course under IAS 2).\n"
                "• Accounting policy choice (IAS 40.30–56): choose EITHER Fair Value Model (fair value changes recognised directly in P&L, NO depreciation) OR Cost Model (depreciated under IAS 16, with fair value still disclosed in notes).\n"
                "• Key CAS 3 vs. IAS 40 nuance: China CAS 3 requires Cost Model as default and permits Fair Value Model only when an active local property market provides reliable ongoing fair value evidence, and prohibits switching back from Fair Value to Cost.",
            ),
        ],
    },
    "issb_sustainability.json": {
        "IFRS S1": [
            (
                "IFRS S1.25–53",
                "Four-Pillar Core Content & Materiality",
                "Built on the TCFD structure, IFRS S1 requires disclosures across FOUR core pillars for all material sustainability-related risks and opportunities:\n"
                "• Governance (IFRS S1.26–27): governance bodies/individuals overseeing sustainability risks, skills, reporting cadence, and remuneration linkage.\n"
                "• Strategy (IFRS S1.28–42): short/medium/long-term risks & opportunities, business model and value chain effects, current and anticipated financial effects, and resilience.\n"
                "• Risk Management (IFRS S1.43–44): processes to identify, assess, prioritise, and monitor sustainability risks and integration with overall enterprise risk management.\n"
                "• Metrics & Targets (IFRS S1.45–53): cross-industry and industry-specific metrics (referencing SASB Standards under S1.55) and progress against targets.",
            ),
            (
                "IFRS S1.17–24 & E1–E6",
                "Financial Materiality, Connected Information & Transition Reliefs",
                "• Investor-focused materiality (IFRS S1.17–19): aligned with IAS 1/IFRS 18 — information is material if omitting, misstating, or obscuring it could reasonably be expected to influence primary users' decisions.\n"
                "• Connected information & reporting boundary (IFRS S1.20–24): same reporting entity and reporting period as the related financial statements.\n"
                "• Transition reliefs (IFRS S1.E3–E6): 'climate-first' relief permits reporting only climate-related disclosures (IFRS S2) in the first annual reporting period, plus comparative-period relief.\n"
                "• China comparison: China's 《企业可持续披露准则——基本准则（试行）》 adopts the same four-pillar structure while incorporating 'double materiality' (impact materiality + financial materiality).",
            ),
        ],
        "IFRS S2": [
            (
                "IFRS S2.10–37",
                "Climate Risks, GHG Emissions (Scope 1–3) & Scenario Analysis",
                "• Climate-related risks & opportunities (IFRS S2.10–14): distinguish physical risks (acute/chronic) and transition risks (policy, legal, technology, market, reputation); disclose transition plans and capital deployment.\n"
                "• Climate resilience & scenario analysis (IFRS S2.22): use climate-related scenario analysis commensurate with entity's circumstances.\n"
                "• Cross-industry climate metrics (IFRS S2.29): absolute gross Scope 1, Scope 2, and Scope 3 GHG emissions (measured per GHG Protocol unless jurisdiction requires another method), financed emissions for financial institutions, internal carbon prices, and climate-linked executive remuneration.\n"
                "• Targeted Amendments (Dec 2025, effective 1 Jan 2027): provide targeted reliefs for certain Scope 3 Category 15 financed emissions (e.g., derivatives, facilitated emissions) and GICS classification.",
            ),
        ],
    },
    "iaasb_auditing.json": {
        "ISQM 1": [
            (
                "ISQM 1.19–56",
                "Eight Components of Firm Quality Management (SOQM)",
                "Requires firms to design and operate a proactive, risk-based System of Quality Management (SOQM) covering 8 integrated components:\n"
                "• (1) Firm's risk assessment process (quality objectives → quality risks → responses); (2) Governance and leadership; (3) Relevant ethical requirements; (4) Acceptance and continuance of client relationships; (5) Engagement performance; (6) Resources (human, technological, intellectual); (7) Information and communication; (8) Monitoring and remediation process.\n"
                "• Annual evaluation (ISQM 1.53–55): leadership must evaluate at least annually whether the SOQM provides reasonable assurance that its objectives are being achieved (converged with China QMS 5101).",
            ),
        ],
        "ISQM 2": [
            (
                "ISQM 2.17–27",
                "Engagement Quality Reviewer Eligibility, Cooling-Off & Review",
                "• Eligibility (ISQM 2.18–20): reviewer must have competence, capabilities, authority, and objectivity; requires a mandatory 2-year cooling-off period before a former engagement partner can serve as EQR for the same entity (ISQM 2.19(b)).\n"
                "• Performance & timing (ISQM 2.24–26): review significant judgements and conclusions at appropriate points throughout the engagement; engagement report CANNOT be dated before the EQR notifies completion (converged with China QMS 5102).",
            ),
        ],
        "ISA 200": [
            (
                "ISA 200.11–24",
                "Overall Objectives, Audit Risk Model & Professional Skepticism",
                "• Overall objective (ISA 200.11): obtain reasonable assurance about whether the financial statements as a whole are free from material misstatement (whether due to fraud or error) and report in accordance with ISAs.\n"
                "• Core pillars (ISA 200.14–17): comply with IESBA ethical/independence requirements; plan and perform with professional skepticism; exercise professional judgment; obtain sufficient appropriate audit evidence to reduce audit risk (AR = IR × CR × DR) to an acceptably low level (converged with China CSA 1101).",
            ),
        ],
        "ISA 240 (Revised)": [
            (
                "ISA 240 (Rev. 2025)",
                "Fraud Responsibilities, Presumed Risks & 2025 Revision Highlights",
                "• Fraud triangle & skepticism (ISA 240.12–16): maintain heightened professional skepticism throughout; hold mandatory engagement team discussion on fraud susceptibility.\n"
                "• Two presumed fraud risks (ISA 240.27, 32): (1) improper revenue recognition (rebuttable, must document if rebutted); (2) management override of controls (NEVER rebuttable — mandatory journal entry testing, retrospective review of estimates, and evaluation of significant unusual transactions).\n"
                "• July 2025 Revised Edition highlights: clarifies auditor's role on fraud, reinforces fraud-lens risk assessment aligned with ISA 315, strengthens responses when fraud or suspected fraud is identified, and enhances transparency in auditor's reports (converged with China CSA 1141).",
            ),
        ],
        "ISA 315 (Revised 2019)": [
            (
                "ISA 315.19–38",
                "Spectrum of Inherent Risk, Significant Risks & ITGCs",
                "• Risk identification & assessment (ISA 315.19–34): separately assess Inherent Risk (using 5 inherent risk factors: complexity, subjectivity, change, uncertainty, susceptibility to bias/fraud) and Control Risk.\n"
                "• Significant risk (ISA 315.12(l), 32): an identified risk of material misstatement where inherent risk sits close to the upper end of the spectrum of inherent risk (triggers mandatory substantive responses under ISA 330).\n"
                "• IT environment & ITGCs (ISA 315.26, Appendix 5): identify risks arising from use of IT and evaluate design & implementation of General IT Controls (ITGCs) addressing those risks (converged with China CSA 1211).",
            ),
        ],
        "ISA 320": [
            (
                "ISA 320.10–14",
                "Overall Materiality, Performance Materiality & Revisions",
                "• Overall materiality (ISA 320.10): determined for the financial statements as a whole using an appropriate benchmark (e.g., profit before tax, revenue, total assets).\n"
                "• Performance materiality (ISA 320.9, 11): set BELOW overall materiality to reduce to an appropriately low level the probability that aggregate uncorrected and undetected misstatements exceed overall materiality.\n"
                "• Revise materiality (ISA 320.12) if new information during the audit would have caused a different initial amount (converged with China CSA 1221).",
            ),
        ],
        "ISA 330": [
            (
                "ISA 330.5–28",
                "Responses to Assessed Risks: Tests of Controls vs. Substantive Procedures",
                "• Overall responses (ISA 330.5): address financial-statement-level risks (e.g., assign more experienced staff, incorporate unpredictability).\n"
                "• Tests of controls (ISA 330.8–17): mandatory when auditor intends to rely on operating effectiveness of controls OR when substantive procedures alone cannot provide sufficient appropriate evidence.\n"
                "• Substantive procedures (ISA 330.18–23): mandatory for each material class of transactions, account balance, and disclosure; for Significant Risks, MUST perform substantive procedures specifically responsive to that risk (including tests of details if relying solely on substantive procedures, converged with China CSA 1231).",
            ),
        ],
        "ISA 500": [
            (
                "ISA 500.6–11",
                "Sufficient Appropriate Audit Evidence & Reliability Hierarchy",
                "• Sufficiency (quantity) and Appropriateness (quality = relevance + reliability) (ISA 500.6, A4–A5).\n"
                "• Reliability principles (ISA 500.A31): independent external sources > internal records; effective controls increase internal reliability; direct auditor-obtained evidence > indirect; documentary > oral; originals > photocopies.\n"
                "• Management's expert (ISA 500.8): evaluate competence, capabilities, and objectivity of any management's expert whose work is used as audit evidence (converged with China CSA 1301).",
            ),
        ],
        "ISA 540 (Revised)": [
            (
                "ISA 540.13–36",
                "Auditing Accounting Estimates: Three Testing Approaches & Bias",
                "• Separate inherent and control risk assessment considering estimation uncertainty, complexity, and subjectivity (ISA 540.16).\n"
                "• Three testing approaches (ISA 540.18): (a) obtain evidence from events occurring up to auditor's report date; (b) test how management made the estimate (method, significant assumptions, data); (c) develop an auditor's point estimate or range.\n"
                "• Stand-back evaluation (ISA 540.33–36): evaluate indicators of possible management bias and reasonableness of disclosures (converged with China CSA 1321).",
            ),
        ],
        "ISA 570 (Revised 2024)": [
            (
                "ISA 570 (Rev. 2024)",
                "Going Concern Assessment, 12-Month Window & Reporting",
                "• Management's assessment (ISA 570 Revised 2024, published April 2025): strengthens auditor evaluation of management's going concern assessment over at least 12 months from the date of approval of the financial statements.\n"
                "• Reporting outcomes: adequate disclosure of Material Uncertainty → unmodified opinion with dedicated 'Material Uncertainty Related to Going Concern' section; inadequate disclosure → Qualified or Adverse opinion; inappropriate going concern basis → Adverse opinion (converged with China CSA 1324).",
            ),
        ],
        "ISA 600 (Revised)": [
            (
                "ISA 600.16–59",
                "Risk-Based Group Audits & Component Auditors",
                "• Removes the legacy 'significant component' full-scope bright line in favour of a risk-based scoping approach aligned with ISA 315.\n"
                "• Group engagement partner retains sole responsibility for direction, supervision, and review of component auditors, determining component performance materiality (lower than group materiality), and evaluating sufficiency of group audit evidence (converged with China CSA 1401).",
            ),
        ],
        "ISA 700 (Revised)": [
            (
                "ISA 700.20–49",
                "Auditor's Report Structure & Unmodified Opinion",
                "• Standardised report order (ISA 700.23–45): (1) Opinion (placed FIRST); (2) Basis for Opinion (including IESBA independence statement); (3) Going Concern (where applicable); (4) Key Audit Matters (ISA 701 for listed entities); (5) Other Information (ISA 720); (6) Responsibilities of Management & TCWG; (7) Auditor's Responsibilities (converged with China CSA 1501).",
            ),
        ],
        "ISA 701": [
            (
                "ISA 701.9–16",
                "Key Audit Matters (KAM) Selection & Description",
                "• Mandatory for audits of complete sets of general purpose financial statements of listed entities (ISA 701.5).\n"
                "• Selection funnel (ISA 701.9–10): matters communicated with TCWG → matters requiring significant auditor attention (high risk, significant judgements/estimates, significant events) → matters of MOST significance in the current period audit.\n"
                "• Description (ISA 701.13): explain WHY the matter was a KAM and HOW it was addressed in the audit (not a substitute for a modified opinion, converged with China CSA 1504).",
            ),
        ],
        "ISA 705 (Revised)": [
            (
                "ISA 705.6–15",
                "Modified Opinions Matrix (Material vs. Pervasive)",
                "• Financial statements are materially misstated: Material but NOT pervasive → Qualified Opinion (保留意见); Material AND pervasive → Adverse Opinion (否定意见).\n"
                "• Inability to obtain sufficient appropriate audit evidence (scope limitation): Material but NOT pervasive → Qualified Opinion; Material AND pervasive → Disclaimer of Opinion (无法表示意见) (converged with China CSA 1502).",
            ),
        ],
        "ISSA 5000": [
            (
                "ISSA 5000 (Eff. Dec 2026)",
                "Sustainability Assurance: Limited vs. Reasonable & Value Chain",
                "• Profession-agnostic, framework-neutral global standard for sustainability assurance engagements (applicable to IFRS S1/S2, ESRS, GRI, etc.) effective for periods beginning on or after 15 Dec 2026.\n"
                "• Covers both Limited Assurance (primarily inquiry and analytical procedures) and Reasonable Assurance (tests of controls and substantive procedures), addressing double vs. financial materiality, forward-looking estimates, value chain data, and fraud/greenwashing risks.\n"
                "• Preconditions: requires firm quality management at least as demanding as ISQM 1 and ethical/independence requirements at least as demanding as IESBA Part 5 (IESSA) (converged with China Sustainability Assurance Standard No. 6101).",
            ),
        ],
    },
    "iesba_ethics.json": {
        "IESBA Code Part 1–3": [
            (
                "IESBA Sec 110–390",
                "Five Fundamental Principles, Threats & 2026 External Expert Rules",
                "• Five Fundamental Principles (Section 110): Integrity, Objectivity, Professional Competence and Due Care, Confidentiality, and Professional Behavior.\n"
                "• Five Threat Categories (Section 120): Self-interest, Self-review, Advocacy, Familiarity, and Intimidation — addressed by eliminating circumstances, applying safeguards, or declining/ending the engagement.\n"
                "• NOCLAR (Sections 260 & 360): structured response framework for Non-Compliance with Laws and Regulations.\n"
                "• 2026 Handbook Additions (effective 15 Dec 2026): new Section 290 (PAIBs) and Section 390 (PAPPs) governing ethical evaluation when using the work of an external expert, plus sustainability reporting ethics revisions.",
            ),
        ],
        "IESBA Code Part 4A": [
            (
                "IESBA Sec 400–600",
                "Audit & Review Independence: PIEs, Fees, NAS & Partner Rotation",
                "• Independence of Mind and Independence in Appearance required throughout the engagement period and period covered by the financial statements (Section 400).\n"
                "• Public Interest Entities — PIEs (Section 400.17): expanded definition covering publicly traded entities, banks, insurers, and entities holding assets in a fiduciary capacity.\n"
                "• Fee-related provisions (Section 410): public fee transparency for PIEs and fee-dependency thresholds (>15% for 2 consecutive years triggers mandatory pre-issuance EQR; >15% for 5 consecutive years triggers resignation for PIEs).\n"
                "• Non-Assurance Services — NAS (Section 600): prohibits creating a self-review threat for PIE audit clients (no materiality qualifier) and requires TCWG concurrence; Key Audit Partner rotation limited to 7 years on / 5 years cooling-off for PIE engagement partners (Section 540).",
            ),
        ],
        "IESBA Code Part 4B": [
            (
                "IESBA Sec 900–990",
                "Independence for Other Assurance Engagements",
                "• Applies to assurance engagements other than audits/reviews of historical financial statements (Part 4A) and sustainability assurance engagements (Part 5 — IESSA).\n"
                "• Covers financial interests, loans/guarantees, business/family relationships, long association, and provision of non-assurance services to assurance clients (ISAE 3000 / 3402 / 3410).",
            ),
        ],
        "IESBA Code Part 5 (IESSA)": [
            (
                "IESBA Part 5 (Eff. Dec 2026)",
                "Sustainability Assurance Ethics & Value-Chain Independence",
                "• Volume 2 of the 2026 IESBA Handbook (effective 15 Dec 2026): applies equally to BOTH professional accountants and non-accountant sustainability assurance practitioners.\n"
                "• Establishes independence standards equivalent in rigor to Part 4A for sustainability assurance engagements of PIEs, plus tailored independence rules for value-chain entities and using the work of another practitioner or external expert.",
            ),
        ],
    },
    "oecd_tax.json": {
        "OECD Pillar Two (GloBE)": [
            (
                "GloBE Art. 1–10",
                "15% Global Minimum Tax: Scope, ETR Formula & Charging Order",
                "• Scope (Art. 1.1): MNE groups with consolidated revenue ≥ EUR 750 million in at least 2 of the 4 preceding fiscal years.\n"
                "• Jurisdictional Effective Tax Rate (ETR) (Art. 5.1–5.2): Adjusted Covered Taxes ÷ Net GloBE Income per jurisdiction; if ETR < 15%, Top-up Tax Percentage = 15% − ETR applied to Excess Profit (Net GloBE Income minus Substance-based Income Exclusion for payroll & tangible assets).\n"
                "• Charging rule order: (1) Qualified Domestic Minimum Top-up Tax (QDMTT) collected locally first; (2) Income Inclusion Rule (IIR) at Ultimate Parent Entity; (3) Undertaxed Profits Rule (UTPR) backstop.\n"
                "• Transitional CbCR Safe Harbours & IAS 12 link: temporary safe harbours simplify 2024–2026 compliance; accounting follows IAS 12.4A/88A–88D mandatory deferred tax exception.",
            ),
        ],
        "OECD Model Tax Convention": [
            (
                "OECD MTC Art. 4–25",
                "Key Treaty Articles: Residency, PE, Passive Income & MAP",
                "• Art. 4 (Resident): tie-breaker rules for dual-resident individuals (permanent home, centre of vital interests) and entities (mutual agreement).\n"
                "• Art. 5 & Art. 7 (Permanent Establishment & Business Profits): source country may tax business profits ONLY if attributable to a PE (fixed place of business, construction site >12 months, or dependent agent).\n"
                "• Arts. 10–12 (Withholding Tax Caps): Dividends (5% substantial holding / 15% portfolio), Interest (10%), Royalties (0% in OECD Model; often 10% in bilateral treaties involving China).\n"
                "• Art. 23 & Art. 25: Elimination of double taxation (exemption or credit method) and Mutual Agreement Procedure (MAP) for cross-border dispute resolution.",
            ),
        ],
        "OECD Transfer Pricing Guidelines": [
            (
                "OECD TPG Ch. I–X",
                "Arm's Length Principle, Five TP Methods, DEMPE & Documentation",
                "• Arm's Length Principle (Chapter I, MTC Art. 9): controlled transactions between associated enterprises must reflect conditions that independent enterprises would agree to.\n"
                "• Five Transfer Pricing Methods (Chapter II): Traditional Transaction Methods (CUP, Resale Price, Cost Plus) and Transactional Profit Methods (TNMM, Transactional Profit Split).\n"
                "• Intangibles & DEMPE (Chapter VI): profit allocation follows Development, Enhancement, Maintenance, Protection, and Exploitation (DEMPE) functions rather than mere legal ownership.\n"
                "• Three-Tier Documentation (Chapter V / BEPS Action 13): Master File, Local File, and Country-by-Country Report (CbCR for groups ≥ EUR 750m).",
            ),
        ],
    },
}


def main() -> int:
    total_docs = 0
    total_sections = 0
    for fname, mapping in ENRICHMENTS_BY_FILE.items():
        path = INTL_DATA_DIR / fname
        if not path.exists():
            continue
        data = json.loads(path.read_text(encoding="utf-8"))
        file_docs = 0
        file_secs = 0
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
            file_docs += 1
            file_secs += len(new_arts)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"{fname}: enriched {file_docs} standards with {file_secs} technical sections")
        total_docs += file_docs
        total_sections += file_secs
    print(f"Total newly enriched: {total_docs} standards / {total_sections} technical sections.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
