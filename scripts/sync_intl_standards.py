#!/usr/bin/env python3
"""
国际准则扩展板块（ISSB 可持续披露 / IAASB 国际审计与鉴证 / IESBA 职业道德守则 / OECD 国际税收）
公开合规卡片生成器（零第三方依赖，需 Python 3.9+）。

说明：
- 严格遵循公开合规边界，仅收录官网公开目录、核心范围概述、生效状态与官方入口链接，不搬运付费全文；
- 所有标准先建立完整卡片与中外对照映射，细则待后续按需补厚；
- 输出至 intl_data/{issb_sustainability,iaasb_auditing,iesba_ethics,oecd_tax}.json，
  由 scripts/build_prototype.py 自动合并构建并接入前端全站。
"""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
INTL_DATA_DIR = PROJECT_ROOT / "intl_data"


def make_doc(
    *,
    code: str,
    title: str,
    display_title: str,
    domain: str,
    doc_type: str,
    issuer: str,
    source_name: str,
    source_url: str,
    summary: str,
    pub_date: str = "2026-09-30",
    effective_date: str = "2026-01-01",
    status: str = "in_force",
    version_level: str = "",
    version_note: str = "",
    scope_note: str = "",
    cited_codes: list[str] | None = None,
    cas_links: list[list[str]] | None = None,
) -> dict:
    articles = [
        {
            "no": "Overview",
            "heading": "Scope & Key Requirements (Public Summary)",
            "text": summary,
            "seq": 0,
        },
        {
            "no": "Official Access",
            "heading": "Official Handbook & Reference Entry",
            "text": (
                f"{scope_note}\n" if scope_note else ""
            ) + f"Official source ({source_name}): {source_url}\nStatus: {status}. Detailed paragraph-level summaries and practice notes can be expanded incrementally.",
            "seq": 1,
        },
    ]
    return {
        "code": code,
        "framework": "INTL",
        "domain": domain,
        "doc_type": doc_type,
        "title": title,
        "display_title": display_title,
        "series_badge": code,
        "doc_no": code,
        "issuer": issuer,
        "pub_date": pub_date,
        "effective_date": effective_date,
        "status": status,
        "version_level": version_level,
        "version_note": version_note,
        "source_name": source_name,
        "source_url": source_url,
        "source_kind": "official",
        "summary": summary,
        "cited_codes": cited_codes or [],
        "cas_links": cas_links or [],
        "articles": articles,
    }


