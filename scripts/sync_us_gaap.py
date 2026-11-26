#!/usr/bin/env python3
"""
生成美国会计准则（US GAAP — FASB ASC 核心主题）公开合规数据源（intl_data/us_gaap_accounting.json）

设计原则：
1. 严格遵守 FAF/FASB 版权边界：不收录付费/受版权保护的 ASC 原文逐字稿；
   收录官方 Topic 编号与名称、按 ASC 子节号（如 ASC 606-10-25）索引的原创技术精要、
   US GAAP vs. IFRS vs. CAS 三方实务差异对照及官方 asc.fasb.org 入口。
2. 建立完整的 US GAAP ↔ IFRS ↔ CAS 三方对照边（intl_mapping）与 US GAAP 内部家族配套边（L1）。
"""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUT_PATH = PROJECT_ROOT / "intl_data" / "us_gaap_accounting.json"

FASB_ASC_URL = "https://asc.fasb.org/"
DELOITTE_COMP_URL = (
    "https://www.deloitte.com/us/en/services/audit-assurance/articles/"
    "us-aers-a-comparison-of-ifrs-standards-and-us-gaap-bridging-the-differences.html"
)

# (code, title, display_title, doc_type, pub_date, eff_date, summary, core_no, core_heading, core_text, diff_text, ifrs_links, cas_links, us_cites)
US_GAAP_SPECS = [
    (
        "CON 8",
        "FASB Concepts Statement No. 8 — Conceptual Framework for Financial Reporting",
        "FASB Conceptual Framework (CON 8)",
        "standard",
        "2024-06-01",
        "2024-06-01",
        "Non-authoritative conceptual foundation guiding the FASB in developing US GAAP, covering the objective of financial reporting (Ch. 1), reporting entity (Ch. 2), qualitative characteristics (Ch. 3), elements (Ch. 4), recognition and derecognition (Ch. 5), measurement (Ch. 6, issued 2024), presentation (Ch. 7), and notes to financial statements (Ch. 8).",
        "CON 8 Ch. 1–8",
        "Conceptual Foundation & 2024 Measurement Chapter",
        "• Fundamental Qualitative Characteristics (Ch. 3): Relevance (predictive/confirmatory value, materiality) and Faithful Representation (complete, neutral, free from error).\n"
        "• Elements of Financial Statements (Ch. 4): Asset = present right of an entity to an economic benefit; Liability = present obligation to transfer an economic benefit.\n"
        "• Measurement (Ch. 6, issued June 2024): Establishes entry price system vs. exit price system as the two overarching measurement frameworks.\n"
        "• Non-authoritative status: Concepts Statements do not override authoritative ASC guidance (ASC 105-10-05-3).",
        "• Largely converged with the IASB Conceptual Framework (2018), though FASB retains its own chapters on Measurement (2024) and Notes (Ch. 8) and places Concepts Statements strictly outside the authoritative GAAP hierarchy.",
        [("Conceptual Framework", "FASB CON 8 与 IASB 概念框架对照")],
        [("企业会计准则——基本准则", "FASB CON 8 与我国企业会计准则基本准则对照")],
        ["ASC 105"],
    ),
    (
        "ASC 105",
        "ASC 105 Generally Accepted Accounting Principles",
        "ASC 105 — Generally Accepted Accounting Principles",
        "standard",
        "2009-07-01",
        "2009-09-15",
        "Establishes the FASB Accounting Standards Codification (ASC) as the single source of authoritative nongovernmental US GAAP (alongside SEC rules/interpretive releases for SEC registrants).",
        "ASC 105-10",
        "Single-Level GAAP Hierarchy & Non-Authoritative Guidance",
        "• Authoritative Sources (ASC 105-10-05-1): Only two levels exist — authoritative (the ASC + SEC guidance for registrants) and non-authoritative.\n"
        "• Analogizing (ASC 105-10-05-2): If a transaction is not specified in the ASC, first analogize to similar transactions within the ASC before consulting non-authoritative sources (CON 8, AICPA guides, IFRS).\n"
        "• True-and-Fair Override: Unlike IAS 1.19, US GAAP effectively prohibits departing from authoritative GAAP in SEC filings.",
        "• IFRS (IAS 8.10–12) provides a formal hierarchy allowing management to look to other standard-setters (including US GAAP) when no IFRS applies; US GAAP centers strictly on the Codification.",
        [("IAS 8", "ASC 105 准则层级与 IAS 8 会计政策选择层级对照"), ("Preface", "ASC 105 与 IFRS 前言定位对照")],
        [("企业会计准则——基本准则", "US GAAP 单一权威层级与我国基本准则体系对照")],
        ["CON 8", "ASC 250"],
    ),
    (
        "ASC 205",
        "ASC 205 Presentation of Financial Statements",
        "ASC 205 — Presentation of Financial Statements",
        "standard",
        "2014-08-27",
        "2016-12-15",
        "Provides baseline presentation rules for financial statements, including Discontinued Operations (ASC 205-20), Liquidation Basis of Accounting (ASC 205-30), and Going Concern disclosures (ASC 205-40).",
        "ASC 205-20 / 205-40",
        "Discontinued Operations, Liquidation Basis & Going Concern",
        "• Discontinued Operations (ASC 205-20): Requires disposal of a component/group of components to represent a 'strategic shift' having a major effect on operations and financial results.\n"
        "• Liquidation Basis (ASC 205-30): Mandatory when liquidation is 'imminent', measuring assets at expected cash collection amounts and accruing liquidation costs.\n"
        "• Going Concern (ASC 205-40): Management must evaluate whether substantial doubt exists within ONE YEAR after the date the financial statements are issued (or available to be issued).",
        "• Going Concern look-forward window: ASC 205-40 measures 12 months from the financial statement ISSUANCE date, whereas IAS 1.26 measures at least 12 months from the REPORTING (balance sheet) date.\n"
        "• Discontinued Operations: ASC 205-20 requires a 'strategic shift', a narrower bar than IFRS 5.32 ('separate major line of business or geographical area').",
        [("IAS 1", "ASC 205 持续经营与列报总则与 IAS 1 对照"), ("IFRS 5", "ASC 205-20 终止经营与 IFRS 5 对照")],
        [("企业会计准则第30号——财务报表列报", "ASC 205 与 CAS 30 财务报表列报对照"), ("企业会计准则第42号——持有待售的非流动资产、处置组和终止经营", "ASC 205-20 与 CAS 42 终止经营对照")],
        ["ASC 210", "ASC 220", "ASC 360"],
    ),
    (
        "ASC 210",
        "ASC 210 Balance Sheet",
        "ASC 210 — Balance Sheet",
        "standard",
        "2013-01-31",
        "2013-01-01",
        "Addresses general balance sheet classification (current vs. noncurrent assets/liabilities, working capital) and strict right-of-setoff / master netting arrangement rules (ASC 210-20).",
        "ASC 210-10 / 210-20",
        "Current/Noncurrent Classification & Right of Setoff",
        "• General Offsetting (ASC 210-20-45-1): Permitted only when four conditions are met (determinable amounts, right to set off, intent to set off, enforceable at law).\n"
        "• Derivative / Repo Exception (ASC 210-20-45-11): Permits net presentation of derivatives and cash collateral executed under an enforceable master netting arrangement even WITHOUT intent to settle net.\n"
        "• Debt Classification: Refinancing completed AFTER the balance sheet date but BEFORE issuance can support noncurrent classification under ASC 470-10 (contrast with IAS 1).",
        "• Offsetting Derivatives: US GAAP allows net balance sheet presentation under master netting agreements (ASC 210-20), whereas IAS 32.42 strictly requires BOTH a legally enforceable right AND intent to settle net/simultaneously — making US bank balance sheets appear smaller than IFRS peers.",
        [("IAS 1", "ASC 210 资产负债表分类与 IAS 1 对照"), ("IAS 32", "ASC 210-20 抵销规则与 IAS 32.42 重大差异对照")],
        [("企业会计准则第30号——财务报表列报", "ASC 210 与 CAS 30 资产负债表列报对照")],
        ["ASC 205", "ASC 470", "ASC 815"],
    ),
    (
        "ASC 220",
        "ASC 220 Income Statement — Reporting Comprehensive Income",
        "ASC 220 — Income Statement & Comprehensive Income (incl. DISE)",
        "standard",
        "2024-11-04",
        "2027-01-01",
        "Governs presentation of net income, Other Comprehensive Income (OCI), Accumulated OCI (AOCI), and footnote disaggregation of income statement expenses (ASC 220-40, added by ASU 2024-03).",
        "ASC 220-10 / 220-40",
        "OCI Presentation & ASU 2024-03 Expense Disaggregation (DISE)",
        "• Single or Two-Statement Approach (ASC 220-10-45): Present comprehensive income in one continuous statement or two consecutive statements.\n"
        "• Recycling: Virtually all US GAAP OCI items (AFS debt unrealized gains/losses, cash flow hedges, pension adjustments, CTA) recycle to net income (unlike IFRS equity FVOCI).\n"
        "• Disaggregation of Income Statement Expenses — DISE (ASC 220-40, ASU 2024-03, effective fiscal years beginning after Dec 15, 2026): Public business entities must disclose tabular breakdowns in footnotes for purchases of inventory, employee compensation, depreciation, intangible amortization, and DD&A embedded in each income statement expense line.",
        "• Structure vs. IFRS 18: IFRS 18 mandates three standardized face-of-P&L categories (Operating, Investing, Financing) plus MPM disclosures; US GAAP (ASU 2024-03) leaves the face of the income statement flexible (SEC Reg S-X drives public company lines) and requires granular expense disaggregation in the footnotes.",
        [("IFRS 18", "ASC 220 (含 ASU 2024-03) 与 IFRS 18 利润表列报及费用分解对照"), ("IAS 1", "ASC 220 综合收益与 IAS 1 对照")],
        [("企业会计准则第30号——财务报表列报", "ASC 220 与 CAS 30 利润表及综合收益列报对照")],
        ["ASC 205", "ASC 280"],
    ),
    (
        "ASC 230",
        "ASC 230 Statement of Cash Flows",
        "ASC 230 — Statement of Cash Flows",
        "standard",
        "2016-11-17",
        "2018-01-01",
        "Establishes classification of cash receipts and payments into Operating, Investing, and Financing activities, including strict rules for restricted cash (ASC 230-10-45-4) and interest/dividends.",
        "ASC 230-10",
        "Cash Flow Classification & Restricted Cash Rules",
        "• Strict Classification (ASC 230-10-45): Interest paid, interest received, and dividends received are ALWAYS Operating; dividends paid are ALWAYS Financing.\n"
        "• Restricted Cash (ASU 2016-18): Beginning and ending cash totals on the Statement of Cash Flows MUST include restricted cash and restricted cash equivalents, with a reconciliation to the balance sheet.\n"
        "• Bank Overdrafts: Classified as Financing activities (not negative cash equivalents).",
        "• Interest & Dividends: US GAAP fixes interest paid/received and dividends received in Operating; IFRS 18 (effective 2027) classifies interest/dividends paid in Financing and interest/dividends received in Investing (for non-financial entities).\n"
        "• Bank Overdrafts: IAS 7.8 allows repayable-on-demand overdrafts to be included in cash & cash equivalents; ASC 230 treats them as Financing.",
        [("IAS 7", "ASC 230 与 IAS 7 现金流量表分类差异对照")],
        [("企业会计准则第31号——现金流量表", "ASC 230 与 CAS 31 现金流量表对照")],
        ["ASC 205", "ASC 210"],
    ),
    (
        "ASC 250",
        "ASC 250 Accounting Changes and Error Corrections",
        "ASC 250 — Accounting Changes & Error Corrections",
        "standard",
        "2005-05-01",
        "2005-12-15",
        "Addresses retrospective application of accounting principle changes, prospective accounting for estimate changes, reporting entity changes, and restatement of prior-period financial statements for errors.",
        "ASC 250-10",
        "Preferability, Estimates, Big R vs. Little r Restatements",
        "• Voluntary Accounting Principle Change (ASC 250-10-45-2): Allowed only if management justifies the new principle as 'preferable' (SEC registrants require a preferability letter from the independent auditor); applied retrospectively.\n"
        "• Change in Accounting Estimate (ASC 250-10-45-17): Applied prospectively; changes in depreciation/amortization method are accounted for as a change in estimate effected by a change in principle.\n"
        "• Error Corrections (ASC 250-10-45-22): Material prior-period errors require 'Big R' restatement (reissuance); immaterial prior errors that would be material if corrected in the current period require 'little r' revision of comparatives (SAB 108 dual rollover/iron-curtain assessment).",
        "• Substantially converged with IAS 8, except US GAAP requires an explicit auditor preferability letter for SEC registrants making voluntary policy changes and has formalized 'Big R' vs. 'little r' SEC restatement practice.",
        [("IAS 8", "ASC 250 与 IAS 8 会计政策、估计变更与差错更正对照")],
        [("企业会计准则第28号——会计政策、会计估计变更和差错更正", "ASC 250 与 CAS 28 对照")],
        ["ASC 105", "ASC 205"],
    ),
    (
        "ASC 260",
        "ASC 260 Earnings Per Share",
        "ASC 260 — Earnings Per Share",
        "standard",
        "2020-08-05",
        "2022-01-01",
        "Establishes computation and presentation of Basic and Diluted EPS for public entities, including the two-class method for participating securities, treasury stock method, and if-converted method.",
        "ASC 260-10",
        "Basic/Diluted EPS, Two-Class & If-Converted Methods",
        "• Treasury Stock Method (ASC 260-10-45-23): Applied to options and warrants; assumed proceeds include unrecognized compensation cost for share-based awards.\n"
        "• Convertible Instruments (ASU 2020-06): Eliminates the treasury stock method for convertible debt settled in cash/shares, requiring the 'if-converted' method (with interest add-back and full share dilution unless principal must be settled in cash).\n"
        "• Two-Class Method (ASC 260-10-45-60): Mandatory when participating securities (e.g., unvested RSAs with nonforfeitable dividends) exist.",
        "• Year-to-date Diluted EPS: ASC 260 averages incremental shares from each interim period, whereas IAS 33 computes YTD diluted EPS independently on a cumulative YTD basis (can yield different results when stock prices fluctuate).",
        [("IAS 33", "ASC 260 与 IAS 33 每股收益对照")],
        [("企业会计准则第34号——每股收益", "ASC 260 与 CAS 34 每股收益对照")],
        ["ASC 470", "ASC 718"],
    ),
    (
        "ASC 270",
        "ASC 270 Interim Reporting",
        "ASC 270 — Interim Reporting",
        "standard",
        "2009-07-01",
        "2009-09-15",
        "Prescribes accounting and disclosure principles for interim periods (quarterly 10-Q reporting), adopting an 'integral' view where each interim period is viewed primarily as an integral part of the annual period.",
        "ASC 270-10",
        "Integral Approach to Interim Periods",
        "• Integral View (ASC 270-10-45-1): Certain annual costs (e.g., property taxes, annual bonuses, volume rebates, LIFO liquidations expected to be replaced by year-end) are allocated/deferred across interim periods.\n"
        "• Income Taxes (ASC 740-270): Computed using the estimated Annual Effective Tax Rate (AETR) applied to YTD ordinary income, with discrete items recognized in the quarter incurred.",
        "• Integral vs. Discrete View: ASC 270 follows an INTEGRAL approach (allowing deferral of certain interim variances/costs expected to reverse by year-end), whereas IAS 34 follows a DISCRETE approach (each interim period stands alone, except for annual effective tax rate).",
        [("IAS 34", "ASC 270 整体观与 IAS 34 独立观中期财务报告差异对照")],
        [("企业会计准则第32号——中期财务报告", "ASC 270 与 CAS 32 中期财务报告对照")],
        ["ASC 205", "ASC 740"],
    ),
    (
        "ASC 275",
        "ASC 275 Risks and Uncertainties",
        "ASC 275 — Risks and Uncertainties",
        "standard",
        "2009-07-01",
        "2009-09-15",
        "Requires disclosures about the nature of operations, use of estimates in preparing financial statements, certain significant estimates reasonably possible to change in the near term (within 1 year), and current vulnerability due to concentrations.",
        "ASC 275-10",
        "Significant Estimates & Concentration Disclosures",
        "• Four Core Disclosure Areas (ASC 275-10-50): (1) Nature of operations; (2) Pervasiveness of estimates; (3) Certain significant estimates (reasonably possible near-term material change); (4) Concentrations (customers, suppliers, lenders, geographic markets, labor).",
        "• Analogous to IAS 1.122–133 (sources of estimation uncertainty) and IFRS 7/IFRS 8 concentration disclosures, consolidated into a dedicated US GAAP topic.",
        [("IAS 1", "ASC 275 重大估计不确定性与 IAS 1.125 对照")],
        [("企业会计准则第30号——财务报表列报", "ASC 275 风险与不确定性披露与 CAS 30 对照")],
        ["ASC 205", "ASC 280"],
    ),
    (
        "ASC 280",
        "ASC 280 Segment Reporting",
        "ASC 280 — Segment Reporting (incl. ASU 2023-07)",
        "standard",
        "2023-11-27",
        "2024-12-15",
        "Requires public entities to report operating segment information through the eyes of the Chief Operating Decision Maker (CODM), significantly expanded by ASU 2023-07 to mandate disclosure of significant segment expenses.",
        "ASC 280-10",
        "CODM Approach & ASU 2023-07 Significant Segment Expenses",
        "• Identification & Aggregation (ASC 280-10-50-1 to 50-12): Operating segments identified via CODM review; quantitative 10% revenue/profit/asset thresholds and 75% consolidated external revenue coverage test.\n"
        "• Significant Segment Expenses (ASU 2023-07, effective FY2024+): Must disclose significant segment expense categories regularly provided to the CODM and included in segment profit/loss, plus the title/position of the CODM and single-reportable-segment entity disclosures.\n"
        "• Multiple Profit Measures: ASU 2023-07 permits disclosing additional CODM profit measures alongside the measure most consistent with GAAP.",
        "• Converged with IFRS 8 on the CODM management approach, though ASU 2023-07's mandatory significant segment expense table goes beyond current IFRS 8 requirements; matrix organizations use products/services under ASC 280-10-50-9.",
        [("IFRS 8", "ASC 280 (含 ASU 2023-07) 与 IFRS 8 经营分部对照")],
        [("企业会计准则第35号——分部报告", "ASC 280 与 CAS 35 分部报告对照")],
        ["ASC 220", "ASC 275"],
    ),
    (
        "ASC 310",
        "ASC 310 Receivables",
        "ASC 310 — Receivables",
        "standard",
        "2022-03-31",
        "2023-01-01",
        "Covers recognition, measurement, nonrefundable loan origination fees/costs (ASC 310-20), and loan modifications to borrowers experiencing financial difficulty (ASU 2022-02, eliminating TDR accounting).",
        "ASC 310-10 / 310-20",
        "Receivables, Loan Origination Fees & ASU 2022-02 Modifications",
        "• Loan Origination Fees & Direct Costs (ASC 310-20): Deferred and recognized over the life of the loan as an adjustment of yield using the effective interest method.\n"
        "• Elimination of TDRs (ASU 2022-02): Eliminated separate Troubled Debt Restructuring (TDR) measurement for creditors adopting CECL (ASC 326), replacing it with general modification guidance and enhanced vintage gross write-off disclosures.",
        "• Credit impairment of receivables is governed by ASC 326 (lifetime CECL from day 1), whereas IFRS 9 applies a 3-stage model (with a simplified lifetime ECL option for trade receivables).",
        [("IFRS 9", "ASC 310 应收款项及贷款修改与 IFRS 9 对照")],
        [("企业会计准则第22号——金融工具确认和计量", "ASC 310 与 CAS 22 应收款项核算对照")],
        ["ASC 326", "ASC 860"],
    ),
    (
        "ASC 320",
        "ASC 320 Investments — Debt Securities",
        "ASC 320 — Investments: Debt Securities",
        "standard",
        "2016-06-16",
        "2020-01-01",
        "Establishes the three-category classification model for debt securities — Held-to-Maturity (HTM), Trading, and Available-for-Sale (AFS) — and their balance sheet/OCI accounting.",
        "ASC 320-10",
        "HTM, Trading & Available-for-Sale (AFS) Debt Classification",
        "• Held-to-Maturity — HTM (ASC 320-10-25-1): Amortized cost; requires positive intent and ability to hold to maturity (selling HTM triggers strict 'tainting' rules).\n"
        "• Trading: Measured at fair value through net income (FVTPL).\n"
        "• Available-for-Sale — AFS: Measured at fair value with unrealized gains/losses in OCI (recycled to net income upon sale); credit losses recorded via allowance under ASC 326-30 (capped at fair value floor).",
        "• Classification Driver: US GAAP classifies debt securities by management intent (HTM/Trading/AFS) without an SPPI cash-flow test; IFRS 9 classifies financial assets by BOTH Business Model AND SPPI contractual cash flow characteristics.",
        [("IFRS 9", "ASC 320 债务证券三分类与 IFRS 9 金融资产分类对照")],
        [("企业会计准则第22号——金融工具确认和计量", "ASC 320 与 CAS 22 债权投资/其他债权投资对照")],
        ["ASC 321", "ASC 326", "ASC 825"],
    ),
    (
        "ASC 321",
        "ASC 321 Investments — Equity Securities",
        "ASC 321 — Investments: Equity Securities",
        "standard",
        "2016-01-05",
        "2018-01-01",
        "Requires all equity investments without significant influence or control to be measured at Fair Value Through Net Income (FVTPL), with an optional measurement alternative for equity securities without a readily determinable fair value.",
        "ASC 321-10",
        "Mandatory FVTPL & Measurement Alternative for Private Equity",
        "• Default Rule (ASC 321-10-35-1): All equity securities (outside equity method/consolidation) are measured at fair value with changes recognized in NET INCOME — NO FVOCI election exists under US GAAP.\n"
        "• Measurement Alternative (ASC 321-10-35-2): For equity securities without a readily determinable fair value, entities may elect cost minus impairment, plus or minus observable price changes in orderly transactions for identical/similar investments of the same issuer.",
        "• Major Divergence from IFRS 9 / CAS 22: IFRS 9.5.7.5 allows an irrevocable FVOCI election for strategic non-trading equity investments (never recycled to P&L); US GAAP (ASC 321) PROHIBITS FVOCI for equity securities — all fair value swings hit Net Income.",
        [("IFRS 9", "ASC 321 权益证券强制 FVTPL 与 IFRS 9 FVOCI 选择权重大差异")],
        [("企业会计准则第22号——金融工具确认和计量", "ASC 321 与 CAS 22 其他权益工具投资差异对照")],
        ["ASC 320", "ASC 323", "ASC 820"],
    ),
    (
        "ASC 323",
        "ASC 323 Investments — Equity Method and Joint Ventures",
        "ASC 323 — Equity Method & Joint Ventures",
        "standard",
        "2023-03-29",
        "2024-01-01",
        "Governs accounting for investments where the investor exercises significant influence (presumed at 20%–50% voting stock, or >3%–5% for limited partnerships/LLCs) and corporate joint ventures.",
        "ASC 323-10",
        "Significant Influence, Equity Method & Impairment",
        "• Significant Influence Thresholds (ASC 323-10-15): Generally 20%–50% voting stock for corporations; much lower threshold (>3%–5%) for limited partnerships/LLCs maintaining specific ownership accounts.\n"
        "• Fair Value Option (ASC 825-10): Any investor may elect FVTPL for an equity method investment at inception (unlike IAS 28, which restricts FVTPL to venture capital/mutual funds).\n"
        "• Impairment (ASC 323-10-35-32): Written down to fair value only when a decline in value is 'other than temporary' (OTTI); impairment reversals are PROHIBITED.",
        "• Uniform Accounting Policies: IAS 28.35 requires aligning the investee's accounting policies to the investor's; ASC 323 does NOT require conforming accounting policies if the investee follows a valid GAAP alternative.\n"
        "• Impairment Reversal: Prohibited under ASC 323; permitted under IAS 36.",
        [("IAS 28", "ASC 323 与 IAS 28 权益法及重大影响对照"), ("IFRS 11", "ASC 323 合营企业与 IFRS 11 对照")],
        [("企业会计准则第2号——长期股权投资", "ASC 323 与 CAS 2 权益法长期股权投资对照"), ("企业会计准则第40号——合营安排", "ASC 323 与 CAS 40 合营安排对照")],
        ["ASC 321", "ASC 810", "ASC 825"],
    ),
    (
        "ASC 326",
        "ASC 326 Financial Instruments — Credit Losses (CECL)",
        "ASC 326 — Credit Losses (CECL)",
        "standard",
        "2016-06-16",
        "2020-01-01",
        "Replaces the incurred loss model with the Current Expected Credit Losses (CECL) model, requiring immediate Day-1 recognition of full lifetime expected credit losses for financial assets measured at amortized cost.",
        "ASC 326-20 / 326-30",
        "Day-1 Lifetime CECL vs. AFS Debt Credit Loss Model",
        "• Amortized Cost Assets (ASC 326-20): Measure lifetime expected credit losses upon origination/acquisition using historical loss experience, current conditions, and reasonable and supportable forecasts (reverting to historical loss thereafter).\n"
        "• Pooled Assessment: Assets sharing similar risk characteristics MUST be evaluated collectively on a pool basis.\n"
        "• AFS Debt Securities (ASC 326-30): Do NOT use CECL; evaluated individually when FV < amortized cost, with credit loss allowance capped at the excess of amortized cost over fair value (fair value floor).",
        "• Major Divergence from IFRS 9 / CAS 22: ASC 326 recognizes FULL LIFETIME expected credit losses on Day 1 for all amortized-cost loans (creating larger Day-1 provisions); IFRS 9 uses a 3-stage model recognizing only 12-month ECL on Day 1 (Stage 1) and moving to lifetime ECL only after a Significant Increase in Credit Risk (Stage 2).",
        [("IFRS 9", "ASC 326 CECL 全生命周期模型与 IFRS 9 三阶段减值模型核心差异")],
        [("企业会计准则第22号——金融工具确认和计量", "ASC 326 CECL 与 CAS 22 预期信用损失三阶段模型差异对照")],
        ["ASC 310", "ASC 320", "ASC 825"],
    ),
    (
        "ASC 330",
        "ASC 330 Inventory",
        "ASC 330 — Inventory",
        "standard",
        "2015-07-22",
        "2017-01-01",
        "Establishes cost determination (FIFO, Weighted Average, Specific Identification, and LIFO) and subsequent measurement of inventory at Lower of Cost and Net Realizable Value (LCNRV) or Lower of Cost or Market (LCM for LIFO/retail).",
        "ASC 330-10",
        "LIFO Costing, LCNRV vs. LCM & Prohibition of Reversals",
        "• Cost Formulas (ASC 330-10-30-9): FIFO, Average Cost, Specific Identification, AND Last-In, First-Out (LIFO) are all permitted (subject to IRS LIFO conformity rule if used for US tax).\n"
        "• Subsequent Measurement (ASC 330-10-35): FIFO & Average Cost inventory is measured at Lower of Cost and NRV (LCNRV); LIFO and Retail Inventory Method remain measured at Lower of Cost or Market (replacement cost bounded by NRV ceiling and NRV-less-normal-profit floor).\n"
        "• Write-Down Reversals (ASC 330-10-35-14): Once inventory is written down below cost, the reduced amount establishes a NEW cost basis — reversals in subsequent periods are STRICTLY PROHIBITED.",
        "• Two Iconic US GAAP vs. IFRS/CAS Divergences: (1) LIFO is PERMITTED under ASC 330 but PROHIBITED under IAS 2.25 and CAS 1; (2) Reversal of prior inventory write-downs is PROHIBITED under ASC 330 but REQUIRED (up to original cost) under IAS 2.33 and CAS 1.",
        [("IAS 2", "ASC 330 (允许 LIFO、禁止减值转回) 与 IAS 2 重大差异对照")],
        [("企业会计准则第1号——存货", "ASC 330 与 CAS 1 存货计价及跌价准备转回差异对照")],
        ["ASC 270", "ASC 606"],
    ),
    (
        "ASC 340",
        "ASC 340 Other Assets and Deferred Costs",
        "ASC 340 — Other Assets & Contract Costs (ASC 340-40)",
        "standard",
        "2014-05-28",
        "2018-01-01",
        "Covers prepaid expenses, advertising costs (ASC 340-20, generally expensed), and incremental costs of obtaining or fulfilling a customer contract (ASC 340-40, companion to ASC 606).",
        "ASC 340-40",
        "Incremental Costs to Obtain & Costs to Fulfill Contracts",
        "• Costs to Obtain (ASC 340-40-25-1): Capitalize incremental costs (e.g., sales commissions) expected to be recovered; practical expedient allows immediate expensing if amortization period <= 1 year.\n"
        "• Costs to Fulfill (ASC 340-40-25-5): Capitalize if not in scope of another Topic (e.g., ASC 330/360), relate directly to a contract, generate/enhance resources, and are expected to be recovered.\n"
        "• Impairment Reversal: Prohibited under ASC 340-40-35-6 (unlike IFRS 15.104, which requires reversal when impairment conditions cease).",
        "• Converged with IFRS 15.91–104 on contract cost capitalization, EXCEPT impairment reversal of capitalized contract costs is prohibited under ASC 340-40.",
        [("IFRS 15", "ASC 340-40 合同取得与履约成本与 IFRS 15.91–104 对照")],
        [("企业会计准则第14号——收入", "ASC 340-40 与 CAS 14 合同成本对照")],
        ["ASC 606"],
    ),
    (
        "ASC 350",
        "ASC 350 Intangibles — Goodwill and Other",
        "ASC 350 — Intangibles, Goodwill & Crypto Assets (ASC 350-60)",
        "standard",
        "2023-12-13",
        "2025-01-01",
        "Governs goodwill impairment testing at the Reporting Unit level (single-step FV < carrying amount), indefinite/finite-lived intangibles, internal-use software (ASC 350-40), and fair value accounting for crypto assets (ASC 350-60, ASU 2023-08).",
        "ASC 350-20 / 350-40 / 350-60",
        "Goodwill Reporting Units, Cloud Computing & Crypto Assets",
        "• Goodwill Impairment (ASC 350-20-35): Tested annually (or upon triggering event) at the Reporting Unit level (operating segment or one level below). Optional qualitative 'Step 0' screen; quantitative test compares Reporting Unit fair value to carrying amount (no reversal allowed).\n"
        "• Internal-Use Software & Cloud Computing (ASC 350-40): Capitalize application-development-stage costs and qualifying cloud implementation costs; expense preliminary and post-implementation costs.\n"
        "• Crypto Assets (ASC 350-60, ASU 2023-08, effective FY2025+): In-scope fungible crypto assets (e.g., Bitcoin, Ether) MUST be measured at fair value each period with changes in NET INCOME, presented separately on the balance sheet and income statement.",
        "• Goodwill Testing Level & Model: US GAAP tests at the Reporting Unit level using Fair Value only; IAS 36 tests at the CGU level using Recoverable Amount (higher of FVLCD and VIU).\n"
        "• Crypto Assets: ASC 350-60 mandates FVTPL for qualifying crypto assets; under IFRS (IFRIC Agenda Decision 2019), crypto is typically an indefinite-lived intangible under IAS 38 (cost model or revaluation through OCI).",
        [("IAS 38", "ASC 350 无形资产与加密资产与 IAS 38 对照"), ("IAS 36", "ASC 350-20 商誉减值与 IAS 36 CGU 减值差异对照")],
        [("企业会计准则第6号——无形资产", "ASC 350 与 CAS 6 无形资产对照"), ("企业会计准则第8号——资产减值", "ASC 350-20 与 CAS 8 商誉减值对照")],
        ["ASC 360", "ASC 730", "ASC 805", "ASC 985"],
    ),
    (
        "ASC 360",
        "ASC 360 Property, Plant, and Equipment",
        "ASC 360 — Property, Plant & Equipment (Impairment & Held for Sale)",
        "standard",
        "2009-07-01",
        "2009-09-15",
        "Covers historical-cost accounting for PP&E, depreciation, the two-step undiscounted-cash-flow impairment test for long-lived assets held and used (ASC 360-10-35), and held-for-sale classification.",
        "ASC 360-10-35",
        "Historical Cost Only, 2-Step Impairment Test & No Reversals",
        "• No Revaluation Model: PP&E MUST be carried at historical cost less accumulated depreciation and impairment — upward revaluation is strictly prohibited.\n"
        "• 2-Step Impairment Test (ASC 360-10-35-17): Step 1 (Recoverability) compares carrying amount of the asset group to UNDISCOUNTED future cash flows; only if Step 1 fails does Step 2 measure impairment as carrying amount minus Fair Value.\n"
        "• Impairment Reversal: Prohibited for held-and-used assets (ASC 360-10-35-20); permitted up to prior carrying amount only for assets classified as Held for Sale.",
        "• Two Major Divergences from IAS 16 / IAS 36: (1) ASC 360 uses a 2-step UNDISCOUNTED recoverability screen (fewer impairments triggered than IAS 36's 1-step discounted recoverable amount); (2) Impairment reversals and upward revaluation are prohibited under US GAAP (both permitted under IFRS).",
        [("IAS 16", "ASC 360 固定资产成本模式与 IAS 16 对照"), ("IAS 36", "ASC 360-10 两步法未折现减值测试与 IAS 36 重大差异"), ("IFRS 5", "ASC 360 持有待售资产与 IFRS 5 对照")],
        [("企业会计准则第4号——固定资产", "ASC 360 与 CAS 4 固定资产对照"), ("企业会计准则第8号——资产减值", "ASC 360-10 与 CAS 8 固定资产减值对照")],
        ["ASC 205", "ASC 350", "ASC 410", "ASC 835"],
    ),
    (
        "ASC 405",
        "ASC 405 Liabilities",
        "ASC 405 — Liabilities & Supplier Finance Programs (ASC 405-50)",
        "standard",
        "2022-09-29",
        "2023-01-01",
        "Addresses extinguishment of liabilities (ASC 405-20), joint and several liability arrangements (ASC 405-40), and buyer disclosures for Supplier Finance Programs / reverse factoring (ASC 405-50, ASU 2022-04).",
        "ASC 405-20 / 405-50",
        "Liability Derecognition & Supplier Finance Disclosures",
        "• Extinguishment (ASC 405-20-40-1): Derecognize a liability only when the debtor pays the creditor OR is legally released from being the primary obligor.\n"
        "• Supplier Finance Programs (ASC 405-50, ASU 2022-04): Buyers must disclose key program terms, confirmed obligations outstanding at period-end (and where presented on the balance sheet), and an annual rollforward of obligations.",
        "• Supplier finance disclosures are closely aligned with IAS 7 / IFRS 7 Supplier Finance Arrangements amendments (effective 2024).",
        [("IAS 7", "ASC 405-50 供应链融资披露与 IAS 7 修订对照"), ("IFRS 9", "ASC 405-20 负债终止确认与 IFRS 9.3.3 对照")],
        [("企业会计准则第22号——金融工具确认和计量", "ASC 405-20 与 CAS 22 金融负债终止确认对照")],
        ["ASC 470", "ASC 210"],
    ),
    (
        "ASC 410",
        "ASC 410 Asset Retirement and Environmental Obligations",
        "ASC 410 — Asset Retirement Obligations (ARO) & Environmental",
        "standard",
        "2009-07-01",
        "2009-09-15",
        "Requires recognition of legal obligations associated with the retirement of tangible long-lived assets (ARO, ASC 410-20) at fair value (discounted at credit-adjusted risk-free rate) and environmental remediation liabilities (ASC 410-30).",
        "ASC 410-20 / 410-30",
        "ARO Credit-Adjusted Discount Rate & Layer Accounting",
        "• Scope (ASC 410-20): Applies to LEGAL obligations (statute, contract, promissory estoppel) — excludes purely constructive obligations.\n"
        "• Discount Rate: Credit-adjusted risk-free rate locked in per cash-flow layer (upward revisions create a new layer at current rate; downward revisions use historical rate).\n"
        "• Environmental Obligations (ASC 410-30): Recognized when probable and reasonably estimable (generally undiscounted unless timing/amount are fixed or reliably determinable).",
        "• Major Divergence from IAS 37 / IFRIC 1: IAS 37 includes CONSTRUCTIVE obligations and remeasures the entire provision each period using the current pre-tax market discount rate; ASC 410-20 covers legal obligations only and locks historical credit-adjusted rates by layer.",
        [("IAS 37", "ASC 410-20 弃置义务与 IAS 37 预计负债差异对照"), ("IFRIC 1", "ASC 410-20 分层折现率与 IFRIC 1 对照")],
        [("企业会计准则第4号——固定资产", "ASC 410-20 与 CAS 4 固定资产弃置费用对照"), ("企业会计准则第13号——或有事项", "ASC 410 与 CAS 13 或有事项对照")],
        ["ASC 360", "ASC 450"],
    ),
    (
        "ASC 450",
        "ASC 450 Contingencies",
        "ASC 450 — Contingencies (Loss & Gain Contingencies)",
        "standard",
        "2009-07-01",
        "2009-09-15",
        "Establishes recognition and disclosure rules for loss contingencies (ASC 450-20) and gain contingencies (ASC 450-30), using the higher US GAAP 'probable' threshold (~70%–75%+).",
        "ASC 450-20 / 450-30",
        "Probable Threshold (~75%), Range Minimum & Gain Contingencies",
        "• Loss Contingency Recognition (ASC 450-20-25-2): Accrue when (a) probable (likely to occur, ~70%–75%+ in US practice) AND (b) reasonably estimable.\n"
        "• Range of Loss (ASC 450-20-30-1): If no point within a range is a better estimate than any other, accrue the MINIMUM amount in the range and disclose the upper bound.\n"
        "• Discounting: Generally prohibited unless amount and timing of cash payments are fixed or reliably determinable.\n"
        "• Gain Contingencies (ASC 450-30): Never recognized prior to realization.",
        "• Two Classic Divergences from IAS 37 / CAS 13: (1) Recognition threshold — ASC 450 'probable' (~70–75%+) is significantly higher than IAS 37 'more likely than not' (>50%); (2) Equal-probability range — ASC 450 accrues the MINIMUM of the range, whereas IAS 37 accrues the MIDPOINT (expected value for large populations).",
        [("IAS 37", "ASC 450 (75%门槛、区间下限) 与 IAS 37 (>50%门槛、区间中值) 经典差异")],
        [("企业会计准则第13号——或有事项", "ASC 450 与 CAS 13 或有事项确认门槛及计量差异对照")],
        ["ASC 410", "ASC 460"],
    ),
    (
        "ASC 460",
        "ASC 460 Guarantees",
        "ASC 460 — Guarantees",
        "standard",
        "2009-07-01",
        "2009-09-15",
        "Requires a guarantor to recognize at inception a liability for the fair value of the non-contingent 'stand-ready' obligation to perform under a guarantee, alongside separate contingent loss evaluation (ASC 450 / ASC 326).",
        "ASC 460-10",
        "Stand-Ready Fair Value Liability & Financial Guarantee Interaction",
        "• Dual-Component Model (ASC 460-10-25): At inception, recognize the non-contingent stand-ready obligation at fair value (typically the fee received); separately assess contingent credit/loss exposure under ASC 326-20 (for financial guarantees) or ASC 450-20 (for performance guarantees).",
        "• Financial guarantee contracts under IFRS 9 are measured at the higher of the ECL allowance and the unamortized initial fair value; US GAAP tracks the ASC 460 stand-ready liability and ASC 326 credit allowance separately.",
        [("IFRS 9", "ASC 460 财务担保合同与 IFRS 9 对照")],
        [("企业会计准则第22号——金融工具确认和计量", "ASC 460 与 CAS 22 财务担保合同对照")],
        ["ASC 326", "ASC 450"],
    ),
    (
        "ASC 470",
        "ASC 470 Debt",
        "ASC 470 — Debt (Convertible Debt & Modifications)",
        "standard",
        "2020-08-05",
        "2022-01-01",
        "Governs classification of debt (callable/refinanced obligations), simplified convertible debt accounting without cash-conversion/CCF bifurcation (ASC 470-20, ASU 2020-06), and debt modifications/extinguishments (ASC 470-50, 10% cash-flow test).",
        "ASC 470-10 / 470-20 / 470-50",
        "Convertible Debt (ASU 2020-06) & 10% Modification Test",
        "• Convertible Debt (ASC 470-20, ASU 2020-06): Eliminated beneficial conversion feature (BCF) and cash conversion separation models — most convertible debt is now accounted for as a SINGLE liability at amortized cost (unless embedded derivative bifurcation applies under ASC 815).\n"
        "• Debt Modifications (ASC 470-50-40-10): Substantially different terms (>= 10% change in PV of cash flows) trigger extinguishment accounting (gain/loss in P&L); < 10% is accounted for prospectively via a new effective interest rate (no immediate P&L gain/loss!).\n"
        "• Debt Issuance Costs (ASC 835-30): Presented as a direct deduction from the carrying amount of the debt liability.",
        "• Convertible Debt: IAS 32 ALWAYS requires split accounting (liability + equity component) for compound convertible bonds; ASU 2020-06 accounts for most US GAAP convertible bonds as a single liability.\n"
        "• Non-Substantial Modification (<10%): IFRS 9.5.4.3 requires an IMMEDIATE P&L gain/loss (recalculating PV at original EIR); ASC 470-50 amortizes the difference prospectively with NO Day-1 P&L gain/loss.",
        [("IAS 32", "ASC 470-20 可转债单一负债模型与 IAS 32 复合金融工具分拆重大差异"), ("IFRS 9", "ASC 470-50 债务修改10%测试与 IFRS 9.5.4.3 差异对照")],
        [("企业会计准则第37号——金融工具列报", "ASC 470-20 与 CAS 37 可转债分拆差异对照"), ("企业会计准则第12号——债务重组", "ASC 470-60 与 CAS 12 债务重组对照")],
        ["ASC 210", "ASC 260", "ASC 405", "ASC 480"],
    ),
    (
        "ASC 480",
        "ASC 480 Distinguishing Liabilities from Equity",
        "ASC 480 — Distinguishing Liabilities from Equity",
        "standard",
        "2009-07-01",
        "2009-09-15",
        "Identifies three narrow classes of freestanding financial instruments (mandatorily redeemable shares, repurchase obligations, and certain share-settled obligations with predominantly fixed monetary value) that MUST be classified as liabilities, supplemented by ASC 815-40 and SEC temporary equity (mezzanine) rules.",
        "ASC 480-10",
        "Liability Classification, Indexation (ASC 815-40) & Mezzanine Equity",
        "• Three Mandatory Liability Classes (ASC 480-10-25): (1) Mandatorily redeemable financial instruments; (2) Obligations to repurchase issuer's equity shares by transferring assets; (3) Certain obligations to issue a variable number of shares based predominantly on a fixed monetary amount.\n"
        "• Temporary / Mezzanine Equity (ASC 480-10-S99-3A): SEC registrants must present conditionally redeemable preferred stock (e.g., VC preferred with change-of-control redemption) outside permanent equity in 'mezzanine' equity.",
        "• Major Divergence from IAS 32 / CAS 37: Under IAS 32, conditionally redeemable preferred shares (outside the issuer's sole control) are generally FINANCIAL LIABILITIES; under US GAAP (ASC 480 + SEC S99-3A), they are classified in Temporary/Mezzanine Equity (between liabilities and stockholders' equity), avoiding P&L fair-value swings.",
        [("IAS 32", "ASC 480 夹层权益与 IAS 32 金融负债/权益划分核心差异")],
        [("企业会计准则第37号——金融工具列报", "ASC 480 与 CAS 37 金融负债与权益工具区分对照")],
        ["ASC 470", "ASC 505", "ASC 815"],
    ),
    (
        "ASC 505",
        "ASC 505 Equity",
        "ASC 505 — Equity",
        "standard",
        "2018-06-20",
        "2019-01-01",
        "Covers stockholders' equity transactions including treasury stock (cost vs. par value method), stock dividends and stock splits, spin-offs, and reverse spin-offs.",
        "ASC 505-10 / 505-30",
        "Treasury Stock, Stock Dividends & Spin-Offs",
        "• Treasury Stock (ASC 505-30): Accounted for under the cost method or par value method; no gain or loss is ever recognized in net income on treasury stock transactions.\n"
        "• Small vs. Large Stock Dividends (ASC 505-20): Stock dividends < 20%–25% capitalize retained earnings at FAIR VALUE; large stock dividends (> 20%–25%, stock splits effected in the form of a dividend) capitalize at PAR VALUE.",
        "• Largely aligned with IAS 32 on treasury shares (no P&L recognition), while US GAAP preserves specific small vs. large stock dividend capitalization conventions.",
        [("IAS 32", "ASC 505 库存股与权益交易与 IAS 32.33 对照")],
        [("企业会计准则第37号——金融工具列报", "ASC 505 与 CAS 37 库存股及权益核算对照")],
        ["ASC 480", "ASC 718"],
    ),
    (
        "ASC 606",
        "ASC 606 Revenue from Contracts with Customers",
        "ASC 606 — Revenue from Contracts with Customers",
        "standard",
        "2014-05-28",
        "2018-01-01",
        "Jointly developed with the IASB (converged with IFRS 15), establishing the five-step revenue recognition model based on transfer of control of promised goods or services to customers.",
        "ASC 606-10-25 / 32",
        "Five-Step Model, Licensing IP & Key US GAAP Elections",
        "• Five-Step Core Principle (ASC 606-10-05-4): (1) Identify contract (collectibility = 'probable', ~75%+); (2) Identify distinct performance obligations (shipping/handling may be elected as a fulfillment activity); (3) Determine transaction price (variable consideration constraint, significant financing component, non-cash consideration measured at contract inception); (4) Allocate transaction price via SSP; (5) Recognize revenue over time or at a point in time.\n"
        "• Licensing Intellectual Property (ASC 606-10-55-58): Distinguishes 'Functional IP' (point in time, e.g., software, films) vs. 'Symbolic IP' (over time, e.g., brands, logos).\n"
        "• Sales Tax Election (ASC 606-10-32-2A): Policy election to exclude all sales/similar taxes from the transaction price.",
        "• Subtle Divergences from IFRS 15 / CAS 14: (1) Step 1 Collectibility — ASC 606 'probable' (~75%+) is higher than IFRS 15 (>50%); (2) Shipping & Handling — ASC 606 permits an explicit fulfillment-cost election after control transfer (not in IFRS 15); (3) Non-cash consideration — ASC 606 mandates measurement at contract inception (IFRS 15 does not specify date); (4) IP licensing uses Functional vs. Symbolic distinction.",
        [("IFRS 15", "ASC 606 与 IFRS 15 趋同核心及实务细微差异对照")],
        [("企业会计准则第14号——收入", "ASC 606 与 CAS 14 五步法收入确认三方对照")],
        ["ASC 340", "ASC 610", "ASC 842"],
    ),
    (
        "ASC 610",
        "ASC 610 Other Income",
        "ASC 610 — Other Income (Nonfinancial Asset Derecognition)",
        "standard",
        "2017-02-22",
        "2018-01-01",
        "Governs recognition of gains and losses from the derecognition of nonfinancial assets (e.g., real estate, PP&E, intangibles) transferred to non-customers, applying ASC 606 control-transfer and measurement principles.",
        "ASC 610-20",
        "Derecognition of Nonfinancial Assets & In-Substance Nonfinancial Assets",
        "• Scope (ASC 610-20-15): Covers sales of nonfinancial assets and subsidiaries consisting solely of 'in-substance nonfinancial assets' to counterparties that are NOT customers.\n"
        "• Partial Sales: Full gain/loss recognition upon loss of control (measuring retained noncontrolling interest at fair value), aligning with ASC 810 deconsolidation.",
        "• Complements ASC 606 (customer contracts) and ASC 810 (deconsolidation of businesses); under IFRS, nonfinancial asset disposals sit inside IAS 16 / IAS 38 referencing IFRS 15 control transfer.",
        [("IFRS 15", "ASC 610-20 非金融资产终止确认引用控制权转移与 IFRS 15 对照")],
        [("企业会计准则第4号——固定资产", "ASC 610-20 与 CAS 4 固定资产处置损益对照")],
        ["ASC 606", "ASC 360", "ASC 810"],
    ),
    (
        "ASC 715",
        "ASC 715 Compensation — Retirement Benefits",
        "ASC 715 — Retirement Benefits (Pensions & OPEB)",
        "standard",
        "2017-03-10",
        "2018-01-01",
        "Establishes accounting for defined benefit pension plans (ASC 715-30), other postretirement benefits (ASC 715-60), and defined contribution plans (ASC 715-70).",
        "ASC 715-30",
        "Corridor Amortization, Expected Return & Prior Service Cost",
        "• Net Periodic Benefit Cost: Service cost is presented with other compensation costs; non-service components (interest cost, expected return on plan assets, amortizations) are presented outside operating income (ASU 2017-07).\n"
        "• Actuarial Gains/Losses & Prior Service Cost: Initially recorded in OCI and subsequently AMORTIZED (recycled) into net income (corridor approach or systematic method).\n"
        "• Expected Return on Plan Assets: Uses expected long-term rate of return on plan assets (not the discount rate).",
        "• Major Divergence from IAS 19 / CAS 9: IAS 19 calculates a single 'net interest' using the discount rate, recognizes past service cost IMMEDIATELY in P&L, and NEVER recycles OCI remeasurements to P&L; ASC 715 uses expected return on plan assets and recycles actuarial gains/losses and prior service cost from AOCI into P&L.",
        [("IAS 19", "ASC 715 预期回报率与AOCI摊销重分类 vs IAS 19 净利息与永不重分类差异")],
        [("企业会计准则第9号——职工薪酬", "ASC 715 与 CAS 9 设定受益计划核算差异对照")],
        ["ASC 220", "ASC 718"],
    ),
    (
        "ASC 718",
        "ASC 718 Compensation — Stock Compensation",
        "ASC 718 — Stock Compensation (Share-Based Payment)",
        "standard",
        "2018-06-20",
        "2019-01-01",
        "Governs equity-classified and liability-classified share-based payment awards to both employees and nonemployees (aligned by ASU 2018-07), measured at grant-date fair value.",
        "ASC 718-10 / 718-20",
        "Grant-Date Fair Value, Graded Vesting & Forfeiture Policy",
        "• Service/Performance/Market Conditions (ASC 718-10-30): Service & performance conditions affect quantity of awards vested; market conditions (e.g., TSR) are baked into grant-date fair value.\n"
        "• Graded Vesting Policy Election (ASC 718-10-35-8): For awards with ONLY service conditions, entities may elect STRAIGHT-LINE attribution over the total requisite service period (or accelerated tranche-by-tranche attribution).\n"
        "• Forfeitures (ASU 2016-09): Policy election to either estimate forfeitures upfront OR account for forfeitures as they occur; excess tax benefits/deficiencies are recognized in Income Tax Expense (P&L), not APIC.",
        "• Three Key Divergences from IFRS 2 / CAS 11: (1) Graded vesting — US GAAP permits straight-line attribution, whereas IFRS 2 MANDATES accelerated tranche-by-tranche attribution; (2) Forfeitures — US GAAP allows recognizing as incurred; (3) Deferred taxes — US GAAP books excess tax benefits to P&L (IFRS 2 caps P&L tax benefit at book expense and puts excess in equity).",
        [("IFRS 2", "ASC 718 分期行权直线法与税盾入损益 vs IFRS 2 核心差异")],
        [("企业会计准则第11号——股份支付", "ASC 718 与 CAS 11 股份支付对照")],
        ["ASC 260", "ASC 505", "ASC 740"],
    ),
    (
        "ASC 730",
        "ASC 730 Research and Development",
        "ASC 730 — Research and Development",
        "standard",
        "2009-07-01",
        "2009-09-15",
        "Requires all research and development (R&D) costs to be expensed as incurred (with narrow exceptions for software development under ASC 350-40 / ASC 985-20 and IPR&D acquired in a business combination under ASC 805).",
        "ASC 730-10",
        "Immediate Expensing of R&D Costs",
        "• General Rule (ASC 730-10-25-1): ALL internal research AND development costs are expensed as incurred — no capitalization of development phase costs.\n"
        "• Narrow Exceptions: (1) Internal-use software (ASC 350-40) and external-sale software post-technological feasibility (ASC 985-20); (2) Assets with alternative future uses (depreciated to R&D); (3) In-process R&D (IPR&D) acquired in a business combination (capitalized as indefinite-lived intangible under ASC 805 / ASC 350).",
        "• Iconic Divergence from IAS 38 / CAS 6: IAS 38.57 and CAS 6 REQUIRE capitalization of internal development costs once 6 technical/commercial feasibility criteria are met; ASC 730 EXPENSES virtually all internal R&D as incurred (except software), significantly impacting EBITDA and R&D-heavy tech/pharma comparisons.",
        [("IAS 38", "ASC 730 研发费用全部费用化 vs IAS 38 开发阶段资本化重大差异")],
        [("企业会计准则第6号——无形资产", "ASC 730 与 CAS 6 内部研发支出资本化差异对照")],
        ["ASC 350", "ASC 805", "ASC 985"],
    ),
    (
        "ASC 740",
        "ASC 740 Income Taxes",
        "ASC 740 — Income Taxes (incl. ASU 2023-09)",
        "standard",
        "2023-12-14",
        "2025-01-01",
        "Establishes the asset-and-liability approach for current and deferred income taxes, uncertain tax positions (2-step MLTN >50%), valuation allowances, and expanded rate reconciliation & cash-taxes-paid disclosures (ASU 2023-09).",
        "ASC 740-10",
        "Enacted Tax Rates, Valuation Allowance, UTPs & ASU 2023-09",
        "• Enacted Rates Only (ASC 740-10-30-8): Deferred taxes MUST use ENACTED tax rates (not 'substantively enacted').\n"
        "• Valuation Allowance (ASC 740-10-30-5): Recognize all DTAs in full, then reduce via a contra-asset Valuation Allowance if it is 'more likely than not' (>50%) that some portion will not be realized.\n"
        "• Uncertain Tax Positions — UTPs (ASC 740-10-25-6): 2-step model — Step 1: Recognition requires >50% ('more likely than not') technical merits; Step 2: Measurement at the largest amount with >50% cumulative likelihood of realization.\n"
        "• ASU 2023-09 (effective FY2025+ for PBEs): Mandates standardized 8-category tabular rate reconciliation (both % and dollar amounts) and disaggregated income taxes paid by federal/state/foreign jurisdiction (>=5% threshold).",
        "• Key Divergences from IAS 12 / CAS 18: (1) Enacted vs. substantively enacted rates; (2) Intra-entity inventory transfers — ASC 740 defers seller's tax expense as a prepaid until sold to third party (IAS 12 recognizes DTA immediately at buyer's rate); (3) UTPs — ASC 740 uses cumulative-probability largest >50% amount (IFRIC 23 uses most likely amount or expected value); (4) Pillar Two — FASB treats GloBE as an Alternative Minimum Tax (period cost, no deferred tax).",
        [("IAS 12", "ASC 740 (含 ASU 2023-09) 与 IAS 12 所得税差异对照"), ("IFRIC 23", "ASC 740-10 不确定税务处理两步法与 IFRIC 23 对照"), ("OECD Pillar Two (GloBE)", "ASC 740 将支柱二视同 AMT 当期费用处理与 OECD GloBE 衔接")],
        [("企业会计准则第18号——所得税", "ASC 740 与 CAS 18 所得税会计对照")],
        ["ASC 270", "ASC 718", "ASC 805"],
    ),
    (
        "ASC 805",
        "ASC 805 Business Combinations",
        "ASC 805 — Business Combinations",
        "standard",
        "2023-08-23",
        "2025-01-01",
        "Applies the acquisition method to business combinations (measuring identifiable assets, liabilities, and noncontrolling interests at fair value), including the 'screen test' for asset acquisitions, pushdown accounting option (ASC 805-50), and joint venture formation at fair value (ASU 2023-05).",
        "ASC 805-10 / 805-50",
        "Screen Test, Full Goodwill, Pushdown Accounting & JV Formation",
        "• Definition of a Business — Screen Test (ASC 805-10-55-5A): If substantially all fair value of gross assets acquired is concentrated in a single identifiable asset (or group of similar assets), it is an ASSET acquisition, NOT a business combination.\n"
        "• Noncontrolling Interest (NCI): MUST be measured at FAIR VALUE (full goodwill method only — no proportionate-share partial goodwill option).\n"
        "• Pushdown Accounting (ASC 805-50-25-4): An acquired entity may ELECT to apply pushdown accounting in its standalone financial statements upon a change-in-control event.\n"
        "• Joint Venture Formations (ASU 2023-05, effective Jan 1, 2025): Newly formed JVs measure contributed net assets at fair value upon formation.",
        "• Key Divergences from IFRS 3 / CAS 20: (1) NCI measurement — ASC 805 requires FAIR VALUE (full goodwill), whereas IFRS 3 allows an election between fair value and proportionate share of identifiable net assets; (2) Pushdown accounting — permitted under ASC 805-50, not permitted under IFRS; (3) Contingent liabilities — ASC 805 recognizes at FV only if determinable during measurement period (otherwise falls back to ASC 450).",
        [("IFRS 3", "ASC 805 全商誉法与下推会计 vs IFRS 3 差异对照")],
        [("企业会计准则第20号——企业合并", "ASC 805 与 CAS 20 企业合并对照")],
        ["ASC 350", "ASC 740", "ASC 810", "ASC 820"],
    ),
    (
        "ASC 810",
        "ASC 810 Consolidation",
        "ASC 810 — Consolidation (VIE & Voting Interest Models)",
        "standard",
        "2015-02-18",
        "2016-01-01",
        "Establishes the two-tier US GAAP consolidation framework: first evaluate the Variable Interest Entity (VIE) model (primary beneficiary = power + economics), then the Voting Interest Entity (VOE) model (>50% voting shares).",
        "ASC 810-10",
        "Dual Consolidation Model: VIE Primary Beneficiary & VOE",
        "• Step 1 — VIE Model (ASC 810-10-15 / 25): An entity is a VIE if equity at risk is insufficient, equity holders lack decision-making power/obligation to absorb losses/right to receive residual returns, or voting rights are disproportionate. The Primary Beneficiary consolidates when it has BOTH (a) power to direct activities that most significantly impact economic performance AND (b) obligation to absorb losses or right to receive benefits that could potentially be significant.\n"
        "• Step 2 — Voting Interest Model: If not a VIE, consolidation generally requires >50% of voting shares (no 'de facto' control concept).\n"
        "• Deconsolidation (ASC 810-10-40): Full gain/loss in P&L with retained investment remeasured to fair value.",
        "• Major Divergence from IFRS 10 / CAS 33: IFRS 10 uses a SINGLE control model (including 'de facto' control with <50% voting rights and consideration of substantive potential voting rights); ASC 810 uses a DUAL VIE/VOE model and generally ignores de facto control and potential voting rights under the VOE model.",
        [("IFRS 10", "ASC 810 VIE/VOE双模型与 IFRS 10 单一控制模型核心差异"), ("IFRS 12", "ASC 810 VIE披露与 IFRS 12 对照")],
        [("企业会计准则第33号——合并财务报表", "ASC 810 与 CAS 33 合并财务报表及VIE架构对照")],
        ["ASC 323", "ASC 805", "ASC 850"],
    ),
    (
        "ASC 815",
        "ASC 815 Derivatives and Hedging",
        "ASC 815 — Derivatives & Hedging",
        "standard",
        "2022-03-28",
        "2023-01-01",
        "Governs definition and FVTPL accounting for freestanding/embedded derivatives, own-equity scope exceptions (ASC 815-40), and fair value, cash flow, and net investment hedge accounting (including Portfolio Layer Method, ASU 2022-01).",
        "ASC 815-10 / 815-20 / 815-40",
        "Derivative Definition, Hedge Accounting & ASC 815-40 Equity Indexation",
        "• Derivative Characteristics (ASC 815-10-15-83): Underlying + notional/payment provision, little or no initial net investment, AND net settlement (including readily convertible to cash).\n"
        "• Hedge Accounting (ASC 815-20): Requires 'highly effective' (80%–125% corridor in practice) at inception and ongoing; Fair Value Hedges (incl. Portfolio Layer Method for closed prepayable pools), Cash Flow Hedges (entire change in hedging instrument recorded in OCI and reclassified when hedged item affects P&L), and Net Investment Hedges.\n"
        "• Contracts in Entity's Own Equity (ASC 815-40): 2-step indexation & equity-classification framework (critical for SPAC warrants and convertible features).",
        "• Hedge Effectiveness: IFRS 9 eliminated the rigid 80%–125% quantitative bright line in favor of an economic relationship principle; ASC 815 retains 'highly effective' (though ASU 2017-12 allows qualitative ongoing assessments and eliminated separate ineffectiveness measurement for cash flow hedges).",
        [("IFRS 9", "ASC 815 套期会计与嵌入式衍生工具与 IFRS 9 对照")],
        [("企业会计准则第24号——套期会计", "ASC 815 与 CAS 24 套期会计对照")],
        ["ASC 210", "ASC 320", "ASC 480", "ASC 820"],
    ),
    (
        "ASC 820",
        "ASC 820 Fair Value Measurement",
        "ASC 820 — Fair Value Measurement",
        "standard",
        "2022-06-30",
        "2024-01-01",
        "Defines fair value as an exit price in an orderly transaction between market participants, establishes the 3-level Fair Value Hierarchy (Levels 1, 2, 3), and includes the NAV practical expedient for investment funds.",
        "ASC 820-10",
        "Exit Price, 3-Level Hierarchy & NAV Practical Expedient",
        "• Definition (ASC 820-10-35-2): Exit price in the principal (or most advantageous) market; nonperformance risk incorporated for liabilities.\n"
        "• Fair Value Hierarchy (ASC 820-10-35-37): Level 1 (quoted prices in active markets), Level 2 (observable inputs), Level 3 (unobservable inputs — requires quantitative range/weighted-average disclosures and rollforward).\n"
        "• NAV Practical Expedient (ASC 820-10-35-59): Permits measuring qualifying investment fund interests at Net Asset Value (NAV) without leveling them in the hierarchy.\n"
        "• Contractual Sale Restrictions (ASU 2022-03): Entity-specific contractual restrictions on selling an equity security are NOT considered in measuring its fair value.",
        "• Substantially converged with IFRS 13, except US GAAP includes the explicit NAV practical expedient (ASC 820-10-35-59) and allows Day-1 gains/losses when fair value is supported by observable/unobservable exit-price evidence (IFRS 9.B5.1.2A strictly defers Day-1 gains unless based solely on observable market data).",
        [("IFRS 13", "ASC 820 与 IFRS 13 公允价值计量高度趋同与实务差异对照")],
        [("企业会计准则第39号——公允价值计量", "ASC 820 与 CAS 39 公允价值计量三方对照")],
        ["ASC 320", "ASC 321", "ASC 805", "ASC 815"],
    ),
    (
        "ASC 825",
        "ASC 825 Financial Instruments",
        "ASC 825 — Financial Instruments (Fair Value Option & Disclosures)",
        "standard",
        "2016-01-05",
        "2018-01-01",
        "Provides an unconditional instrument-by-instrument Fair Value Option (FVO) for most financial assets and financial liabilities (ASC 825-10-25), with own-credit changes for FVO liabilities presented in OCI, plus fair value footnote disclosures.",
        "ASC 825-10",
        "Unconditional Fair Value Option & Own-Credit OCI",
        "• Fair Value Option (ASC 825-10-25-1): Irrevocable election at initial recognition for eligible financial instruments (including equity method investments under ASC 323) — NO accounting-mismatch qualification required.\n"
        "• Instrument-Specific Credit Risk (ASC 825-10-45-5): Changes in fair value of FVO financial liabilities attributable to the issuer's own credit risk are presented in OCI (and recycled to P&L upon derecognition).",
        "• Fair Value Option Bar: ASC 825 allows an unconditional FVO; IFRS 9.4.1.5 / 4.2.2 restricts the FVO to eliminating an accounting mismatch or managing a group on a fair value basis.",
        [("IFRS 9", "ASC 825 无条件公允价值选择权与 IFRS 9 差异对照"), ("IFRS 7", "ASC 825 金融工具公允价值披露与 IFRS 7 对照")],
        [("企业会计准则第37号——金融工具列报", "ASC 825 与 CAS 37 金融工具披露对照")],
        ["ASC 320", "ASC 321", "ASC 323", "ASC 326"],
    ),
    (
        "ASC 830",
        "ASC 830 Foreign Currency Matters",
        "ASC 830 — Foreign Currency Matters",
        "standard",
        "2009-07-01",
        "2009-09-15",
        "Governs determination of functional currency, remeasurement of foreign currency transactions, translation of foreign entity financial statements (current rate method with CTA in OCI), and highly inflationary economies (>=100% 3-year cumulative inflation).",
        "ASC 830-10 / 830-30",
        "Functional Currency, Translation & Highly Inflationary Economies",
        "• Functional Currency (ASC 830-10-45): Determined by evaluating economic indicators (cash flows, sales prices, sales market, expenses, financing, intercompany) without a strict primary/secondary hierarchy.\n"
        "• Translation (ASC 830-30): Assets/liabilities at closing rate, P&L at weighted-average rate, Cumulative Translation Adjustment (CTA) in OCI.\n"
        "• Highly Inflationary Economies (ASC 830-10-45-11): Bright-line >= 100% cumulative 3-year inflation requires remeasuring the foreign entity as if the reporting currency (e.g., USD) were its functional currency.",
        "• Highly Inflationary Accounting: ASC 830 switches functional currency to the parent's reporting currency (temporal remeasurement); IAS 29 restates local-currency statements using a general price index before translating at the closing rate.",
        [("IAS 21", "ASC 830 与 IAS 21 外币折算对照"), ("IAS 29", "ASC 830 高通胀重述法与 IAS 29 差异对照")],
        [("企业会计准则第19号——外币折算", "ASC 830 与 CAS 19 外币折算对照")],
        ["ASC 220", "ASC 815"],
    ),
    (
        "ASC 835",
        "ASC 835 Interest",
        "ASC 835 — Interest (Capitalization & Imputation)",
        "standard",
        "2015-04-07",
        "2016-01-01",
        "Covers capitalization of interest cost for qualifying constructed assets (ASC 835-20) and imputation of interest / presentation of debt issuance costs (ASC 835-30).",
        "ASC 835-20 / 835-30",
        "Interest Capitalization (Avoidable Interest) & Imputation",
        "• Avoidable Interest (ASC 835-20-30): Capitalize interest on qualifying assets during construction based on weighted-average accumulated expenditures multiplied by specific borrowing rate (optional) and general borrowing weighted-average rate.\n"
        "• Temporary Investment Income: Generally NOT netted against capitalized interest (except certain tax-exempt borrowings).\n"
        "• Debt Issuance Costs (ASC 835-30-45-1A): Deducted directly from the carrying amount of the debt liability.",
        "• Temporary Investment Income: IAS 23.12 REQUIRES deducting temporary investment income earned on specific borrowings from capitalized borrowing costs; ASC 835-20 generally prohibits netting investment income.",
        [("IAS 23", "ASC 835-20 利息资本化与 IAS 23 差异对照")],
        [("企业会计准则第17号——借款费用", "ASC 835-20 与 CAS 17 借款费用对照")],
        ["ASC 360", "ASC 470"],
    ),
    (
        "ASC 842",
        "ASC 842 Leases",
        "ASC 842 — Leases (Dual Lessee Model)",
        "standard",
        "2016-02-25",
        "2019-01-01",
        "Requires lessees to recognize Right-of-Use (ROU) assets and lease liabilities on the balance sheet for virtually all leases (>12 months), while retaining a DUAL income-statement model distinguishing Finance Leases from Operating Leases.",
        "ASC 842-20 / 842-30",
        "Dual Lessee Model (Finance vs. Operating), Lessor & Sale-Leaseback",
        "• Lessee Dual Model (ASC 842-20-25): BOTH Finance and Operating leases sit on the balance sheet (ROU asset + Lease Liability). However:\n"
        "  – Finance Lease: Front-loaded expense (ROU amortization + interest expense on lease liability), similar to IFRS 16.\n"
        "  – Operating Lease: SINGLE STRAIGHT-LINE lease expense in operating income (ROU asset is plugged each period so amortization + interest = straight-line rent); cash payments stay in Operating Cash Flows.\n"
        "• Scope Exemptions: Short-term lease election (<= 12 months); NO 'low-value asset' exemption (unlike IFRS 16.5(b)).\n"
        "• Sale-Leaseback (ASC 842-40): If transfer qualifies as a sale under ASC 606, seller-lessee recognizes 100% of the gain/loss immediately (unlike IFRS 16's partial gain restriction).",
        "• One of the Biggest US GAAP vs. IFRS/CAS Divergences: (1) Lessee P&L — ASC 842 keeps a straight-line Operating Lease expense (preserving EBITDA comparability vs. old GAAP), whereas IFRS 16 / CAS 21 uses a SINGLE front-loaded Finance model for all leases; (2) No low-value asset exemption under ASC 842; (3) Full gain on sale-leaseback under ASC 842 vs. partial gain under IFRS 16.",
        [("IFRS 16", "ASC 842 承租人双轨模型(直线法经营租赁) vs IFRS 16 单一模型重大差异")],
        [("企业会计准则第21号——租赁", "ASC 842 与 CAS 21 租赁准则核心差异对照")],
        ["ASC 606", "ASC 360"],
    ),
    (
        "ASC 845",
        "ASC 845 Nonmonetary Transactions",
        "ASC 845 — Nonmonetary Transactions",
        "standard",
        "2009-07-01",
        "2009-09-15",
        "Establishes fair-value measurement for nonmonetary exchanges having commercial substance, and carryover-basis accounting when an exchange lacks commercial substance or fair value is not determinable.",
        "ASC 845-10",
        "Commercial Substance & Fair Value vs. Carryover Basis",
        "• General Rule (ASC 845-10-30-1): Measure nonmonetary exchanges at the fair value of the asset surrendered (or received if more clearly evident), recognizing gain/loss.\n"
        "• Exceptions (ASC 845-10-30-3): Record at carrying amount (no gain) if fair value is not determinable, exchange is to facilitate sales to customers, or transaction lacks commercial substance.",
        "• Broadly aligned with IAS 16.24 / IAS 38.45 and CAS 7 Non-monetary Asset Exchanges (note that exchanges with customers fall under ASC 606 non-cash consideration).",
        [("IAS 16", "ASC 845 非货币性资产交换与 IAS 16.24 对照")],
        [("企业会计准则第7号——非货币性资产交换", "ASC 845 与 CAS 7 非货币性资产交换对照")],
        ["ASC 360", "ASC 606"],
    ),
    (
        "ASC 850",
        "ASC 850 Related Party Disclosures",
        "ASC 850 — Related Party Disclosures",
        "standard",
        "2009-07-01",
        "2009-09-15",
        "Requires footnote disclosures of material related-party transactions, nature of relationships, dollar amounts, and balances due to/from related parties (excluding ordinary compensation arrangements).",
        "ASC 850-10",
        "Related Party Definition & Disclosure Requirements",
        "• Required Disclosures (ASC 850-10-50-1): Nature of relationship(s), description of transactions, dollar amounts for each income statement period, and amounts due from/to related parties at each balance sheet date.\n"
        "• Arm's-Length Representation (ASC 850-10-50-5): Representations that transactions were on arm's-length terms may NOT be made unless substantiated.",
        "• Key Difference from IAS 24 / CAS 36: ASC 850 excludes key management personnel (KMP) compensation disclosures from the financial statement footnotes (covered in SEC proxy statements for public companies), whereas IAS 24.17 mandates KMP compensation disclosures in the footnotes.",
        [("IAS 24", "ASC 850 与 IAS 24 关联方披露（含关键管理人员薪酬差异）对照")],
        [("企业会计准则第36号——关联方披露", "ASC 850 与 CAS 36 关联方披露对照")],
        ["ASC 810"],
    ),
    (
        "ASC 855",
        "ASC 855 Subsequent Events",
        "ASC 855 — Subsequent Events",
        "standard",
        "2010-02-24",
        "2010-02-24",
        "Distinguishes Recognized (Type 1) vs. Nonrecognized (Type 2) subsequent events occurring after the balance sheet date through the date financial statements are issued (SEC filers) or available to be issued (non-SEC entities).",
        "ASC 855-10",
        "Type 1 Recognized vs. Type 2 Nonrecognized Events",
        "• Evaluation Cutoff (ASC 855-10-25): SEC filers evaluate subsequent events through the date financial statements are ISSUED; non-SEC entities evaluate through the date financial statements are AVAILABLE TO BE ISSUED (and must disclose that date).\n"
        "• Recognized vs. Nonrecognized: Conditions existing at the balance sheet date adjust financial statements; conditions arising after the balance sheet date are disclosed if material.",
        "• Cutoff Date: ASC 855 runs through the date financial statements are ISSUED (for SEC filers), whereas IAS 10.3 runs through the date financial statements are AUTHORIZED FOR ISSUE (typically slightly earlier).",
        [("IAS 10", "ASC 855 与 IAS 10 资产负债表日后事项对照")],
        [("企业会计准则第29号——资产负债表日后事项", "ASC 855 与 CAS 29 资产负债表日后事项对照")],
        ["ASC 205", "ASC 450"],
    ),
    (
        "ASC 860",
        "ASC 860 Transfers and Servicing",
        "ASC 860 — Transfers & Servicing (Securitizations & Factoring)",
        "standard",
        "2014-06-12",
        "2015-01-01",
        "Establishes the control-based derecognition criteria for transfers of financial assets (securitizations, receivable factoring, repurchase agreements) requiring legal isolation, transferee pledge/exchange rights, and absence of effective control.",
        "ASC 860-10",
        "Control-Based Derecognition (Legal Isolation) & Repos",
        "• Three Sale Criteria (ASC 860-10-40-5): (a) Legal isolation — transferred assets are put presumptively beyond the reach of the transferor even in bankruptcy ('true sale' legal opinion); (b) Transferee right to pledge/exchange; (c) Transferor does not maintain effective control (e.g., repurchase agreement).\n"
        "• No Continuing Involvement Partial Derecognition: Binary sale vs. secured borrowing outcome for entire financial assets (or qualifying 'participating interests').",
        "• Major Divergence from IFRS 9.3.2 / CAS 23: IFRS 9 focuses primarily on transfer of RISKS AND REWARDS before evaluating control (and permits continuing-involvement partial derecognition); ASC 860 focuses strictly on LEGAL ISOLATION AND CONTROL.",
        [("IFRS 9", "ASC 860 控制权与法律隔离终止确认 vs IFRS 9 风险报酬转移模型差异")],
        [("企业会计准则第23号——金融资产转移", "ASC 860 与 CAS 23 金融资产转移核心差异对照")],
        ["ASC 310", "ASC 810"],
    ),
    (
        "ASC 944",
        "ASC 944 Financial Services — Insurance",
        "ASC 944 — Insurance (incl. LDTI)",
        "standard",
        "2018-08-15",
        "2023-01-01",
        "Governs accounting for short-duration and long-duration insurance contracts, modernized by ASU 2018-12 (Long-Duration Targeted Improvements — LDTI) requiring annual assumption updates, market risk benefits at fair value, and upper-medium-grade bond discounting.",
        "ASC 944-40",
        "Short- vs. Long-Duration Insurance & LDTI Modernization",
        "• Long-Duration Targeted Improvements (LDTI, ASU 2018-12): Liability for future policy benefits updated annually for cash flow assumptions; discount rate updated quarterly via OCI using upper-medium-grade fixed-income instrument yields; Market Risk Benefits (MRBs) measured at fair value; DAC amortized on a constant-level basis.",
        "• Major Divergence from IFRS 17 / CAS 25: IFRS 17 builds a unified current-value Contractual Service Margin (CSM) model across all insurance contracts; US GAAP (ASC 944 + LDTI) retains separate short-duration vs. long-duration models without a CSM.",
        [("IFRS 17", "ASC 944 (LDTI) 与 IFRS 17 保险合同准则核心差异对照")],
        [("企业会计准则第25号——保险合同", "ASC 944 与 CAS 25 保险合同对照")],
        ["ASC 320", "ASC 820"],
    ),
    (
        "ASC 985",
        "ASC 985 Software",
        "ASC 985 — Software (External-Sale Software Costs)",
        "standard",
        "2009-07-01",
        "2009-09-15",
        "Establishes capitalization of costs incurred to develop computer software to be sold, leased, or otherwise marketed (ASC 985-20) once 'technological feasibility' is established through general release.",
        "ASC 985-20",
        "Technological Feasibility Window & Amortization",
        "• Capitalization Window (ASC 985-20-25): Expense all costs as R&D (ASC 730) until 'technological feasibility' (detailed program design or working model) is established; capitalize coding/testing costs until product is available for general release to customers.\n"
        "• Amortization & NRV Test (ASC 985-20-35): Amortize at the greater of revenue-ratio method or straight-line; evaluate unamortized cost against Net Realizable Value each balance sheet date.",
        "• Under US GAAP, software development has two distinct models (ASC 985-20 for external sale vs. ASC 350-40 for internal-use/SaaS); under IFRS, both sit under IAS 38's unified 6-criteria development model.",
        [("IAS 38", "ASC 985-20 外售软件资本化窗口与 IAS 38 对照")],
        [("企业会计准则第6号——无形资产", "ASC 985-20 与 CAS 6 软件研发成本对照")],
        ["ASC 350", "ASC 730"],
    ),
    (
        "Big4 US GAAP Guide",
        "Deloitte Roadmap — Comparing IFRS Accounting Standards and US GAAP (Bridging the Differences)",
        "Deloitte Roadmap: Comparing IFRS & US GAAP",
        "interpretation",
        "2025-10-01",
        "2025-10-01",
        "Public practical comparison guide from Deloitte summarizing the most significant recognition, measurement, presentation, and disclosure differences between US GAAP (FASB ASC) and IFRS Accounting Standards.",
        "Big4 Practical Guide",
        "Top US GAAP vs. IFRS Divergence Map (Reference Only)",
        "• High-Impact Divergence Areas Covered:\n"
        "  – Revenue (ASC 606 vs. IFRS 15): collectibility threshold, shipping/handling election, IP licensing.\n"
        "  – Leases (ASC 842 vs. IFRS 16): dual lessee P&L model vs. single front-loaded model; sale-leaseback gain.\n"
        "  – Financial Instruments & Credit Losses (ASC 320/321/326 vs. IFRS 9): Day-1 lifetime CECL vs. 3-stage ECL; no equity FVOCI.\n"
        "  – Non-Financial Assets (ASC 330/350/360/730 vs. IAS 2/16/36/38): LIFO, no impairment reversals, R&D expensing, 2-step undiscounted PP&E impairment.\n"
        "  – Consolidation & Liabilities/Equity (ASC 810/480/470 vs. IFRS 10/IAS 32): VIE/VOE model, mezzanine equity, single-liability convertible debt.",
        "• Reference guide only (non-authoritative); always verify against authoritative FASB ASC and IFRS texts.",
        [("IFRS 15", "四大美欧准则差异指南覆盖收入"), ("IFRS 16", "四大美欧准则差异指南覆盖租赁"), ("IFRS 9", "四大美欧准则差异指南覆盖金融工具"), ("IAS 36", "四大美欧准则差异指南覆盖资产减值")],
        [],
        ["ASC 606", "ASC 842", "ASC 326", "ASC 350", "ASC 360", "ASC 730", "ASC 740", "ASC 805", "ASC 810"],
    ),
]


