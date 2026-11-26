#!/usr/bin/env python3
"""
生成美国审计准则（PCAOB / AICPA）、联邦公司与国际税法（IRC）及证券/治理/反腐败法（SOX / SEC / FCPA）
公开合规数据源（intl_data/us_audit_tax_gov.json）

全部内容均为基于 PCAOB、SEC、DOJ 与美国国内税收法典公开官方来源整理的结构化技术精要与三方对照，
严格遵守版权与合规边界。
"""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUT_PATH = PROJECT_ROOT / "intl_data" / "us_audit_tax_gov.json"

PCAOB_HUB = "https://pcaobus.org/oversight/standards/auditing-standards"
PCAOB_AS2201 = "https://pcaobus.org/oversight/standards/auditing-standards/details/AS2201"
SEC_ICFR_URL = "https://www.sec.gov/rules-regulations/2003/03/managements-report-internal-control-over-financial-reporting-certification-disclosure-exchange-act"
FCPA_GUIDE_URL = "https://www.sec.gov/spotlight/fcpa/fcpa-resource-guide.pdf"
US_CODE_T26 = "https://uscode.house.gov/"
TREASURY_TREATY = "https://home.treasury.gov/policy-issues/tax-policy/treaties"

# (code, domain, doc_type, title, display_title, issuer, pub_date, eff_date, source_name, source_url, summary, core_no, core_heading, core_text, diff_text, ifrs_links, cas_links, us_cites)
SPECS = [
    # ==================== US AUDIT (PCAOB & AICPA) ====================
    (
        "PCAOB AS 1000",
        "audit",
        "standard",
        "PCAOB AS 1000 General Responsibilities of the Auditor in Conducting an Audit",
        "PCAOB AS 1000 — General Responsibilities of the Auditor",
        "PCAOB",
        "2024-05-13",
        "2024-12-15",
        "PCAOB Auditing Standards",
        PCAOB_HUB,
        "Modernized overarching PCAOB standard (replacing legacy AS 1001/1005/1010/1015) establishing the auditor's fundamental obligation to protect investors through independent, objective, and professionally skeptical audits of SEC issuers and broker-dealers.",
        "AS 1000.01–.20",
        "Investor Protection Obligation, Independence & 14-Day Documentation Cutoff",
        "• Fundamental Obligation (AS 1000.01): Protects investors through informative, accurate, and independent auditor's reports — transcending the auditor's relationship with management and the audit committee.\n"
        "• Independence & Due Care (AS 1000.04–.12): Independent in fact and appearance (SEC Rule 2-01 + PCAOB ethics rules); exercise professional skepticism and objectively evaluate both corroborating and contradictory evidence.\n"
        "• Modernized Engagement Mechanics: Clarifies engagement partner responsibility for review and accelerates the audit documentation assembly window under AS 1215 from 45 days to 14 days (for large firms).",
        "• Parallel to ISA 200 and China's CSA 1101, but explicitly frames investor protection as the auditor's overriding duty under the Sarbanes-Oxley Act and applies to integrated FS + ICFR audits.",
        [("ISA 200", "PCAOB AS 1000 与 ISA 200 审计总体目标与基本责任对照")],
        [("中国注册会计师审计准则第1101号——注册会计师的总体目标和审计工作的基本要求", "PCAOB AS 1000 与 CSA 1101 总体目标对照")],
        ["PCAOB QC 1000", "PCAOB AS 1215", "PCAOB AS 2201", "SOX (2002)"],
    ),
    (
        "PCAOB QC 1000",
        "audit",
        "standard",
        "PCAOB QC 1000 A Firm's System of Quality Control",
        "PCAOB QC 1000 — Firm Quality Control System",
        "PCAOB",
        "2024-05-13",
        "2025-12-15",
        "PCAOB Quality Control Standards",
        PCAOB_HUB,
        "Risk-based quality control standard for PCAOB-registered public accounting firms requiring an integrated quality control system, annual evaluation reported to the PCAOB on Form QC, and an External Quality Control Function (EQCF) for firms auditing >100 issuers.",
        "QC 1000",
        "Risk-Based QC System, Annual Form QC & External Oversight (EQCF)",
        "• Eight Components: Governance & leadership, ethics & independence, acceptance & continuance, engagement performance, resources, information & communication, monitoring & remediation, and risk assessment.\n"
        "• External Quality Control Function (EQCF): Firms issuing audit reports for >100 issuers annually must establish an independent external oversight function to evaluate significant QC judgments.\n"
        "• Annual Evaluation & Certification: Registered firms must annually evaluate QC effectiveness as of September 30 and report to the PCAOB on Form QC.",
        "• Structurally aligned with IAASB ISQM 1 (8 risk-based components), but adds strict US regulatory features: mandatory Form QC filing with the PCAOB and the EQCF requirement for major firms.",
        [("ISQM 1", "PCAOB QC 1000 与 ISQM 1 会计师事务所质量管理对照")],
        [("会计师事务所质量管理准则第5101号——业务质量管理", "PCAOB QC 1000 与我国质量管理准则第5101号对照")],
        ["PCAOB AS 1000", "PCAOB AS 1220"],
    ),
    (
        "PCAOB AS 1105",
        "audit",
        "standard",
        "PCAOB AS 1105 Audit Evidence",
        "PCAOB AS 1105 — Audit Evidence",
        "PCAOB",
        "2024-06-12",
        "2025-12-15",
        "PCAOB Auditing Standards",
        PCAOB_HUB,
        "Defines sufficient appropriate audit evidence (relevance and reliability), financial statement assertions, testing company-produced information (IPE), and using the work of a company's specialist.",
        "AS 1105.04–.29",
        "Relevance, Reliability, IPE Testing & Technology-Assisted Analysis",
        "• Assertions (AS 1105.11): Existence/occurrence, completeness, valuation/allocation, rights/obligations, presentation/disclosure.\n"
        "• Information Produced by the Company — IPE (AS 1105.10): Auditor must test accuracy and completeness of company-generated reports/data or test controls over them.\n"
        "• Technology-Assisted Analysis (2024 Amendments): Clarifies reliability evaluation when using automated tools and data analytics on external/electronic information.",
        "• Closely aligned with ISA 500, with especially rigorous PCAOB inspection focus on IPE completeness/accuracy testing and external specialist evaluation (Appendix A).",
        [("ISA 500", "PCAOB AS 1105 与 ISA 500 审计证据对照")],
        [("中国注册会计师审计准则第1301号——审计证据", "PCAOB AS 1105 与 CSA 1301 审计证据对照")],
        ["PCAOB AS 1000", "PCAOB AS 2301", "PCAOB AS 2310"],
    ),
    (
        "PCAOB AS 1215",
        "audit",
        "standard",
        "PCAOB AS 1215 Audit Documentation",
        "PCAOB AS 1215 — Audit Documentation",
        "PCAOB",
        "2024-05-13",
        "2024-12-15",
        "PCAOB Auditing Standards",
        PCAOB_HUB,
        "Establishes documentation requirements for audit workpapers, including the 'experienced auditor' standard, 7-year retention period under SOX, and accelerated 14-day documentation completion date.",
        "AS 1215.04–.16",
        "Experienced Auditor Bar, 14-Day Archiving & 7-Year Retention",
        "• Experienced Auditor Standard (AS 1215.06): Documentation must be sufficient for an experienced auditor with no previous connection to the engagement to understand nature, timing, extent, results, and significant conclusions.\n"
        "• Documentation Completion Date (AS 1215.15): Accelerated to 14 days after report release (down from 45 days for large firms under 2024 AS 1000 amendments).\n"
        "• Retention (AS 1215.14): Minimum 7 years from report release date (SOX Section 103).",
        "• Tighter than ISA 230 (which allows up to 60 days for file assembly and 5-year retention under ISQM 1): PCAOB enforces 14-day assembly and 7-year retention.",
        [("ISA 230", "PCAOB AS 1215 (14天归档/7年保存) 与 ISA 230 对照")],
        [("中国注册会计师审计准则第1131号——审计工作底稿", "PCAOB AS 1215 与 CSA 1131 审计工作底稿对照")],
        ["PCAOB AS 1000", "SOX (2002)"],
    ),
    (
        "PCAOB AS 1220",
        "audit",
        "standard",
        "PCAOB AS 1220 Engagement Quality Review",
        "PCAOB AS 1220 — Engagement Quality Review (EQR)",
        "PCAOB",
        "2009-07-28",
        "2009-12-15",
        "PCAOB Auditing Standards",
        PCAOB_HUB,
        "Requires an Engagement Quality Review (EQR) and concurring approval of issuance for EVERY issuer audit and interim review conducted under PCAOB standards.",
        "AS 1220.03–.18",
        "Mandatory EQR, 2-Year Cooling-Off & Concurring Approval",
        "• Mandatory Scope: Required for ALL issuer audits, ICFR audits, and interim financial statement reviews.\n"
        "• Objectivity & Cooling-Off (AS 1220.08): Engagement partner cannot serve as EQR for at least 2 subsequent annual audits.\n"
        "• Concurring Approval (AS 1220.12): Firm may NOT grant permission to use the audit report until the EQR provides concurring approval of issuance.",
        "• Parallel to ISQM 2 (which requires EQR for listed entities and specified high-risk engagements), whereas AS 1220 mandates EQR for 100% of PCAOB issuer engagements.",
        [("ISQM 2", "PCAOB AS 1220 与 ISQM 2 项目质量复核对照")],
        [("会计师事务所质量管理准则第5102号——项目质量复核", "PCAOB AS 1220 与我国质量管理准则第5102号对照")],
        ["PCAOB QC 1000", "PCAOB AS 1000"],
    ),
    (
        "PCAOB AS 1301",
        "audit",
        "standard",
        "PCAOB AS 1301 Communications with Audit Committees",
        "PCAOB AS 1301 — Communications with Audit Committees",
        "PCAOB",
        "2012-08-15",
        "2012-12-15",
        "PCAOB Auditing Standards",
        PCAOB_HUB,
        "Mandates two-way communication between the independent auditor and the audit committee regarding audit strategy, significant risks, critical accounting policies and estimates, uncorrected misstatements, and auditor independence.",
        "AS 1301.04–.26",
        "Audit Strategy, Critical Estimates & Pre-Report Communications",
        "• Mandatory Topics: Terms of engagement, overall audit strategy & significant risks, critical accounting policies/practices, critical accounting estimates, significant unusual transactions, uncorrected/corrected misstatements, and disagreements with management.\n"
        "• Timing (AS 1301.26): All required communications must occur PRIOR to the issuance of the auditor's report (directly linking to CAM identification under AS 3101).",
        "• Parallel to ISA 260 (Revised), with direct statutory tie-in to SOX Section 204 and AS 3101 Critical Audit Matters (only matters communicated or required to be communicated to the audit committee can be CAMs).",
        [("ISA 260 (Revised)", "PCAOB AS 1301 与 ISA 260 治理层沟通对照")],
        [("中国注册会计师审计准则第1151号——与治理层的沟通", "PCAOB AS 1301 与 CSA 1151 与治理层沟通对照")],
        ["PCAOB AS 3101", "SOX (2002)"],
    ),
    (
        "PCAOB AS 2110",
        "audit",
        "standard",
        "PCAOB AS 2110 Identifying and Assessing Risks of Material Misstatement",
        "PCAOB AS 2110 — Risk Assessment",
        "PCAOB",
        "2010-08-05",
        "2010-12-15",
        "PCAOB Auditing Standards",
        PCAOB_HUB,
        "Establishes risk assessment procedures to obtain an understanding of the company, its environment, and its internal control over financial reporting (ICFR) in order to identify and assess risks of material misstatement (including fraud risks and significant risks).",
        "AS 2110.04–.74",
        "Understanding the Company, Walkthroughs & Significant Risks",
        "• Risk Assessment Procedures (AS 2110.05): Understanding industry/regulatory factors, company objectives/strategies, performance measures, and all 5 COSO components of internal control.\n"
        "• Walkthroughs (AS 2110.37): Performing walkthroughs of significant transaction flows to confirm understanding of likely sources of misstatement.\n"
        "• Presumed Fraud Risk (AS 2110.68): Presumption that improper revenue recognition is a fraud risk requiring special audit consideration.",
        "• Parallel to ISA 315 (Revised 2019), integrated directly with AS 2201 ICFR audits for SEC accelerated/large accelerated filers.",
        [("ISA 315 (Revised 2019)", "PCAOB AS 2110 与 ISA 315 风险评估对照")],
        [("中国注册会计师审计准则第1211号——重大错报风险的识别和评估", "PCAOB AS 2110 与 CSA 1211 风险评估对照")],
        ["PCAOB AS 2201", "PCAOB AS 2301", "PCAOB AS 2401"],
    ),
    (
        "PCAOB AS 2201",
        "audit",
        "standard",
        "PCAOB AS 2201 An Audit of Internal Control Over Financial Reporting That Is Integrated with An Audit of Financial Statements",
        "PCAOB AS 2201 — Integrated Audit of ICFR (SOX 404(b))",
        "PCAOB",
        "2007-05-24",
        "2007-11-15",
        "PCAOB Auditing Standards",
        PCAOB_AS2201,
        "The flagship SOX Section 404(b) auditing standard governing integrated audits of Internal Control Over Financial Reporting (ICFR) and financial statements, using a top-down, risk-based approach anchored in the COSO Internal Control framework.",
        "AS 2201.01–.99",
        "Top-Down Approach, Entity-Level Controls, Walkthroughs & Material Weaknesses",
        "• Top-Down Approach (AS 2201.21–.41): Start at the financial statement level → evaluate Entity-Level Controls (ELCs) and period-end financial reporting process → identify significant accounts/disclosures and relevant assertions → select key controls to test (ITGCs + automated/manual controls).\n"
        "• Testing Operating Effectiveness (AS 2201.44–.61): Test design and operating effectiveness as of year-end; perform roll-forward procedures for interim testing.\n"
        "• Deficiency Evaluation (AS 2201.62–.70): Classify into Control Deficiency, Significant Deficiency (communicated to Audit Committee), or Material Weakness (reasonable possibility of material misstatement not prevented/detected timely → triggers ADVERSE ICFR opinion!).",
        "• Unique US Statutory Requirement: Under SOX 404(b), SEC accelerated/large accelerated filers require an independent auditor's opinion on ICFR under AS 2201 (no equivalent mandatory ICFR audit under IFRS/ISAs, though China implemented a parallel mandatory ICFR audit for A-share listed companies under《企业内部控制审计指引》).",
        [("COSO Internal Control (ICIF)", "PCAOB AS 2201 内控整合审计直接以 COSO 五要素为评价标准"), ("ISA 315 (Revised 2019)", "PCAOB AS 2201 内控测试与 ISA 315 内控了解对比")],
        [("企业内部控制配套指引——审计指引", "PCAOB AS 2201 与我国《企业内部控制审计指引》直接对照"), ("企业内部控制基本规范（财会〔2008〕7号）", "PCAOB AS 2201 与我国内控基本规范衔接")],
        ["SOX (2002)", "PCAOB AS 2110", "PCAOB AS 2301", "PCAOB AS 3101"],
    ),
    (
        "PCAOB AS 2301",
        "audit",
        "standard",
        "PCAOB AS 2301 The Auditor's Responses to the Risks of Material Misstatement",
        "PCAOB AS 2301 — Responses to Assessed Risks",
        "PCAOB",
        "2010-08-05",
        "2010-12-15",
        "PCAOB Auditing Standards",
        PCAOB_HUB,
        "Requires designing and implementing overall responses and tailored audit procedures (tests of controls and substantive procedures) whose nature, timing, and extent directly respond to assessed risks of material misstatement.",
        "AS 2301.05–.46",
        "Tests of Controls, Dual-Purpose Tests & Substantive Responses",
        "• Significant & Fraud Risks (AS 2301.11–.15): Must perform substantive procedures specifically responsive to significant risks, including tests of details.\n"
        "• Reliance on Controls (AS 2301.16–.35): Must test operating effectiveness whenever relying on controls to reduce substantive testing (or when substantive procedures alone cannot provide sufficient evidence).\n"
        "• No Rotational Control Testing for ICFR: In an integrated audit (AS 2201), key controls MUST be tested EVERY YEAR (unlike ISA 330's 3-year rotation option for non-significant risks).",
        "• Key Difference from ISA 330: ISA 330.14 permits relying on prior-year control testing once every 3 years for unchanged non-significant controls; in a SOX 404(b) integrated audit under AS 2201/AS 2301, key controls must be tested annually.",
        [("ISA 330", "PCAOB AS 2301 与 ISA 330 风险应对及控制测试频率差异对照")],
        [("中国注册会计师审计准则第1231号——针对评估的重大错报风险采取的应对措施", "PCAOB AS 2301 与 CSA 1231 风险应对对照")],
        ["PCAOB AS 2110", "PCAOB AS 2201", "PCAOB AS 1105"],
    ),
    (
        "PCAOB AS 2310",
        "audit",
        "standard",
        "PCAOB AS 2310 The Auditor's Use of Confirmation",
        "PCAOB AS 2310 — Auditor's Use of Confirmation (Modernized)",
        "PCAOB",
        "2023-09-28",
        "2025-06-15",
        "PCAOB Auditing Standards",
        PCAOB_HUB,
        "Modernized PCAOB confirmation standard (effective FY ending on or after June 15, 2025) mandating confirmation of cash and accounts receivable, strengthening electronic confirmation controls, and prohibiting negative confirmations as sole substantive evidence.",
        "AS 2310.01–.31",
        "Mandatory Cash & A/R Confirmation & Electronic Intermediary Controls",
        "• Mandatory Cash & A/R Confirmation (AS 2310.24): Explicitly requires confirming cash and cash equivalents held by third parties AND accounts receivable (unless alternative procedures provide at least as persuasive evidence for A/R).\n"
        "• Electronic Confirmation & Intermediaries: Auditor must maintain direct control over selection, sending, and receipt; evaluate reliability of third-party electronic confirmation platforms.\n"
        "• Negative Confirmations: Strictly prohibited as the sole substantive audit procedure.",
        "• Goes further than ISA 505 by making third-party cash confirmation an explicit presumptive requirement and addressing modern electronic confirmation intermediaries.",
        [("ISA 505", "PCAOB AS 2310 (2025生效新版) 与 ISA 505 外部函证对照")],
        [("中国注册会计师审计准则第1312号——函证", "PCAOB AS 2310 与 CSA 1312 函证准则对照")],
        ["PCAOB AS 1105", "PCAOB AS 2301"],
    ),
    (
        "PCAOB AS 2401",
        "audit",
        "standard",
        "PCAOB AS 2401 Consideration of Fraud in a Financial Statement Audit",
        "PCAOB AS 2401 — Consideration of Fraud",
        "PCAOB",
        "2002-10-01",
        "2002-12-15",
        "PCAOB Auditing Standards",
        PCAOB_HUB,
        "Addresses the auditor's responsibility to plan and perform the audit to obtain reasonable assurance about whether the financial statements are free of material misstatement caused by fraudulent financial reporting or misappropriation of assets.",
        "AS 2401.52–.67",
        "Management Override of Controls, Journal Entry Testing & Estimates",
        "• Mandatory Procedures for Management Override (AS 2401.57–.67):\n"
        "  1. Examine journal entries and other adjustments for evidence of possible material misstatement due to fraud.\n"
        "  2. Review accounting estimates for management bias (including retrospective review of prior-year estimates).\n"
        "  3. Evaluate the business purpose (or lack thereof) for significant unusual transactions.\n"
        "• Unpredictability: Incorporate an element of unpredictability in selecting audit procedures.",
        "• Closely aligned with ISA 240 (Revised) and China's CSA 1141 on the three mandatory management-override procedures.",
        [("ISA 240 (Revised)", "PCAOB AS 2401 与 ISA 240 舞弊审计对照")],
        [("中国注册会计师审计准则第1141号——财务报表审计中与舞弊相关的责任", "PCAOB AS 2401 与 CSA 1141 舞弊审计对照")],
        ["PCAOB AS 2110", "PCAOB AS 2501"],
    ),
    (
        "PCAOB AS 2501",
        "audit",
        "standard",
        "PCAOB AS 2501 Auditing Accounting Estimates, Including Fair Value Measurements",
        "PCAOB AS 2501 — Auditing Accounting Estimates & Fair Value",
        "PCAOB",
        "2018-12-20",
        "2020-12-15",
        "PCAOB Auditing Standards",
        PCAOB_HUB,
        "Unified risk-based standard replacing legacy estimates/fair value/derivatives standards, requiring auditors to test management's process, develop an independent expectation, or review subsequent events, with heightened scrutiny of third-party pricing sources.",
        "AS 2501.07–.30",
        "Three Substantive Approaches, Management Bias & Pricing Services",
        "• Three Testing Approaches (AS 2501.07): (1) Test the company's process (methods, data, significant assumptions); (2) Develop an independent expectation; (3) Evaluate audit evidence from events/transactions occurring after the measurement date.\n"
        "• Third-Party Pricing Sources (Appendix A): Specific reliability procedures for pricing services and broker quotes used in ASC 820 fair value measurements.",
        "• Converged in risk-based philosophy with ISA 540 (Revised) and China's CSA 1321.",
        [("ISA 540 (Revised)", "PCAOB AS 2501 与 ISA 540 会计估计审计对照")],
        [("中国注册会计师审计准则第1321号——会计估计和相关披露的审计", "PCAOB AS 2501 与 CSA 1321 会计估计审计对照")],
        ["PCAOB AS 2110", "ASC 820", "ASC 326"],
    ),
    (
        "PCAOB AS 3101",
        "audit",
        "standard",
        "PCAOB AS 3101 The Auditor's Report on an Audit of Financial Statements When the Auditor Expresses an Unqualified Opinion",
        "PCAOB AS 3101 — Auditor's Report & Critical Audit Matters (CAMs)",
        "PCAOB",
        "2017-06-01",
        "2019-06-30",
        "PCAOB Auditing Standards",
        PCAOB_HUB,
        "Overhauled the US public company audit report to place the Opinion first, disclose auditor tenure (year firm began serving consecutively), and communicate Critical Audit Matters (CAMs).",
        "AS 3101.11–.17",
        "Opinion-First Format, Auditor Tenure & Critical Audit Matters (CAMs)",
        "• Critical Audit Matter — CAM (AS 3101.11): Any matter arising from the audit that was communicated (or required to be communicated) to the audit committee AND (1) relates to accounts or disclosures that are material to the financial statements AND (2) involved especially challenging, subjective, or complex auditor judgment.\n"
        "• Required CAM Elements: Identify the CAM, describe the principal considerations, describe how the CAM was addressed in the audit, and refer to the relevant financial statement accounts/disclosures.\n"
        "• Auditor Tenure: Must state the year the firm began serving consecutively as the company's auditor.",
        "• CAMs (AS 3101) vs. KAMs (ISA 701): CAMs explicitly require materiality to the financial statements AND 'especially challenging, subjective, or complex auditor judgment', and apply to SEC issuers (excluding Emerging Growth Companies — EGCs); KAMs focus on matters of 'most significance in the audit' and apply to all listed entities under ISAs.",
        [("ISA 700 (Revised)", "PCAOB AS 3101 与 ISA 700 审计报告格式对照"), ("ISA 701", "PCAOB AS 3101 CAM 关键审计事项与 ISA 701 KAM 差异对照")],
        [("中国注册会计师审计准则第1504号——在审计报告中沟通关键审计事项", "PCAOB AS 3101 CAM 与 CSA 1504 关键审计事项对照")],
        ["PCAOB AS 1301", "PCAOB AS 2201"],
    ),
    (
        "AICPA AU-C Standards",
        "audit",
        "standard",
        "AICPA Statements on Auditing Standards (AU-C Sections — US GAAS for Non-Issuers)",
        "AICPA US GAAS (AU-C Sections — Private Entities)",
        "AICPA Auditing Standards Board (ASB)",
        "2023-05-01",
        "2025-12-15",
        "AICPA Professional Standards",
        "https://www.aicpa-cima.com/",
        "Governs audits of non-issuers (private companies, nonprofits, and certain employee benefit plans) in the United States, structured via AU-C section numbers largely converged with IAASB ISAs (including SQMS 1–2 and SAS 145–149).",
        "AU-C 200–940",
        "Clarity Convergence with ISAs & Private Company Scope",
        "• Scope Split in the US: SEC public issuers & broker-dealers MUST be audited under PCAOB Standards (AS 1000–6100); private companies and non-issuers are audited under AICPA US GAAS (AU-C sections).\n"
        "• High Convergence with ISAs: AU-C numbering mirrors ISA numbering (e.g., AU-C 315 ≈ ISA 315, AU-C 540 ≈ ISA 540, SQMS 1 ≈ ISQM 1, SAS 149 Group Audits ≈ ISA 600 Revised).\n"
        "• Key Audit Matters (AU-C 701): Optional for non-issuers (communicated only when engaged to do so).",
        "• Dual US Audit Regime: Unlike most countries with one unified ISA-based framework, US practice splits between PCAOB (public issuers) and AICPA AU-C (private entities).",
        [("ISA 200", "AICPA AU-C 体系与 IAASB ISA 高度趋同对照"), ("ISQM 1", "AICPA SQMS 1 与 ISQM 1 对照")],
        [("中国注册会计师审计准则第1101号——注册会计师的总体目标和审计工作的基本要求", "AICPA US GAAS 与我国审计准则体系对照")],
        ["PCAOB AS 1000"],
    ),
    # ==================== US FEDERAL TAX (IRC) ====================
    (
        "IRC §11 & §55 (CAMT)",
        "tax",
        "law",
        "Internal Revenue Code §11 & §55 — US Federal Corporate Income Tax & 15% Corporate AMT (CAMT)",
        "IRC §11 & §55 — Corporate Income Tax (21%) & CAMT (15%)",
        "US Congress (Title 26, U.S. Code)",
        "2022-08-16",
        "2023-01-01",
        "Office of the Law Revision Counsel (U.S. Code)",
        US_CODE_T26,
        "Establishes the 21% flat US federal corporate income tax rate (enacted by TCJA 2017) alongside the 15% Corporate Alternative Minimum Tax (CAMT, enacted by IRA 2022) on Adjusted Financial Statement Income (AFSI) for corporations averaging >$1 billion in AFSI.",
        "IRC §11 / §55 / §56A",
        "21% Flat Corporate Rate, 15% Book-Income CAMT & NOL Rules",
        "• Regular Corporate Tax (IRC §11): Flat 21% federal rate on taxable income of C corporations (plus state/local corporate income taxes, which are deductible federally).\n"
        "• Corporate AMT — CAMT (IRC §55 / §56A, effective FY2023+): 15% minimum tax on Adjusted Financial Statement Income (AFSI) for Applicable Corporations exceeding $1B 3-year average AFSI ($100M US threshold for foreign-parented multinational groups).\n"
        "• Net Operating Losses (IRC §172): Post-2017 NOLs carry forward INDEFINITELY, subject to an 80% taxable income offset cap (no carryback).",
        "• Interaction with ASC 740 & OECD Pillar Two: Both CAMT (IRC §55) and OECD GloBE Pillar Two are 15% book-income minimum taxes, yet CAMT is NOT a Qualified Domestic Minimum Top-up Tax (QDMTT) under Pillar Two due to US tax credit and depreciation adjustments; FASB treats CAMT as a regular AMT (no deferred tax remeasurement).",
        [("OECD Pillar Two (GloBE)", "美国 15% CAMT 账面最低税与 OECD 支柱二 GloBE 15% 规则差异衔接")],
        [("中华人民共和国企业所得税法（2018年第二次修正）", "美国 IRC §11 21%公司所得税与我国 25% 企业所得税法对照")],
        ["ASC 740", "IRC §163(j)", "IRC §951 / §951A"],
    ),
    (
        "IRC §163(j)",
        "tax",
        "law",
        "Internal Revenue Code §163(j) — Limitation on Business Interest Expense Deduction",
        "IRC §163(j) — Business Interest Limitation (30% ATI)",
        "US Congress (Title 26, U.S. Code)",
        "2017-12-22",
        "2018-01-01",
        "Office of the Law Revision Counsel (U.S. Code)",
        US_CODE_T26,
        "Limits annual deductible business interest expense to business interest income plus 30% of Adjusted Taxable Income (ATI), with disallowed interest carried forward indefinitely.",
        "IRC §163(j)",
        "30% ATI Cap, Carryforward & Small Business Exemption",
        "• General Limit: Deductible business interest capped at (1) Business Interest Income + (2) 30% of Adjusted Taxable Income (ATI) + (3) Floor plan financing interest.\n"
        "• ATI Base: Shifted from EBITDA-like base (2018–2021) to EBIT-like base (starting 2022, after depreciation & amortization), subject to ongoing US statutory modifications.\n"
        "• Indefinite Carryforward: Disallowed interest carries forward indefinitely (creating a Deferred Tax Asset evaluated for valuation allowance under ASC 740).",
        "• Comparable to OECD BEPS Action 4 (30% EBITDA interest barrier) and China's thin-capitalization debt-to-equity ratio rule (2:1 / 5:1 under Enterprise Income Tax Law Art. 46).",
        [("OECD Transfer Pricing Guidelines", "IRC §163(j) 利息扣除限制与 OECD BEPS 税基侵蚀规则衔接")],
        [("中华人民共和国企业所得税法（2018年第二次修正）", "IRC §163(j) 与我国企业所得税资本弱化/利息扣除限制对照")],
        ["IRC §11 & §55 (CAMT)", "ASC 740"],
    ),
    (
        "IRC §482",
        "tax",
        "law",
        "Internal Revenue Code §482 — Allocation of Income and Deductions Among Taxpayers (US Transfer Pricing)",
        "IRC §482 — US Transfer Pricing (Arm's Length Standard)",
        "US Congress & IRS (26 CFR §1.482)",
        "1986-10-22",
        "1994-07-08",
        "Office of the Law Revision Counsel (U.S. Code)",
        US_CODE_T26,
        "Authorizes the IRS to reallocate gross income, deductions, credits, or allowances between commonly controlled entities to prevent tax evasion or clearly reflect income, anchored in the Arm's Length Standard and Best Method Rule.",
        "IRC §482 / Reg. §1.482",
        "Best Method Rule, Commensurate-with-Income & Cost Sharing",
        "• Best Method Rule (Treas. Reg. §1.482-1(c)): Select the transfer pricing method (CUP, Resale Price, Cost Plus, CPM, Profit Split) providing the most reliable measure of an arm's length result.\n"
        "• Commensurate with Income (CWI) Standard: For transfers/licenses of intangible property, income must be 'commensurate with the income attributable to the intangible' (allowing periodic IRS adjustments).\n"
        "• Penalties & Documentation (IRC §6662(e)): Contemporaneous transfer pricing documentation required to avoid 20%/40% valuation misstatement penalties; Advance Pricing Agreements (APAs) available.",
        "• Broadly aligned with the OECD Transfer Pricing Guidelines (CPM ≈ TNMM), though US Reg. §1.482-7 Cost Sharing Arrangements (CSAs) and the statutory 'commensurate with income' rule have distinct US litigation history.",
        [("OECD Transfer Pricing Guidelines", "美国 IRC §482 与 OECD 转让定价指南直接对照")],
        [("中华人民共和国企业所得税法（2018年第二次修正）", "美国 IRC §482 与我国特别纳税调整/独立交易原则对照")],
        ["IRC §951 / §951A", "US Model Tax Treaty"],
    ),
    (
        "IRC §951 / §951A",
        "tax",
        "law",
        "Internal Revenue Code §951 & §951A — Controlled Foreign Corporations (Subpart F & GILTI)",
        "IRC §951 / §951A — CFC Rules: Subpart F & GILTI",
        "US Congress (Title 26, U.S. Code)",
        "2017-12-22",
        "2018-01-01",
        "Office of the Law Revision Counsel (U.S. Code)",
        US_CODE_T26,
        "Governs current US taxation of US shareholders (>=10% vote or value) owning >50% of Controlled Foreign Corporations (CFCs), covering passive/mobile Subpart F income (§951) and Global Intangible Low-Taxed Income — GILTI (§951A).",
        "IRC §951 / §951A / §250",
        "CFC Ownership Test, Subpart F Income & GILTI Minimum Tax",
        "• CFC Definition (IRC §957): Foreign corporation >50% owned (vote or value) by 'US Shareholders' (each owning >=10% vote or value).\n"
        "• Subpart F (§951–§964): Immediate US inclusion of passive Foreign Personal Holding Company Income (dividends, interest, royalties) and certain base-company sales/services income.\n"
        "• GILTI (§951A): Current inclusion of CFC tested income exceeding a 10% routine return on Qualified Business Asset Investment (QBAI), partially offset by the §250 deduction and deemed-paid Foreign Tax Credits (80% haircut, separate basket, no carryforward).",
        "• GILTI vs. OECD Pillar Two: GILTI aggregates CFC income globally ('global blending'), whereas OECD Pillar Two GloBE computes the 15% minimum tax jurisdiction-by-jurisdiction (making GILTI a 'blended CFC tax regime' requiring special Pillar Two allocation).",
        [("OECD Pillar Two (GloBE)", "美国 GILTI 全球混合最低税与 OECD 支柱二按国别计算衔接对照")],
        [("中华人民共和国企业所得税法（2018年第二次修正）", "美国 CFC/Subpart F 与我国企业所得税法第45条受控外国企业规则对照")],
        ["IRC §11 & §55 (CAMT)", "IRC §482", "IRC §59A (BEAT)", "ASC 740"],
    ),
    (
        "IRC §59A (BEAT)",
        "tax",
        "law",
        "Internal Revenue Code §59A — Base Erosion and Anti-Abuse Tax (BEAT)",
        "IRC §59A — Base Erosion and Anti-Abuse Tax (BEAT)",
        "US Congress (Title 26, U.S. Code)",
        "2017-12-22",
        "2018-01-01",
        "Office of the Law Revision Counsel (U.S. Code)",
        US_CODE_T26,
        "Minimum tax targeting large multinational corporations ($500M+ 3-year average US gross receipts and >=3% base erosion percentage) that strip US taxable income via deductible payments (royalties, interest, services) to foreign related parties.",
        "IRC §59A",
        "$500M Receipts Test, 3% Base Erosion Threshold & Modified Taxable Income",
        "• Applicable Taxpayer Test: (1) C corporation (not RIC/REIT/S corp); (2) 3-year average US effectively connected gross receipts >= $500M; (3) Base Erosion Percentage >= 3% (2% for banks/securities dealers).\n"
        "• Base Erosion Payments: Deductible payments to foreign related parties (interest, royalties, management/R&D fees) — generally EXCLUDING Cost of Goods Sold (COGS) and Services Cost Method (SCM) at-cost charges.\n"
        "• Computation: Excess of BEAT rate (10%, rising under scheduled statutory step-up) × Modified Taxable Income over regular tax liability reduced by certain credits.",
        "• Operates alongside OECD Pillar Two UTPR as a defensive US inbound base-erosion backstop; accounted for as a period cost under ASC 740 (no deferred tax remeasurement).",
        [("OECD Pillar Two (GloBE)", "美国 BEAT 反税基侵蚀税与 OECD 支柱二 UTPR 机制对比")],
        [],
        ["IRC §11 & §55 (CAMT)", "IRC §951 / §951A", "ASC 740"],
    ),
    (
        "US Model Tax Treaty",
        "tax",
        "standard",
        "United States Model Income Tax Convention (US Treasury Model Treaty)",
        "US Model Income Tax Convention (Treaties & LOB)",
        "US Department of the Treasury",
        "2016-02-17",
        "2016-02-17",
        "US Department of the Treasury",
        TREASURY_TREATY,
        "Baseline template used by the US Treasury when negotiating bilateral income tax treaties, featuring the signature US 'Saving Clause', strict Limitation on Benefits (LOB) anti-treaty-shopping rules, and Special Tax Regime (STR) exclusions.",
        "Art. 1, 5, 10–12, 22 (LOB)",
        "Saving Clause, Withholding Rates & Limitation on Benefits (LOB)",
        "• Saving Clause (Art. 1(4)): Preserves the US right to tax its own citizens and residents as if the treaty had not come into effect.\n"
        "• Limitation on Benefits — LOB (Art. 22): Objective tests (publicly traded, active trade or business, ownership/base-erosion, derivative benefits) preventing third-country treaty shopping.\n"
        "• Withholding Rates (Art. 10–12): Generally 5% (direct >=10% corporate) / 15% portfolio dividends, 0% interest, 0% royalties (subject to STR/expatriated entity exceptions).",
        "• Diverges from the OECD Model Tax Convention primarily through its strict objective LOB article (vs. OECD Principal Purpose Test — PPT) and citizenship-based Saving Clause.",
        [("OECD Model Tax Convention", "美国税收协定范本(LOB条款)与 OECD 范本(PPT条款)对照")],
        [],
        ["IRC §482", "IRC §951 / §951A"],
    ),
    # ==================== US SECURITIES, SOX & GOVERNANCE ====================
    (
        "SOX (2002)",
        "general",
        "law",
        "Sarbanes-Oxley Act of 2002 (Public Company Accounting Reform and Investor Protection Act)",
        "Sarbanes-Oxley Act of 2002 (SOX — Sec. 302 / 404 / 906)",
        "US Congress (Pub. L. 107-204)",
        "2002-07-30",
        "2002-07-30",
        "SEC / U.S. Congress",
        SEC_ICFR_URL,
        "Landmark US federal legislation enacted following Enron/WorldCom that created the PCAOB, mandated CEO/CFO financial certifications (Sec. 302/906), established management and auditor ICFR attestation (Sec. 404), strengthened audit committee independence, and restricted auditor non-audit services.",
        "SOX Sec. 101, 201, 302, 404, 802, 906",
        "PCAOB Oversight, CEO/CFO Certifications, ICFR (404) & Penalties",
        "• Title I (Sec. 101–109): Established the PCAOB to inspect, regulate, and set auditing standards for public company auditors.\n"
        "• Title II (Sec. 201–209): Prohibits 9 categories of non-audit services for audit clients, mandates audit committee pre-approval, and requires 5-year lead/concurring audit partner rotation.\n"
        "• Section 302 & 906: Personal civil and criminal certifications by CEO and CFO on 10-K/10-Q/20-F accuracy and disclosure controls (up to $5M fine / 20 years imprisonment for willful false certification).\n"
        "• Section 404(a) & 404(b): Sec. 404(a) requires annual management assessment of ICFR; Sec. 404(b) requires independent auditor attestation under PCAOB AS 2201 (exempting non-accelerated filers and EGCs).\n"
        "• Section 301 & 806: Fully independent audit committees and whistleblower anti-retaliation protections.",
        "• Global Ripple Effect: SOX 404 catalyzed China's《企业内部控制基本规范》&《企业内部控制审计指引》(C-SOX) and Japan's J-SOX, making COSO ICIF the de facto global ICFR benchmark.",
        [("COSO Internal Control (ICIF)", "SOX 404 内部控制评估事实标准直接采用 COSO ICIF"), ("G20/OECD Corporate Governance", "SOX 审计委员会独立性与 G20/OECD 公司治理原则对照")],
        [("企业内部控制基本规范（财会〔2008〕7号）", "SOX 404 与我国 C-SOX（企业内部控制基本规范）直接对照"), ("中华人民共和国证券法（2019年第二次修订）", "SOX 与我国证券法董监高保证与信息披露责任对照")],
        ["PCAOB AS 2201", "PCAOB AS 1000", "SEC Regulation S-X", "Securities Acts (1933 / 1934)"],
    ),
    (
        "Securities Acts (1933 / 1934)",
        "general",
        "law",
        "US Securities Act of 1933 & Securities Exchange Act of 1934 (US Capital Markets Framework)",
        "US Securities Act (1933) & Exchange Act (1934)",
        "US Congress / SEC",
        "1934-06-06",
        "1934-07-01",
        "U.S. Securities and Exchange Commission (SEC)",
        SEC_ICFR_URL,
        "The twin statutory pillars of US federal securities regulation: the 1933 Act governs primary public offerings (IPOs — Forms S-1 / F-1, Section 11 strict liability), while the 1934 Act created the SEC and governs ongoing periodic reporting (Forms 10-K, 10-Q, 8-K, 20-F, 6-K) and Rule 10b-5 anti-fraud enforcement.",
        "1933 Act & 1934 Act (10-K / 20-F / 10b-5)",
        "IPO Registration, Foreign Private Issuers (20-F) & Rule 10b-5",
        "• Securities Act of 1933 (Primary Offerings): Requires registration statement (Form S-1 for domestic, Form F-1 for Foreign Private Issuers — FPIs) before public sale unless exempt (e.g., Reg D, Rule 144A); Section 11 imposes strict/negligence liability for material misstatements.\n"
        "• Securities Exchange Act of 1934 (Ongoing Reporting): Periodic filings — Form 10-K (annual, 60/75/90 days), Form 10-Q (quarterly), Form 8-K (current events within 4 business days); FPIs file annual Form 20-F (within 4 months, permitting US GAAP OR IASB IFRS without reconciliation!) and Form 6-K.\n"
        "• Section 10(b) & Rule 10b-5: Core anti-fraud & insider trading prohibition.",
        "• Critical for Cross-Border Issuers: Since 2007, Foreign Private Issuers (including US-listed Chinese/European companies) may file Form 20-F using IFRS as issued by the IASB without US GAAP reconciliation, while still complying with SOX 302/404 and PCAOB audit standards.",
        [("G20/OECD Corporate Governance", "美国1933/1934证券法披露制度与 G20/OECD 信息披露原则对照")],
        [("中华人民共和国证券法（2019年第二次修订）", "美国1933/1934证券法与我国《证券法》注册制及定期报告对照")],
        ["SOX (2002)", "SEC Regulation S-X", "SEC Regulation S-K", "FCPA (1977)"],
    ),
    (
        "SEC Regulation S-X",
        "general",
        "regulation",
        "SEC Regulation S-X — Form and Content of Financial Statements (17 CFR Part 210)",
        "SEC Regulation S-X (Financial Statement Rules & Independence)",
        "U.S. Securities and Exchange Commission (SEC)",
        "2020-05-20",
        "2021-01-01",
        "SEC / eCFR (17 CFR Part 210)",
        SEC_ICFR_URL,
        "Prescribes the form, content, age, and audit requirements of financial statements filed with the SEC, including Rule 2-01 (Auditor Independence), Rule 3-05 (Significant Acquired Businesses), Rule 3-09 (Significant Equity Investees), and Article 11 (Pro Forma Financial Information).",
        "Reg. S-X Art. 2, 3, 5, 10, 11",
        "Auditor Independence (2-01), Significant Acquisitions (3-05) & Pro Forma",
        "• Rule 2-01 (Auditor Independence): General standard ('reasonable investor' test) + strict rules on financial/employment/business relationships, prohibited non-audit services, and 5-year partner rotation.\n"
        "• Rule 3-05 & Rule 1-02(w) (Significant Acquisitions): Requires 1 or 2 years of audited financial statements for acquired businesses exceeding 20%/40% significance tests (Investment, Asset, Income/Revenue).\n"
        "• Article 5 (Commercial & Industrial Companies) & Article 10 (Interim 10-Q): Prescribes specific income statement/balance sheet captions.\n"
        "• Article 11 (Pro Forma): Transaction accounting adjustments for significant business acquisitions/dispositions.",
        "• Bridges FASB ASC and SEC filings: Even when a company follows US GAAP (or IASB IFRS on Form 20-F), SEC Regulation S-X dictates financial statement age, significant acquiree financials, and auditor independence.",
        [("IESBA Code Part 4A", "SEC Rule 2-01 独立性规则与 IESBA Part 4A 审计独立性对照")],
        [("中华人民共和国证券法（2019年第二次修订）", "SEC Reg S-X 财报编报规则与我国证监会信息披露编报规则对照")],
        ["Securities Acts (1933 / 1934)", "SOX (2002)", "ASC 205", "ASC 805"],
    ),
    (
        "SEC Regulation S-K",
        "general",
        "regulation",
        "SEC Regulation S-K — Integrated Disclosure Requirements for Non-Financial Information (17 CFR Part 229)",
        "SEC Regulation S-K (MD&A, Risk Factors & Non-GAAP)",
        "U.S. Securities and Exchange Commission (SEC)",
        "2023-07-26",
        "2023-12-18",
        "SEC / eCFR (17 CFR Part 229)",
        SEC_ICFR_URL,
        "Governs qualitative and non-financial disclosures in SEC registration statements and periodic reports, including Business (Item 101), Risk Factors (Item 105), Cybersecurity (Item 106), MD&A (Item 303), Executive Compensation (Item 402), and Non-GAAP Measures (Item 10(e)).",
        "Reg. S-K Item 10(e), 105, 106, 303, 402",
        "MD&A (Item 303), Non-GAAP Rules (Item 10(e)) & Cybersecurity (106)",
        "• Item 10(e) & Reg G (Non-GAAP Measures): Requires equal or greater prominence for the most directly comparable GAAP measure, quantitative reconciliation, and prohibition of misleading adjustments.\n"
        "• Item 303 (MD&A): Liquidity, capital resources, results of operations, known trends/uncertainties, and Critical Accounting Estimates.\n"
        "• Item 106 (Cybersecurity, effective Dec 2023): Annual disclosures of cybersecurity risk management, strategy, and board governance (paired with 4-business-day Form 8-K Item 1.05 material incident reporting).\n"
        "• Item 105 (Risk Factors) & Item 402 (Executive Compensation & Clawbacks).",
        "• Item 303 MD&A parallels IFRS Practice Statement 1 (Management Commentary), while Item 10(e) Non-GAAP rules parallel IFRS 18's new Management-Defined Performance Measures (MPMs).",
        [("Practice Statement 1", "SEC Reg S-K Item 303 MD&A 与 IFRS 管理层评论实务公告对照"), ("IFRS 18", "SEC Item 10(e) Non-GAAP 规则与 IFRS 18 MPM 披露对照")],
        [("中华人民共和国证券法（2019年第二次修订）", "SEC Reg S-K 非财务信息披露与我国年报信息披露规则对照")],
        ["Securities Acts (1933 / 1934)", "SEC Regulation S-X", "ASC 220"],
    ),
    (
        "FCPA (1977)",
        "general",
        "law",
        "U.S. Foreign Corrupt Practices Act of 1977 (FCPA — Anti-Bribery & Books-and-Records Provisions)",
        "FCPA (1977) — Anti-Bribery & Internal Accounting Controls",
        "US Congress / DOJ & SEC",
        "1977-12-19",
        "1977-12-19",
        "SEC & DOJ FCPA Resource Guide",
        FCPA_GUIDE_URL,
        "Enacted to halt bribery of foreign government officials and off-the-books slush funds; jointly enforced by the DOJ (criminal) and SEC (civil) across two pillars: Anti-Bribery provisions (broad extraterritorial reach) and Accounting provisions (accurate books/records & internal accounting controls for all SEC issuers).",
        "15 U.S.C. §78dd-1 / §78m(b)(2)",
        "Anti-Bribery Prohibitions & Books-and-Records Accounting Provisions",
        "• Anti-Bribery Provisions: Prohibits issuers, US domestic concerns, and foreign persons acting in US territory from corruptly offering/paying anything of value to a foreign official (including employees of state-owned enterprises) to obtain or retain business.\n"
        "• Accounting Provisions (Exchange Act §13(b)(2)): Requires ALL SEC issuers (including Foreign Private Issuers) to (a) make and keep books, records, and accounts in reasonable detail accurately reflecting transactions and dispositions of assets, and (b) devise and maintain a system of internal accounting controls.\n"
        "• No Materiality Threshold: Unlike financial statement fraud, FCPA books-and-records violations have NO financial statement materiality threshold.",
        "• Directly reinforces COSO Internal Control, FATF anti-corruption/AML standards, and OECD MNE Guidelines Chapter VII (Combating Bribery), with major compliance impact on multinational subsidiaries and US-listed foreign issuers.",
        [("FATF 40 Recommendations", "美国 FCPA 反贿赂/账簿内控与 FATF 反洗钱及腐败收益防范衔接"), ("OECD MNE Guidelines (RBC)", "美国 FCPA 与 OECD 跨国企业指南第七章反贿赂对照"), ("COSO Internal Control (ICIF)", "FCPA 内部会计控制条款与 COSO 内控框架衔接")],
        [("中华人民共和国公司法（2023年第二次修订）", "FCPA 账簿记录与内部会计控制要求与公司治理合规对照")],
        ["Securities Acts (1933 / 1934)", "SOX (2002)", "PCAOB AS 2401"],
    ),
]