def build_issb() -> list[dict]:
    issb_hub = "https://www.ifrs.org/sustainability/knowledge-hub/introduction-to-issb-and-ifrs-sustainability-disclosure-standards/"
    return [
        make_doc(
            code="IFRS S1",
            title="IFRS S1 General Requirements for Disclosure of Sustainability-related Financial Information",
            display_title="General Requirements for Disclosure of Sustainability-related Financial Information",
            domain="accounting",
            doc_type="standard",
            issuer="ISSB (IFRS Foundation)",
            source_name="IFRS Foundation (ISSB)",
            source_url="https://www.ifrs.org/issued-standards/ifrs-sustainability-standards-navigator/ifrs-s1-general-requirements/",
            summary="Sets out overarching requirements for an entity to disclose material information about sustainability-related risks and opportunities useful to primary users of general purpose financial reports, structured around governance, strategy, risk management, and metrics & targets.",
            pub_date="2023-06-26",
            effective_date="2024-01-01",
            status="in_force",
            cited_codes=["IFRS S2", "SASB Standards", "Integrated Reporting Framework", "Conceptual Framework", "IFRS 18"],
            cas_links=[["企业可持续披露准则——基本准则（试行）", "ISSB 一般要求与我国企业可持续披露基本准则直接对照"]],
        ),
        make_doc(
            code="IFRS S2",
            title="IFRS S2 Climate-related Disclosures",
            display_title="Climate-related Disclosures",
            domain="accounting",
            doc_type="standard",
            issuer="ISSB (IFRS Foundation)",
            source_name="IFRS Foundation (ISSB)",
            source_url="https://www.ifrs.org/issued-standards/ifrs-sustainability-standards-navigator/ifrs-s2-climate-related-disclosures/",
            summary="Sets out specific climate-related disclosure requirements (physical and transition risks, Scope 1–3 GHG emissions, scenario analysis, and industry-based metrics) designed to be applied together with IFRS S1. Targeted amendments issued Dec 2025 take effect 1 Jan 2027.",
            pub_date="2023-06-26",
            effective_date="2024-01-01",
            status="in_force",
            version_level="info",
            version_note="In force from 1 Jan 2024; targeted amendments issued Dec 2025 effective 1 Jan 2027.",
            cited_codes=["IFRS S1", "IFRS S2 Industry Guidance", "ISSA 5000"],
            cas_links=[["企业可持续披露准则第1号——气候（试行）", "ISSB 气候披露准则与我国第1号气候准则直接对照"]],
        ),
        make_doc(
            code="IFRS S2 Industry Guidance",
            title="Industry-based Guidance on Implementing IFRS S2",
            display_title="Industry-based Guidance on Implementing IFRS S2",
            domain="accounting",
            doc_type="guidance",
            issuer="ISSB (IFRS Foundation)",
            source_name="IFRS Foundation (ISSB)",
            source_url=issb_hub,
            summary="Provides industry-specific climate disclosure topics and metrics derived from SASB Standards across 68 industries; IFRS S2 requires entities to refer to and consider this guidance when identifying climate risks and metrics.",
            pub_date="2023-06-26",
            effective_date="2024-01-01",
            status="in_force",
            cited_codes=["IFRS S2", "SASB Standards"],
            cas_links=[["企业可持续披露准则第1号——气候（试行）", "行业气候指标实施指引参考"]],
        ),
        make_doc(
            code="SASB Standards",
            title="SASB Standards (Sustainability Accounting Standards Board)",
            display_title="SASB Standards (Industry Sustainability Topics & Metrics)",
            domain="accounting",
            doc_type="guidance",
            issuer="ISSB (IFRS Foundation)",
            source_name="IFRS Foundation (ISSB)",
            source_url=issb_hub,
            summary="Industry-based sustainability disclosure standards maintained by the ISSB across 77 industries; referenced by IFRS S1 as a required source of guidance for identifying sustainability-related risks, opportunities, and metrics beyond climate.",
            pub_date="2023-12-01",
            effective_date="2024-01-01",
            status="in_force",
            cited_codes=["IFRS S1", "IFRS S2 Industry Guidance"],
        ),
        make_doc(
            code="Integrated Reporting Framework",
            title="Integrated Reporting Framework (<IR>)",
            display_title="Integrated Reporting Framework (<IR>)",
            domain="accounting",
            doc_type="guidance",
            issuer="IFRS Foundation (IASB & ISSB)",
            source_name="IFRS Foundation",
            source_url=issb_hub,
            summary="Principles-based framework jointly overseen by the IASB and ISSB to promote connected reporting between financial statements and sustainability-related financial disclosures.",
            pub_date="2022-08-01",
            effective_date="2022-08-01",
            status="in_force",
            cited_codes=["IFRS S1", "Practice Statement 1", "Conceptual Framework"],
        ),
    ]


