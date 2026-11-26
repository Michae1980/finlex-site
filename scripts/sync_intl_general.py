#!/usr/bin/env python3
"""
生成国际综合商法、公司治理、内部控制与反洗钱合规公开数据源（intl_data/intl_general_gov.json）
覆盖：
1. G20/OECD Principles of Corporate Governance (2023)
2. FATF 40 Recommendations (updated June 2026)
3. COSO Internal Control — Integrated Framework (2013 + 2023 ICSR + 2026 GenAI)
4. COSO Enterprise Risk Management — Integrating with Strategy and Performance (2017)
5. OECD Guidelines for Multinational Enterprises on Responsible Business Conduct (2023)

全部内容均为基于官方公开摘要整理的结构化导读与官方原文入口，严格遵守版权合规边界。
"""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUT_PATH = PROJECT_ROOT / "intl_data" / "intl_general_gov.json"

DOCS = [
    {
        "code": "G20/OECD Corporate Governance",
        "framework": "INTL",
        "domain": "general",
        "doc_type": "standard",
        "title": "G20/OECD Principles of Corporate Governance (2023 Edition)",
        "display_title": "G20/OECD Principles of Corporate Governance (2023)",
        "series_badge": "G20/OECD CG",
        "doc_no": "G20/OECD CG 2023",
        "issuer": "OECD / G20",
        "pub_date": "2023-09-11",
        "effective_date": "2023-09-11",
        "status": "in_force",
        "version_level": "",
        "version_note": "",
        "source_name": "OECD Official Publication",
        "source_url": "https://www.oecd.org/en/publications/g20-oecd-principles-of-corporate-governance-2023_ed750b30-en.html",
        "source_kind": "official",
        "summary": "The international benchmark for policy makers, investors, corporations, and stakeholders worldwide (Financial Stability Board Key Standard). The 2023 revision introduces a dedicated Chapter VI on Sustainability and Resilience alongside modernized rules on shareholder rights, related-party transactions, digital general meetings, and board oversight.",
        "cited_codes": [
            "IFRS S1",
            "IAS 24",
            "COSO Internal Control (ICIF)",
            "OECD MNE Guidelines (RBC)",
        ],
        "cas_links": [
            [
                "中华人民共和国公司法（2023年第二次修订）",
                "G20/OECD 公司治理原则与我国2023年新《公司法》董事忠实勤勉义务、审计委员会及股东权利对照",
            ],
            [
                "中华人民共和国证券法（2019年第二次修订）",
                "上市公司信息披露透明度、关联交易监管与中小投资者保护对照",
            ],
        ],
        "articles": [
            {
                "no": "Overview",
                "heading": "Scope & Global Benchmark Status (2023 Edition)",
                "text": "Endorsed by G20 Leaders in September 2023, the G20/OECD Principles of Corporate Governance serve as the global standard for sound corporate governance and one of the Financial Stability Board's (FSB) Key Standards for Sound Financial Systems. Structured into six chapters, the 2023 edition updates guidance for capital markets, company groups, digital technologies, bondholder rights, and sustainability-related risks.",
                "seq": 0,
            },
            {
                "no": "Chapters I–III",
                "heading": "Framework, Shareholder Rights & Institutional Investors",
                "text": "[Chapter I — Effective Corporate Governance Framework]\n• Transparent and fair markets, efficient resource allocation, clear division of supervisory/regulatory responsibilities, and cross-border regulatory cooperation.\n\n[Chapter II — Rights & Equitable Treatment of Shareholders]\n• Basic ownership rights, participation and voting in general meetings (including remote/hybrid digital meetings), disclosure of disproportionate control/capital structures, and fair approval/disclosure of material related-party transactions (aligning with IAS 24).\n• Clear rules for corporate control markets, takeovers, and protection of minority shareholders in company groups.\n\n[Chapter III — Institutional Investors, Stock Markets & Intermediaries]\n• Stewardship and voting policy disclosures by institutional investors, management of conflicts of interest by proxy advisors, analysts, rating agencies, and ESG rating/data providers.",
                "seq": 1,
            },
            {
                "no": "Chapters IV–VI",
                "heading": "Disclosure, Board Responsibilities & Sustainability (New in 2023)",
                "text": "[Chapter IV — Disclosure and Transparency]\n• Timely and accurate disclosure of financial and operating results, major share ownership and beneficial ownership, remuneration, related-party transactions, and foreseeable risk factors; high-quality accounting (IFRS) and independent annual external audit (ISAs).\n\n[Chapter V — Responsibilities of the Board]\n• Duty of care and duty of loyalty; guiding corporate strategy, overseeing internal control and risk management (aligning with COSO ICIF / ERM), selecting/monitoring key executives, ensuring integrity of accounting/reporting systems, and maintaining board independence and audit committee effectiveness.\n\n[Chapter VI — Sustainability and Resilience (New 2023 Chapter)]\n• Consistent, comparable, and reliable sustainability-related disclosures (interoperable with IFRS S1 / S2), independent assurance over sustainability information (ISSA 5000), board oversight of climate and stakeholder risks, and dialogue between companies, shareholders, and stakeholders.",
                "seq": 2,
            },
            {
                "no": "Official Access",
                "heading": "Official Publication & Full Report Entry",
                "text": "Official Publication Page: https://www.oecd.org/en/publications/g20-oecd-principles-of-corporate-governance-2023_ed750b30-en.html\nFull Online Report: https://www.oecd.org/en/publications/g20-oecd-principles-of-corporate-governance-2023_ed750b30-en/full-report.html\nStatus: in_force (2023 Edition).",
                "seq": 3,
            },
        ],
    },
    {
        "code": "FATF 40 Recommendations",
        "framework": "INTL",
        "domain": "general",
        "doc_type": "standard",
        "title": "FATF Recommendations — International Standards on Combating Money Laundering and the Financing of Terrorism & Proliferation",
        "display_title": "FATF 40 Recommendations (AML / CFT / CPF)",
        "series_badge": "FATF 40 Recs",
        "doc_no": "FATF 40 Recommendations",
        "issuer": "FATF (Financial Action Task Force)",
        "pub_date": "2026-06-01",
        "effective_date": "2026-06-01",
        "status": "in_force",
        "version_level": "",
        "version_note": "",
        "source_name": "FATF Official Standards",
        "source_url": "https://www.fatf-gafi.org/en/publications/Fatfrecommendations/Fatf-recommendations.html",
        "source_kind": "official",
        "summary": "The globally recognized international AML/CFT/CPF standards (originally adopted Feb 2012, regularly updated through June 2026). Covers 40 Recommendations across risk-based policies, customer due diligence (CDD), virtual assets (R.15), payment transparency (R.16), beneficial ownership of legal persons and arrangements (R.24/R.25), DNFBPs (including accountants/auditors), and international cooperation.",
        "cited_codes": [
            "ISA 250 (Revised)",
            "IESBA Code Part 1–3",
            "G20/OECD Corporate Governance",
        ],
        "cas_links": [
            [
                "中华人民共和国公司法（2023年第二次修订）",
                "FATF R.24 法人受益所有人透明度要求与公司股权登记治理衔接",
            ],
        ],
        "articles": [
            {
                "no": "Overview",
                "heading": "Scope & 2025–2026 Revision Highlights",
                "text": "The FATF Recommendations set out a comprehensive, consistent framework of measures that countries should implement to combat money laundering (ML), terrorist financing (TF), and proliferation financing (PF). Updated continuously (most recently June 2026), recent revisions strengthened R.1 (risk-based proportionality and financial inclusion), R.16 (payment transparency and cross-border wire transfers), and R.24/R.25 (beneficial ownership registries and trust transparency).",
                "seq": 0,
            },
            {
                "no": "R.1–R.23",
                "heading": "AML/CFT Policies, Preventive Measures & DNFBPs (Accountants)",
                "text": "[A. AML/CFT Policies & Coordination (R.1–R.2)]\n• R.1: Risk-based approach (RBA) — countries, financial institutions, and DNFBPs identify, assess, and mitigate ML/TF/PF risks proportionately.\n• R.2: National cooperation and coordination among FIUs, supervisors, and law enforcement.\n\n[B–C. Money Laundering, Confiscation & Terrorist/Proliferation Financing (R.3–R.8)]\n• Criminalization of ML/TF, asset confiscation and provisional measures (R.4), targeted financial sanctions (R.6–R.7), and non-profit organization risk safeguards (R.8).\n\n[D. Preventive Measures (R.9–R.23)]\n• R.10–R.12: Customer Due Diligence (CDD), record-keeping (at least 5 years), and enhanced due diligence for Politically Exposed Persons (PEPs).\n• R.15 (New Technologies & Virtual Assets): AML/CFT regulation and Travel Rule for Virtual Asset Service Providers (VASPs).\n• R.16 (Payment Transparency): Originator and beneficiary information required across cross-border payment chains.\n• R.20–R.21: Suspicious Transaction Reporting (STR) to the Financial Intelligence Unit (FIU) and prohibition on tipping-off.\n• R.22–R.23 (DNFBPs): Extends CDD, record-keeping, and STR obligations to Designated Non-Financial Businesses and Professions, explicitly including accountants, auditors, lawyers, and trust/company service providers (TCSPs) when preparing or carrying out covered transactions (interacting directly with ISA 250 and IESBA NOCLAR Sections 260/360).",
                "seq": 1,
            },
            {
                "no": "R.24–R.40",
                "heading": "Beneficial Ownership, Powers & International Cooperation",
                "text": "[E. Transparency and Beneficial Ownership (R.24–R.25)]\n• R.24 (Legal Persons): Requires adequate, accurate, and up-to-date beneficial ownership information via multi-pronged mechanisms (including public authority registries), restrictions on bearer shares and nominee arrangements.\n• R.25 (Legal Arrangements): Requires trustees of express trusts and similar legal arrangements to maintain accurate beneficial ownership information on settlors, trustees, protectors, and beneficiaries.\n\n[F. Powers & Responsibilities of Competent Authorities (R.26–R.35)]\n• Risk-based supervision of financial institutions and DNFBPs, operational independence of FIUs (R.29), law enforcement investigative powers, and proportionate dissuasive sanctions (R.35).\n\n[G. International Cooperation (R.36–R.40)]\n• Mutual legal assistance (MLA), cross-border asset freezing/confiscation, extradition, and spontaneous supervisory/FIU information exchange.",
                "seq": 2,
            },
            {
                "no": "Official Access",
                "heading": "Official FATF Standards & Topic Hub",
                "text": "Official Recommendations Publication: https://www.fatf-gafi.org/en/publications/Fatfrecommendations/Fatf-recommendations.html\nFATF Recommendations Topic Hub: https://www.fatf-gafi.org/en/topics/fatf-recommendations.html\nStatus: in_force (updated June 2026).",
                "seq": 3,
            },
        ],
    },
    {
        "code": "COSO Internal Control (ICIF)",
        "framework": "INTL",
        "domain": "general",
        "doc_type": "standard",
        "title": "COSO Internal Control — Integrated Framework (ICIF 2013, with 2023 ICSR & 2026 GenAI Guidance)",
        "display_title": "COSO Internal Control — Integrated Framework (ICIF)",
        "series_badge": "COSO ICIF",
        "doc_no": "COSO ICIF (2013)",
        "issuer": "COSO (Committee of Sponsoring Organizations of the Treadway Commission)",
        "pub_date": "2013-05-14",
        "effective_date": "2014-12-15",
        "status": "in_force",
        "version_level": "",
        "version_note": "",
        "source_name": "COSO Official Guidance",
        "source_url": "https://www.coso.org/guidance-on-ic",
        "source_kind": "official",
        "summary": "The preeminent global framework for designing, implementing, conducting, and assessing internal control (widely used for SOX 404 ICFR and aligned with China's Basic Standard for Enterprise Internal Control). Structured around 3 objective categories (Operations, Reporting, Compliance), 5 integrated components, and 17 principles, supplemented by COSO guidance on Sustainability Reporting (ICSR 2023), RPA (2024), and Generative AI (2026).",
        "cited_codes": [
            "COSO ERM (2017)",
            "ISA 315 (Revised 2019)",
            "IFRS S1",
            "G20/OECD Corporate Governance",
        ],
        "cas_links": [
            [
                "企业内部控制基本规范（财会〔2008〕7号）",
                "COSO 内部控制五要素（控制环境、风险评估、控制活动、信息与沟通、监督）与我国《企业内部控制基本规范》直接对照",
            ],
            [
                "企业内部控制配套指引——评价指引",
                "COSO 17项原则存在性与运行有效性评价与我国内控评价指引对照",
            ],
        ],
        "articles": [
            {
                "no": "Overview",
                "heading": "The COSO Cube: 3 Objectives, 5 Components & 17 Principles",
                "text": "Published by COSO (sponsored by AAA, AICPA, FEI, IIA, and IMA) in May 2013 (superseding the 1992 framework), the Internal Control — Integrated Framework defines internal control as a process, effected by an entity's board of directors, management, and other personnel, designed to provide reasonable assurance regarding the achievement of objectives relating to Operations, Reporting (internal/external, financial and non-financial), and Compliance. An effective system requires all 5 components and all 17 relevant principles to be present and functioning together.",
                "seq": 0,
            },
            {
                "no": "Components 1–5 (17 Principles)",
                "heading": "Five Integrated Components & Seventeen Principles",
                "text": "[1. Control Environment (Principles 1–5)]\n• P1: Demonstrates commitment to integrity and ethical values.\n• P2: Board of directors exercises independence and oversight of internal control.\n• P3: Management establishes structures, reporting lines, and appropriate authorities/responsibilities.\n• P4: Demonstrates commitment to attract, develop, and retain competent individuals.\n• P5: Holds individuals accountable for their internal control responsibilities.\n\n[2. Risk Assessment (Principles 6–9)]\n• P6: Specifies objectives with sufficient clarity to identify and assess risks.\n• P7: Identifies risks to achievement of objectives across the entity and analyzes them.\n• P8: Considers the potential for fraud in assessing risks.\n• P9: Identifies and assesses changes that could significantly impact the system of internal control.\n\n[3. Control Activities (Principles 10–12)]\n• P10: Selects and develops control activities (preventive/detective, manual/automated) mitigating risks.\n• P11: Selects and develops general control activities over technology (ITGCs).\n• P12: Deploys control activities through policies and procedures.\n\n[4. Information & Communication (Principles 13–15)]\n• P13: Obtains or generates and uses relevant, quality information.\n• P14: Internally communicates internal control objectives and responsibilities.\n• P15: Communicates with external parties regarding matters affecting internal control.\n\n[5. Monitoring Activities (Principles 16–17)]\n• P16: Selects, develops, and performs ongoing and/or separate evaluations.\n• P17: Evaluates and communicates internal control deficiencies timely to management and the board.",
                "seq": 1,
            },
            {
                "no": "ICSR (2023) & GenAI (2026)",
                "heading": "Supplemental Guidance: Sustainability Reporting (ICSR), RPA & Generative AI",
                "text": "• Achieving Effective Internal Control Over Sustainability Reporting — ICSR (2023): Applies the 5 components and 17 principles to ESG / sustainability data, estimates, and value-chain reporting supporting IFRS S1 / S2 and ISSA 5000 assurance readiness.\n• Robotic Process Automation (2024) & Generative AI Guidance (2026): Addresses governance, model/prompt risk assessment, data privacy, hallucination controls, and human-in-the-loop monitoring when deploying AI in financial and operational processes.\n• Fraud Risk Management Guide (2023 Edition): Companion operational guide detailing anti-fraud governance, fraud risk assessment, control activities, investigation, and monitoring.",
                "seq": 2,
            },
            {
                "no": "Official Access",
                "heading": "Official COSO Internal Control Hub",
                "text": "Official Guidance Page: https://www.coso.org/guidance-on-ic\nStatus: in_force (2013 Integrated Framework + 2023–2026 Supplemental Guidance).",
                "seq": 3,
            },
        ],
    },
    {
        "code": "COSO ERM (2017)",
        "framework": "INTL",
        "domain": "general",
        "doc_type": "standard",
        "title": "COSO Enterprise Risk Management — Integrating with Strategy and Performance (2017)",
        "display_title": "COSO Enterprise Risk Management (ERM 2017)",
        "series_badge": "COSO ERM",
        "doc_no": "COSO ERM (2017)",
        "issuer": "COSO (Committee of Sponsoring Organizations of the Treadway Commission)",
        "pub_date": "2017-09-06",
        "effective_date": "2017-09-06",
        "status": "in_force",
        "version_level": "",
        "version_note": "",
        "source_name": "COSO Official Portal",
        "source_url": "https://www.coso.org/about-us",
        "source_kind": "official",
        "summary": "Updates the 2004 COSO ERM framework to highlight the importance of considering risk in both strategy-setting and driving performance. Organizes enterprise risk management into 5 interrelated components and 20 principles spanning governance & culture, strategy & objective-setting, performance, review & revision, and information/reporting.",
        "cited_codes": [
            "COSO Internal Control (ICIF)",
            "G20/OECD Corporate Governance",
            "ISA 315 (Revised 2019)",
        ],
        "cas_links": [
            [
                "企业内部控制基本规范（财会〔2008〕7号）",
                "COSO 全面风险管理框架与我国企业内部控制风险评估与战略治理衔接",
            ],
        ],
        "articles": [
            {
                "no": "Overview",
                "heading": "Integrating Risk Management with Strategy & Value Creation",
                "text": "COSO's 2017 Enterprise Risk Management — Integrating with Strategy and Performance moves beyond compliance-centric risk lists to embed risk considerations into mission, vision, core values, strategy formulation, and day-to-day performance. While distinct from Internal Control (ICIF), ERM complements ICIF by addressing risk appetite, strategic alignment, and enterprise-wide portfolio views of risk.",
                "seq": 0,
            },
            {
                "no": "Components 1–5 (20 Principles)",
                "heading": "Five Interrelated ERM Components & Key Principles",
                "text": "• 1. Governance and Culture (Principles 1–5): Board risk oversight, operating structures, desired culture, commitment to core values, and talent development.\n• 2. Strategy and Objective-Setting (Principles 6–9): Analyzing business context, defining risk appetite, evaluating alternative strategies, and formulating business objectives.\n• 3. Performance (Principles 10–14): Identifying risk, assessing severity of risk, prioritizing risks, implementing risk responses (accept, avoid, pursue, reduce, share), and developing a portfolio view.\n• 4. Review and Revision (Principles 15–17): Assessing substantial change, reviewing risk and performance, and pursuing improvement in ERM.\n• 5. Information, Communication, and Reporting (Principles 18–20): Leveraging information and technology, communicating risk information, and reporting on risk, culture, and performance.",
                "seq": 1,
            },
            {
                "no": "Official Access",
                "heading": "Official COSO Portal Entry",
                "text": "Official COSO Portal: https://www.coso.org/about-us\nInternal Control Guidance Hub: https://www.coso.org/guidance-on-ic\nStatus: in_force (2017 Edition).",
                "seq": 2,
            },
        ],
    },
    {
        "code": "OECD MNE Guidelines (RBC)",
        "framework": "INTL",
        "domain": "general",
        "doc_type": "standard",
        "title": "OECD Guidelines for Multinational Enterprises on Responsible Business Conduct (2023 Edition)",
        "display_title": "OECD MNE Guidelines on Responsible Business Conduct (2023)",
        "series_badge": "OECD MNE RBC",
        "doc_no": "OECD MNE RBC 2023",
        "issuer": "OECD",
        "pub_date": "2023-06-08",
        "effective_date": "2023-06-08",
        "status": "in_force",
        "version_level": "",
        "version_note": "",
        "source_name": "OECD Official Publication",
        "source_url": "https://www.oecd.org/en/publications/oecd-guidelines-for-multinational-enterprises-on-responsible-business-conduct_81f92357-en.html",
        "source_kind": "official",
        "summary": "The foremost government-backed international standard on Responsible Business Conduct (RBC) for multinational enterprises. The 2023 update incorporates climate change and biodiversity alignment, technology/AI due diligence, supply-chain human rights, anti-bribery, taxation transparency, and the unique National Contact Point (NCP) grievance mechanism.",
        "cited_codes": [
            "G20/OECD Corporate Governance",
            "IFRS S1",
            "OECD Transfer Pricing Guidelines",
        ],
        "cas_links": [
            [
                "中华人民共和国公司法（2023年第二次修订）",
                "跨国企业负责任商业行为与我国2023年《公司法》第20条社会责任及利益相关方保护对照",
            ],
        ],
        "articles": [
            {
                "no": "Overview",
                "heading": "Scope & 2023 Responsible Business Conduct Update",
                "text": "Adopted by adhering governments representing the major global economies, the OECD Guidelines for Multinational Enterprises on Responsible Business Conduct provide non-binding principles and standards for responsible conduct in a global context. The June 2023 update strengthens expectations on climate transition, biodiversity, digital technology, downstream value-chain due diligence, and anti-corruption.",
                "seq": 0,
            },
            {
                "no": "6-Step Due Diligence & Chapters",
                "heading": "Risk-Based Due Diligence, Core Chapters & National Contact Points",
                "text": "[6-Step Risk-Based Due Diligence Process]\n• 1. Embed RBC into policies and management systems.\n• 2. Identify and assess actual and potential adverse impacts in operations, supply chains, and business relationships.\n• 3. Cease, prevent, or mitigate adverse impacts.\n• 4. Track implementation and results.\n• 5. Communicate how impacts are addressed.\n• 6. Provide for or cooperate in remediation when appropriate.\n\n[Core Thematic Chapters]\n• Disclosure (Ch. III): Transparent reporting on financial, governance, and sustainability impacts.\n• Human Rights & Employment (Ch. IV–V): Alignment with UN Guiding Principles on Business and Human Rights.\n• Environment (Ch. VI): Science-based climate targets, Scope 1–3 emissions, biodiversity, and circular economy.\n• Combating Bribery & Solicitation (Ch. VII), Consumer Interests (Ch. VIII), Science/Technology/Innovation (Ch. IX), Competition (Ch. X), and Taxation (Ch. XI — complying with both the letter and spirit of tax laws, cooperating with tax authorities, and applying arm's length pricing).\n• National Contact Points (NCPs): Government-established non-judicial grievance and mediation bodies handling specific instances alleging non-observance of the Guidelines.",
                "seq": 1,
            },
            {
                "no": "Official Access",
                "heading": "Official Publication & RBC Topic Hub",
                "text": "Official Publication Page: https://www.oecd.org/en/publications/oecd-guidelines-for-multinational-enterprises-on-responsible-business-conduct_81f92357-en.html\nOECD Responsible Business Conduct Hub: https://www.oecd.org/en/topics/responsible-business-conduct.html\nStatus: in_force (2023 Edition).",
                "seq": 2,
            },
        ],
    },
]


def main() -> int:
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "generated_at": dt.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "source": "OECD / FATF / COSO Official Public Standards",
        "count": len(DOCS),
        "documents": DOCS,
    }
    OUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {len(DOCS)} INTL general governance/IC/AML documents -> {OUT_PATH.relative_to(PROJECT_ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