def build_docs() -> list[dict]:
    docs: list[dict] = []
    for (
        code,
        domain,
        doc_type,
        title,
        display_title,
        issuer,
        pub_date,
        eff_date,
        src_name,
        src_url,
        summary,
        core_no,
        core_heading,
        core_text,
        diff_text,
        ifrs_links,
        cas_links,
        us_cites,
    ) in SPECS:
        articles = [
            {
                "no": "Overview",
                "heading": "Scope & Statutory / Regulatory Role (Public Summary)",
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
                "no": "Cross-Framework Comparison",
                "heading": "US vs. International (ISA/OECD/COSO) & China Context",
                "text": diff_text,
                "seq": 2,
            },
            {
                "no": "Official Access",
                "heading": "Official Regulatory / Statutory Source",
                "text": f"Official Source ({src_name}): {src_url}\nStatus: in_force.",
                "seq": 3,
            },
        ]
        docs.append(
            {
                "code": code,
                "framework": "US",
                "domain": domain,
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
                "source_kind": "official",
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
        "source": "PCAOB / AICPA / IRC (Title 26) / SEC / SOX / FCPA Official Public Standards",
        "count": len(docs),
        "documents": docs,
    }
    OUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(docs)} US audit/tax/governance documents -> {OUT_PATH.relative_to(PROJECT_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