def build_iaasb() -> list[dict]:
    hb_url = "https://www.iaasb.org/publications/2026-handbook-international-quality-management-auditing-review-sustainability-and-other-assurance"
    docs: list[dict] = []

    # 1. Assurance Framework & Quality Management (ISQM)
    docs.extend([
        make_doc(
            code="Assurance Framework",
            title="International Framework for Assurance Engagements",
            display_title="International Framework for Assurance Engagements",
            domain="audit",
            doc_type="standard",
            issuer="IAASB",
            source_name="IAASB 2026 Handbook",
            source_url=hb_url,
            summary="Defines and describes the elements and objectives of an assurance engagement (reasonable and limited assurance) and identifies engagements to which ISAs, ISREs, ISAEs, and ISSAs apply.",
            pub_date="2026-09-30",
            effective_date="2026-09-30",
            cas_links=[["中国注册会计师鉴证业务基本准则", "国际鉴证业务框架与我国鉴证业务基本准则直接对照"]],
        ),
        make_doc(
            code="ISQM 1",
            title="ISQM 1 Quality Management for Firms that Perform Audits or Reviews of Financial Statements, or Other Assurance or Related Services Engagements",
            display_title="Quality Management for Firms (ISQM 1)",
            domain="audit",
            doc_type="standard",
            issuer="IAASB",
            source_name="IAASB 2026 Handbook",
            source_url=hb_url,
            summary="Requires firms to design, implement, and operate a risk-based system of quality management (SOQM) covering governance, ethics, acceptance/continuance, engagement performance, resources, information/communication, and monitoring/remediation.",
            pub_date="2020-12-18",
            effective_date="2022-12-15",
            cited_codes=["ISQM 2", "ISA 220 (Revised)", "IESBA Code Part 1–3"],
            cas_links=[["发布通知——会计师事务所质量管理准则第5101号等三项", "ISQM 1 与我国质量管理准则第5101号直接对照"]],
        ),
        make_doc(
            code="ISQM 2",
            title="ISQM 2 Engagement Quality Reviews",
            display_title="Engagement Quality Reviews (ISQM 2)",
            domain="audit",
            doc_type="standard",
            issuer="IAASB",
            source_name="IAASB 2026 Handbook",
            source_url=hb_url,
            summary="Deals with the appointment and eligibility of the engagement quality reviewer (EQR) and the reviewer's responsibilities relating to the performance and documentation of an engagement quality review.",
            pub_date="2020-12-18",
            effective_date="2022-12-15",
            cited_codes=["ISQM 1", "ISA 220 (Revised)"],
            cas_links=[["发布通知——会计师事务所质量管理准则第5101号等三项", "ISQM 2 与我国项目质量复核准则第5102号直接对照"]],
        ),
    ])

    # 2. Full ISA 200-810 Suite (37 standards) + ISA for LCE
    isa_specs = [
        ("ISA 200", "Overall Objectives of the Independent Auditor and the Conduct of an Audit in Accordance with International Standards on Auditing", "Establishes the independent auditor's overall responsibilities when conducting an audit of financial statements in accordance with ISAs, including ethical requirements, professional skepticism, and professional judgment.", "中国注册会计师审计准则第1101号", "in_force", ""),
        ("ISA 210", "Agreeing the Terms of Audit Engagements", "Deals with the auditor's responsibilities in agreeing the terms of the audit engagement with management and, where appropriate, those charged with governance, including preconditions for an audit.", "中国注册会计师审计准则第1111号", "in_force", ""),
        ("ISA 220 (Revised)", "Quality Management for an Audit of Financial Statements", "Deals with the specific responsibilities of the auditor regarding quality management at the engagement level for an audit of financial statements, and the related responsibilities of the engagement partner.", "中国注册会计师审计准则第1121号", "in_force", ""),
        ("ISA 230", "Audit Documentation", "Deals with the auditor's responsibility to prepare audit documentation for an audit of financial statements sufficient to enable an experienced auditor to understand the nature, timing, extent, and results of audit procedures.", "中国注册会计师审计准则第1131号", "in_force", ""),
        ("ISA 240 (Revised)", "The Auditor's Responsibilities Relating to Fraud in an Audit of Financial Statements", "Deals with the auditor's responsibilities relating to fraud in an audit of financial statements, including reinforced professional skepticism, fraud risk identification, and transparent communication (Revised July 2025).", "中国注册会计师审计准则第1141号", "in_force", "Revised edition published July 2025 in IAASB 2026 Handbook."),
        ("ISA 250 (Revised)", "Consideration of Laws and Regulations in an Audit of Financial Statements", "Deals with the auditor's responsibility to consider laws and regulations in an audit of financial statements, including non-compliance with laws and regulations (NOCLAR).", "中国注册会计师审计准则第1142号", "in_force", ""),
        ("ISA 260 (Revised)", "Communication with Those Charged with Governance", "Deals with the auditor's responsibility to communicate with those charged with governance in an audit of financial statements regarding planned scope, timing, and significant audit findings.", "中国注册会计师审计准则第1151号", "in_force", ""),
        ("ISA 265", "Communicating Deficiencies in Internal Control to Those Charged with Governance and Management", "Deals with the auditor's responsibility to communicate appropriately to those charged with governance and management deficiencies in internal control identified in an audit.", "中国注册会计师审计准则第1152号", "in_force", ""),
        ("ISA 300", "Planning an Audit of Financial Statements", "Deals with the auditor's responsibility to plan an audit of financial statements, including establishing an overall audit strategy and developing an audit plan.", "中国注册会计师审计准则第1201号", "in_force", ""),
        ("ISA 315 (Revised 2019)", "Identifying and Assessing the Risks of Material Misstatement", "Deals with the auditor's responsibility to identify and assess the risks of material misstatement in the financial statements through understanding the entity, its environment, and its system of internal control.", "中国注册会计师审计准则第1211号", "in_force", ""),
        ("ISA 320", "Materiality in Planning and Performing an Audit", "Deals with the auditor's responsibility to apply the concept of materiality in planning and performing an audit of financial statements, including performance materiality.", "中国注册会计师审计准则第1221号", "in_force", ""),
        ("ISA 330", "The Auditor's Responses to Assessed Risks", "Deals with the auditor's responsibility to design and implement responses to the risks of material misstatement identified and assessed in accordance with ISA 315.", "中国注册会计师审计准则第1231号", "in_force", ""),
        ("ISA 402", "Audit Considerations Relating to an Entity Using a Service Organization", "Deals with the user auditor's responsibility to obtain sufficient appropriate audit evidence when a user entity uses the services of one or more service organizations.", "中国注册会计师审计准则第1241号", "in_force", ""),
        ("ISA 450", "Evaluation of Misstatements Identified during the Audit", "Deals with the auditor's responsibility to evaluate the effect of identified misstatements on the audit and of uncorrected misstatements, if any, on the financial statements.", "中国注册会计师审计准则第1251号", "in_force", ""),
        ("ISA 500", "Audit Evidence", "Explains what constitutes audit evidence in an audit of financial statements and deals with the auditor's responsibility to design and perform audit procedures to obtain sufficient appropriate audit evidence.", "中国注册会计师审计准则第1301号", "in_force", ""),
        ("ISA 501", "Audit Evidence—Specific Considerations for Selected Items", "Deals with specific considerations by the auditor in obtaining sufficient appropriate audit evidence with respect to inventory, litigation and claims, and segment information.", "中国注册会计师审计准则第1311号", "in_force", ""),
        ("ISA 505", "External Confirmations", "Deals with the auditor's use of external confirmation procedures to obtain audit evidence in accordance with ISA 330 and ISA 500.", "中国注册会计师审计准则第1312号", "in_force", ""),
        ("ISA 510", "Initial Audit Engagements—Opening Balances", "Deals with the auditor's responsibilities relating to opening balances in an initial audit engagement.", "中国注册会计师审计准则第1331号", "in_force", ""),
        ("ISA 520", "Analytical Procedures", "Deals with the auditor's use of analytical procedures as substantive procedures and near the end of the audit to assist in forming an overall conclusion.", "中国注册会计师审计准则第1313号", "in_force", ""),
        ("ISA 530", "Audit Sampling", "Applies when the auditor has decided to use audit sampling in performing audit procedures, covering statistical and non-statistical sampling design, selection, and evaluation.", "中国注册会计师审计准则第1314号", "in_force", ""),
        ("ISA 540 (Revised)", "Auditing Accounting Estimates and Related Disclosures", "Deals with the auditor's responsibilities relating to accounting estimates and related disclosures in an audit of financial statements, emphasizing estimation uncertainty and inherent risk factors.", "中国注册会计师审计准则第1321号", "in_force", ""),
        ("ISA 550", "Related Parties", "Deals with the auditor's responsibilities relating to related party relationships and transactions in an audit of financial statements.", "中国注册会计师审计准则第1323号", "in_force", ""),
        ("ISA 560", "Subsequent Events", "Deals with the auditor's responsibilities relating to subsequent events in an audit of financial statements, covering events up to and after the auditor's report date.", "中国注册会计师审计准则第1332号", "in_force", ""),
        ("ISA 570 (Revised 2024)", "Going Concern", "Deals with the auditor's responsibilities in the audit of financial statements relating to going concern and the implications for the auditor's report (Revised 2024, published April 2025).", "中国注册会计师审计准则第1324号", "in_force", "Revised 2024 edition published April 2025 in IAASB 2026 Handbook."),
        ("ISA 580", "Written Representations", "Deals with the auditor's responsibility to obtain written representations from management and, where appropriate, those charged with governance.", "中国注册会计师审计准则第1341号", "in_force", ""),
        ("ISA 600 (Revised)", "Special Considerations—Audits of Group Financial Statements (Including the Work of Component Auditors)", "Deals with special considerations that apply to a group audit, including a risk-based approach to scoping components and directing, supervising, and reviewing component auditors.", "中国注册会计师审计准则第1401号", "in_force", ""),
        ("ISA 610 (Revised 2013)", "Using the Work of Internal Auditors", "Deals with the external auditor's responsibilities if using the work of internal auditors, including obtaining audit evidence and direct assistance.", "中国注册会计师审计准则第1411号", "in_force", ""),
        ("ISA 620", "Using the Work of an Auditor's Expert", "Deals with the auditor's responsibilities relating to the work of an individual or organization in a field of expertise other than accounting or auditing, when used to obtain sufficient appropriate audit evidence.", "中国注册会计师审计准则第1421号", "in_force", ""),
        ("ISA 700 (Revised)", "Forming an Opinion and Reporting on Financial Statements", "Deals with the auditor's responsibility to form an opinion on the financial statements and the form and content of the auditor's report.", "中国注册会计师审计准则第1501号", "in_force", ""),
        ("ISA 701", "Communicating Key Audit Matters in the Independent Auditor's Report", "Deals with the auditor's responsibility to communicate key audit matters (KAM) in the auditor's report for listed entities and where required.", "中国注册会计师审计准则第1504号", "in_force", ""),
        ("ISA 705 (Revised)", "Modifications to the Opinion in the Independent Auditor's Report", "Deals with the auditor's responsibility to issue an appropriate report when a modification to the opinion (qualified, adverse, or disclaimer of opinion) is necessary.", "中国注册会计师审计准则第1502号", "in_force", ""),
        ("ISA 706 (Revised)", "Emphasis of Matter Paragraphs and Other Matter Paragraphs in the Independent Auditor's Report", "Deals with additional communication in the auditor's report when the auditor considers it necessary to draw users' attention to a matter via an Emphasis of Matter or Other Matter paragraph.", "中国注册会计师审计准则第1503号", "in_force", ""),
        ("ISA 710", "Comparative Information—Corresponding Figures and Comparative Financial Statements", "Deals with the auditor's responsibilities relating to comparative information in an audit of financial statements.", "中国注册会计师审计准则第1511号", "in_force", ""),
        ("ISA 720 (Revised)", "The Auditor's Responsibilities Relating to Other Information", "Deals with the auditor's responsibilities relating to other information, whether financial or non-financial information, included in an entity's annual report.", "中国注册会计师审计准则第1521号", "in_force", ""),
        ("ISA 800 (Revised)", "Special Considerations—Audits of Financial Statements Prepared in Accordance with Special Purpose Frameworks", "Deals with special considerations in the application of ISAs to an audit of financial statements prepared in accordance with a special purpose framework.", "中国注册会计师审计准则第1601号", "in_force", ""),
        ("ISA 805 (Revised)", "Special Considerations—Audits of Single Financial Statements and Specific Elements, Accounts or Items of a Financial Statement", "Deals with special considerations in the application of ISAs to an audit of a single financial statement or of a specific element, account, or item of a financial statement.", "中国注册会计师审计准则第1603号", "in_force", ""),
        ("ISA 810 (Revised)", "Engagements to Report on Summary Financial Statements", "Deals with the auditor's responsibilities relating to an engagement to report on summary financial statements derived from financial statements audited in accordance with ISAs.", "中国注册会计师审计准则第1604号", "in_force", ""),
    ]

    for code, short_t, summ, cn_prefix, st, vnote in isa_specs:
        docs.append(
            make_doc(
                code=code,
                title=f"{code} {short_t}",
                display_title=short_t,
                domain="audit",
                doc_type="standard",
                issuer="IAASB",
                source_name="IAASB 2026 Handbook",
                source_url=hb_url,
                summary=summ,
                status=st,
                version_level="info" if vnote else "",
                version_note=vnote,
                cas_links=[[cn_prefix, f"{code} 与我国审计准则直接对照"]],
            )
        )

    # 3. ISA for LCE + Review (ISRE) + Assurance (ISAE / ISSA) + Related Services (ISRS)
    docs.extend([
        make_doc(
            code="ISA for LCE",
            title="International Standard on Auditing for Audits of Financial Statements of Less Complex Entities (ISA for LCE)",
            display_title="Audits of Financial Statements of Less Complex Entities (ISA for LCE)",
            domain="audit",
            doc_type="standard",
            issuer="IAASB",
            source_name="IAASB 2026 Handbook",
            source_url=hb_url,
            summary="Standalone global auditing standard designed specifically for audits of financial statements of less complex entities (LCEs), providing a proportionate risk-based audit framework effective for periods beginning on or after 15 Dec 2025.",
            pub_date="2023-12-06",
            effective_date="2025-12-15",
            cited_codes=["ISA 200", "ISQM 1"],
        ),
        make_doc(
            code="ISRE 2400 (Revised)",
            title="ISRE 2400 (Revised) Engagements to Review Historical Financial Statements",
            display_title="Engagements to Review Historical Financial Statements",
            domain="audit",
            doc_type="standard",
            issuer="IAASB",
            source_name="IAASB 2026 Handbook",
            source_url=hb_url,
            summary="Deals with the practitioner's responsibilities when engaged to perform a review of historical financial statements when the practitioner is not the auditor of the entity's financial statements.",
            cited_codes=["Assurance Framework", "ISRE 2410"],
            cas_links=[["中国注册会计师审阅准则第2101号", "ISRE 2400 与我国财务报表审阅准则对照"]],
        ),
        make_doc(
            code="ISRE 2410",
            title="ISRE 2410 Review of Interim Financial Information Performed by the Independent Auditor of the Entity",
            display_title="Review of Interim Financial Information by the Independent Auditor",
            domain="audit",
            doc_type="standard",
            issuer="IAASB",
            source_name="IAASB 2026 Handbook",
            source_url=hb_url,
            summary="Establishes standards and provides guidance on the auditor's professional responsibilities when undertaking an engagement to review interim financial information of an audit client.",
            cited_codes=["ISRE 2400 (Revised)", "IAS 34"],
            cas_links=[["中国注册会计师审阅准则第2101号", "中期财务信息审阅对照"]],
        ),
        make_doc(
            code="ISAE 3000 (Revised)",
            title="ISAE 3000 (Revised) Assurance Engagements Other than Audits or Reviews of Historical Financial Information",
            display_title="Assurance Engagements Other than Audits or Reviews of Historical Financial Information",
            domain="audit",
            doc_type="standard",
            issuer="IAASB",
            source_name="IAASB 2026 Handbook",
            source_url=hb_url,
            summary="Umbrella standard for reasonable and limited assurance engagements other than audits or reviews of historical financial information.",
            cited_codes=["Assurance Framework", "ISAE 3402", "ISAE 3410", "ISSA 5000"],
            cas_links=[["中国注册会计师其他鉴证业务准则第3101号", "ISAE 3000 与我国其他鉴证业务准则第3101号直接对照"]],
        ),
        make_doc(
            code="ISAE 3400",
            title="ISAE 3400 The Examination of Prospective Financial Information",
            display_title="The Examination of Prospective Financial Information",
            domain="audit",
            doc_type="standard",
            issuer="IAASB",
            source_name="IAASB 2026 Handbook",
            source_url=hb_url,
            summary="Establishes standards and provides guidance on engagements to examine and report on prospective financial information (forecasts and projections).",
            cited_codes=["ISAE 3000 (Revised)"],
            cas_links=[["中国注册会计师其他鉴证业务准则第3111号", "ISAE 3400 与我国预测性财务信息审核第3111号直接对照"]],
        ),
        make_doc(
            code="ISAE 3402",
            title="ISAE 3402 Assurance Reports on Controls at a Service Organization",
            display_title="Assurance Reports on Controls at a Service Organization",
            domain="audit",
            doc_type="standard",
            issuer="IAASB",
            source_name="IAASB 2026 Handbook",
            source_url=hb_url,
            summary="Deals with assurance engagements undertaken by a professional accountant in public practice to provide a report for use by user entities and their auditors on the controls at a service organization (Type 1 & Type 2).",
            cited_codes=["ISAE 3000 (Revised)", "ISA 402"],
        ),
        make_doc(
            code="ISAE 3410",
            title="ISAE 3410 Assurance Engagements on Greenhouse Gas Statements",
            display_title="Assurance Engagements on Greenhouse Gas Statements",
            domain="audit",
            doc_type="standard",
            issuer="IAASB",
            source_name="IAASB 2026 Handbook",
            source_url=hb_url,
            summary="Deals with assurance engagements to report on an entity's greenhouse gas (GHG) statement, complementing ISAE 3000 (Revised) and ISSA 5000.",
            cited_codes=["ISAE 3000 (Revised)", "ISSA 5000", "IFRS S2"],
        ),
        make_doc(
            code="ISAE 3420",
            title="ISAE 3420 Assurance Engagements to Report on the Compilation of Pro Forma Financial Information Included in a Prospectus",
            display_title="Assurance Reports on Pro Forma Financial Information in a Prospectus",
            domain="audit",
            doc_type="standard",
            issuer="IAASB",
            source_name="IAASB 2026 Handbook",
            source_url=hb_url,
            summary="Deals with reasonable assurance engagements undertaken by a practitioner to report on the responsible party's compilation of pro forma financial information included in a prospectus.",
            cited_codes=["ISAE 3000 (Revised)"],
        ),
        make_doc(
            code="ISSA 5000",
            title="ISSA 5000 General Requirements for Sustainability Assurance Engagements",
            display_title="General Requirements for Sustainability Assurance Engagements",
            domain="audit",
            doc_type="standard",
            issuer="IAASB",
            source_name="IAASB 2026 Handbook",
            source_url=hb_url,
            summary="Overarching global standard for limited and reasonable sustainability assurance engagements across all sustainability reporting frameworks (including IFRS S1/S2), effective for periods beginning on or after 15 Dec 2026.",
            pub_date="2024-11-12",
            effective_date="2026-12-15",
            status="upcoming",
            version_level="upcoming",
            version_note="Effective for sustainability assurance engagements for periods beginning on or after 15 Dec 2026; early adoption permitted.",
            cited_codes=["IFRS S1", "IFRS S2", "ISQM 1", "IESBA Code Part 5 (IESSA)", "ISAE 3000 (Revised)"],
            cas_links=[["可持续信息鉴证业务准则第6101号——基本准则（试行）", "ISSA 5000 与我国可持续信息鉴证基本准则第6101号直接对照"]],
        ),
        make_doc(
            code="ISRS 4400 (Revised)",
            title="ISRS 4400 (Revised) Agreed-Upon Procedures Engagements",
            display_title="Agreed-Upon Procedures Engagements",
            domain="audit",
            doc_type="standard",
            issuer="IAASB",
            source_name="IAASB 2026 Handbook",
            source_url=hb_url,
            summary="Deals with the practitioner's responsibilities when engaged to perform an agreed-upon procedures (AUP) engagement and the form and content of the AUP report.",
            cas_links=[["中国注册会计师相关服务准则第4101号", "ISRS 4400 与我国商定程序准则第4101号直接对照"]],
        ),
        make_doc(
            code="ISRS 4410 (Revised)",
            title="ISRS 4410 (Revised) Compilation Engagements",
            display_title="Compilation Engagements",
            domain="audit",
            doc_type="standard",
            issuer="IAASB",
            source_name="IAASB 2026 Handbook",
            source_url=hb_url,
            summary="Deals with the practitioner's responsibilities when engaged to assist management with the preparation and presentation of historical financial information without obtaining any assurance on that information.",
            cas_links=[["中国注册会计师相关服务准则第4111号", "ISRS 4410 与我国代编财务信息准则第4111号直接对照"]],
        ),
    ])
    return docs