def build_docs() -> list[dict]:
    docs: list[dict] = []
    for (
        code,
        title,
        display_title,
        doc_type,
        pub_date,
        eff_date,
        summary,
        core_no,
        core_heading,
        core_text,
        diff_text,
        ifrs_links,
        cas_links,
        us_cites,
    ) in US_GAAP_SPECS:
        is_guide = doc_type == "interpretation"
        src_url = DELOITTE_COMP_URL if is_guide else FASB_ASC_URL
        src_name = "Deloitte US (Public Roadmap)" if is_guide else "FASB Accounting Standards Codification®"
        src_kind = "third_party" if is_guide else "official"
        issuer = "Deloitte" if is_guide else "FASB (Financial Accounting Standards Board)"

        articles = [
            {
                "no": "Overview",
                "heading": "Scope & Core Objective (Public Summary)",
                "text": summary,
                "seq": 0,
            },
            {
                "no": core_no,
                "heading": core_heading,
                "text": core_text,
                "seq": 1,
            },
            {
                "no": "US GAAP vs. IFRS / CAS",
                "heading": "Key Cross-Framework Differences",
                "text": diff_text,
                "seq": 2,
            },
            {
                "no": "Official Access",
                "heading": "Official FASB Codification & Reference Entry",
                "text": (
                    f"Official Portal ({src_name}): {src_url}\n"
                    f"Status: in_force (FASB ASC free Basic View available at https://asc.fasb.org/)."
                ),
                "seq": 3,
            },
        ]

        docs.append(
            {
                "code": code,
                "framework": "US",
                "domain": "accounting",
                "doc_type": doc_type,
                "title": title,
                "display_title": display_title,
                "series_badge": code,
                "doc_no": code,
                "issuer": issuer,
                "pub_date": pub_date,
                "effective_date": eff_date,
                "status": "in_force",
                "version_level": "",
                "version_note": "",
                "source_name": src_name,
                "source_url": src_url,
                "source_kind": src_kind,
                "summary": summary,
                "cited_codes": us_cites,
                "ifrs_links": ifrs_links,
                "cas_links": cas_links,
                "articles": articles,
            }
        )
    return docs


def main() -> int:
    docs = build_docs()
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": dt.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "source": "FASB Accounting Standards Codification® (Public Structured Summaries)",
        "count": len(docs),
        "documents": docs,
    }
    OUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(docs)} US GAAP accounting documents -> {OUT_PATH.relative_to(PROJECT_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