def build_iesba() -> list[dict]:
    iesba_url = "https://www.ethicsboard.org/publications/2026-handbook-international-code-ethics-professional-accountants"
    return [
        make_doc(
            code="IESBA Code Part 1–3",
            title="IESBA International Code of Ethics for Professional Accountants — Parts 1 to 3 (Fundamental Principles, PAIBs & PAPPs)",
            display_title="IESBA Code of Ethics — Parts 1–3 (Fundamental Principles & Conceptual Framework)",
            domain="audit",
            doc_type="standard",
            issuer="IESBA",
            source_name="IESBA 2026 Handbook",
            source_url=iesba_url,
            summary="Establishes the five fundamental principles (integrity, objectivity, professional competence and due care, confidentiality, professional behavior) and the conceptual framework for all professional accountants in business (Part 2) and public practice (Part 3), incorporating 2026 external expert and sustainability reporting revisions.",
            pub_date="2026-09-01",
            effective_date="2026-12-15",
            status="in_force",
            cited_codes=["IESBA Code Part 4A", "IESBA Code Part 4B", "ISQM 1", "ISA 200"],
            cas_links=[["发布通知——中国注册会计师独立性准则第1号", "国际职业道德守则总则与我国职业道德/独立性框架对照"]],
        ),
        make_doc(
            code="IESBA Code Part 4A",
            title="IESBA International Independence Standards — Part 4A (Independence for Audit and Review Engagements)",
            display_title="IESBA Independence Standards — Part 4A (Audit & Review)",
            domain="audit",
            doc_type="standard",
            issuer="IESBA",
            source_name="IESBA 2026 Handbook",
            source_url=iesba_url,
            summary="Sets out the International Independence Standards applicable to audit and review engagements, including public interest entity (PIE) definitions, fee-related provisions, non-assurance services restrictions, and partner rotation.",
            pub_date="2026-09-01",
            effective_date="2026-12-15",
            status="in_force",
            cited_codes=["IESBA Code Part 1–3", "ISQM 1", "ISA 220 (Revised)"],
            cas_links=[["发布通知——中国注册会计师独立性准则第1号", "IESBA Part 4A 与我国独立性准则第1号直接对照"]],
        ),
        make_doc(
            code="IESBA Code Part 4B",
            title="IESBA International Independence Standards — Part 4B (Independence for Assurance Engagements Other than Audit and Review)",
            display_title="IESBA Independence Standards — Part 4B (Other Assurance)",
            domain="audit",
            doc_type="standard",
            issuer="IESBA",
            source_name="IESBA 2026 Handbook",
            source_url=iesba_url,
            summary="Sets out independence standards for assurance engagements other than audit, review, and sustainability assurance engagements covered by Part 5.",
            pub_date="2026-09-01",
            effective_date="2026-12-15",
            status="in_force",
            cited_codes=["IESBA Code Part 1–3", "ISAE 3000 (Revised)"],
            cas_links=[["中国注册会计师其他鉴证业务准则第3101号", "其他鉴证业务独立性要求对照"]],
        ),
        make_doc(
            code="IESBA Code Part 5 (IESSA)",
            title="IESBA International Ethics Standards for Sustainability Assurance (including International Independence Standards) — Part 5 (IESSA)",
            display_title="International Ethics Standards for Sustainability Assurance (Part 5 — IESSA)",
            domain="audit",
            doc_type="standard",
            issuer="IESBA",
            source_name="IESBA 2026 Handbook (Volume 2)",
            source_url=iesba_url,
            summary="Profession-agnostic ethics and independence standards for all sustainability assurance practitioners (Volume 2 of the 2026 IESBA Handbook), effective for sustainability assurance engagements for periods beginning on or after 15 Dec 2026.",
            pub_date="2025-01-27",
            effective_date="2026-12-15",
            status="upcoming",
            version_level="upcoming",
            version_note="Effective for sustainability assurance engagements for periods beginning on or after 15 Dec 2026.",
            cited_codes=["ISSA 5000", "IFRS S1", "IFRS S2", "IESBA Code Part 1–3"],
            cas_links=[["可持续信息鉴证业务准则第6101号——基本准则（试行）", "IESSA 可持续鉴证职业道德与我国可持续鉴证准则衔接"]],
        ),
    ]


def build_oecd_tax() -> list[dict]:
    return [
        make_doc(
            code="OECD Pillar Two (GloBE)",
            title="OECD Global Anti-Base Erosion (GloBE) Model Rules — Pillar Two (15% Global Minimum Tax)",
            display_title="Pillar Two — Global Minimum Tax (GloBE Model Rules)",
            domain="tax",
            doc_type="standard",
            issuer="OECD / G20 Inclusive Framework",
            source_name="OECD",
            source_url="https://www.oecd.org/en/topics/sub-issues/global-minimum-tax/global-anti-base-erosion-model-rules-pillar-two.html",
            summary="Sets out the coordinated 15% global minimum tax framework (Income Inclusion Rule — IIR, Undertaxed Profits Rule — UTPR, and Qualified Domestic Minimum Top-up Tax — QDMTT) for MNE groups with consolidated revenue ≥ EUR 750 million. Directly linked to IAS 12 Pillar Two amendments.",
            pub_date="2021-12-20",
            effective_date="2024-01-01",
            status="in_force",
            cited_codes=["IAS 12", "OECD Model Tax Convention"],
            cas_links=[["中华人民共和国企业所得税法", "跨国集团全球最低税规则与企业所得税跨境衔接"]],
        ),
        make_doc(
            code="OECD Model Tax Convention",
            title="OECD Model Tax Convention on Income and on Capital",
            display_title="Model Tax Convention on Income and on Capital",
            domain="tax",
            doc_type="standard",
            issuer="OECD",
            source_name="OECD",
            source_url="https://www.oecd.org/en/topics/sub-issues/oecd-model-tax-convention-on-income-and-on-capital.html",
            summary="Global template for bilateral double taxation treaties covering residency, permanent establishment (PE), business profits, dividends/interest/royalties withholding tax, and mutual agreement procedures (MAP).",
            pub_date="2017-11-21",
            effective_date="2017-11-21",
            status="in_force",
            cited_codes=["OECD Transfer Pricing Guidelines", "OECD Pillar Two (GloBE)"],
            cas_links=[["中华人民共和国企业所得税法", "税收协定范本与企业所得税跨境征管衔接"]],
        ),
        make_doc(
            code="OECD Transfer Pricing Guidelines",
            title="OECD Transfer Pricing Guidelines for Multinational Enterprises and Tax Administrations",
            display_title="Transfer Pricing Guidelines for MNEs and Tax Administrations",
            domain="tax",
            doc_type="guidance",
            issuer="OECD",
            source_name="OECD",
            source_url="https://www.oecd.org/en/topics/sub-issues/transfer-pricing.html",
            summary="Authoritative international guidance on the arm's length principle, comparability analysis, transfer pricing methods (CUP, RPM, CPLM, TNMM, Profit Split), intangibles, intra-group services, and Country-by-Country Reporting (CbCR).",
            pub_date="2022-01-20",
            effective_date="2022-01-20",
            status="in_force",
            cited_codes=["OECD Model Tax Convention", "IAS 24"],
            cas_links=[["中华人民共和国企业所得税法", "特别纳税调整/转让定价国际规则与企业所得税法衔接"]],
        ),
    ]


def write_dataset(filename: str, source: str, docs: list[dict]) -> None:
    INTL_DATA_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": dt.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "source": source,
        "count": len(docs),
        "documents": docs,
    }
    out = INTL_DATA_DIR / filename
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {out.name}: {len(docs)} documents")


def main() -> int:
    write_dataset("issb_sustainability.json", "IFRS Foundation (ISSB)", build_issb())
    write_dataset("iaasb_auditing.json", "IAASB 2026 Handbook", build_iaasb())
    write_dataset("iesba_ethics.json", "IESBA 2026 Handbook", build_iesba())
    write_dataset("oecd_tax.json", "OECD", build_oecd_tax())
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
