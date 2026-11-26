#!/usr/bin/env python3
"""
ESMA（欧洲证券监管局）IFRS 监管执法案例摘编生成器（L5 实务案例参考，非规范依据）。

数据来源（均为 ESMA 官网免费公开执法报告）：
- ESMA Financial Reporting Enforcement Portal: https://www.esma.europa.eu/issuer-disclosure/financial-reporting
- ESMA 31st Extract & 2026 European Common Enforcement Priorities (ESMA32-2064178921-9265 / -9738, Oct 2026)
- ESMA 29th Extract from the EECS's Database of Enforcement (ESMA32-193237008-8267, May 2024)
"""

from __future__ import annotations

import datetime as dt
import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUT_PATH = PROJECT_ROOT / "intl_data" / "esma_cases.json"

ESMA_PORTAL = "https://www.esma.europa.eu/issuer-disclosure/financial-reporting"
ESMA_ECEP_2026 = "https://www.esma.europa.eu/press-news/esma-news/esma-sets-out-2026-european-common-enforcement-priorities"
ESMA_29TH = "https://www.esma.europa.eu/sites/default/files/2024-05/ESMA32-193237008-8267_29th_Extract_from_the_EECS_s_Database_of_Enforcement.pdf"
ESMA_LIST = "https://www.esma.europa.eu/document/list-decisions-published-extracts-eecss-database-enforcement"


def make_case(
    *,
    code: str,
    title: str,
    display_title: str,
    doc_no: str,
    pub_date: str,
    source_url: str,
    summary: str,
    cited_codes: list[str],
    sections: list[tuple[str, str, str]],
) -> dict:
    articles = [
        {"no": no, "heading": hd, "text": txt, "seq": idx}
        for idx, (no, hd, txt) in enumerate(sections)
    ]
    return {
        "code": code,
        "framework": "INTL",
        "domain": "accounting",
        "doc_type": "case",
        "title": title,
        "display_title": display_title,
        "series_badge": "ESMA Enforcement",
        "doc_no": doc_no,
        "issuer": "ESMA (FRWG / EECS)",
        "pub_date": pub_date,
        "effective_date": pub_date,
        "status": "in_force",
        "version_level": "info",
        "version_note": "Regulatory enforcement reference only (non-authoritative; see official ESMA publication).",
        "source_name": "ESMA",
        "source_url": source_url,
        "source_kind": "official",
        "summary": summary,
        "cited_codes": cited_codes,
        "cas_links": [],
        "articles": articles,
    }


def main() -> int:
    cases = [
        make_case(
            code="ESMA Case: ECEP 2026",
            title="ESMA 2026 European Common Enforcement Priorities — Geopolitical Risks, Restructuring & Debt Restructuring",
            display_title="2026 Common Enforcement Priorities: Geopolitical Risks & Restructuring",
            doc_no="ESMA32-2064178921-9738",
            pub_date="2026-10-13",
            source_url=ESMA_ECEP_2026,
            summary="ESMA's October 2026 enforcement priorities for annual financial reports highlight geopolitical risks and uncertainties, restructuring provisions (IAS 37), debt restructuring/modifications (IFRS 9), and connected sustainability materiality disclosures.",
            cited_codes=["IAS 37", "IFRS 9", "IAS 36", "IFRS S1", "IFRS S2"],
            sections=[
                (
                    "Enforcement Focus",
                    "2026 IFRS & Sustainability Priorities (ESMA32-2064178921-9738)",
                    "[IFRS Financial Statements]\n"
                    "• Geopolitical risks and uncertainties: issuers must transparently reflect macro/geopolitical volatility in impairment assumptions (IAS 36), going concern assessments (IAS 1/IAS 8), and significant judgement disclosures.\n"
                    "• Restructuring provisions (IAS 37.70–83): verify that a detailed formal plan and valid expectation exist at the reporting date before recognising a provision.\n"
                    "• Debt restructuring (IFRS 9.3.3.2 & B3.3.6): rigorously apply the 10% present-value test and qualitative assessment to determine substantial modification vs. extinguishment.\n\n"
                    "[Sustainability & Connected Reporting]\n"
                    "• Ensure consistency between financial statement assumptions and sustainability disclosures (impacts, risks, opportunities, policies, actions, targets, and metrics).\n\n"
                    f"Official ESMA release: {ESMA_ECEP_2026}",
                ),
            ],
        ),
        make_case(
            code="ESMA Case: IFRS 9 ECL",
            title="ESMA EECS Enforcement Decisions — IFRS 9 Expected Credit Loss (Multi-Scenario Macroeconomic Inputs)",
            display_title="EECS Case: IFRS 9 ECL Multi-Scenario Macroeconomic Inputs",
            doc_no="ESMA32-193237008-8267",
            pub_date="2024-05-27",
            source_url=ESMA_29TH,
            summary="National enforcer disagreed with an issuer that omitted forward-looking macroeconomic scenarios from its ECL model, requiring collection of current and projected macroeconomic data across multiple scenarios under IFRS 9.5.5.17(c).",
            cited_codes=["IFRS 9", "IFRS 7"],
            sections=[
                (
                    "Decision Summary",
                    "Forward-Looking Macroeconomic Scenarios in ECL (IFRS 9.5.5.17(c))",
                    "[Issue & Enforcement Decision]\n"
                    "• An issuer estimated expected credit losses relying solely on historical loss rates without incorporating forward-looking macroeconomic factors.\n"
                    "• The enforcer required the issuer to collect current and projected macroeconomic data and incorporate it as actual input data into the ECL estimation using more than one economic scenario.\n\n"
                    "[Regulatory Rationale]\n"
                    "• Under IFRS 9.5.5.17(c), ECL must reflect reasonable and supportable information available without undue cost or effort at the reporting date about past events, current conditions, and forecasts of future economic conditions, evaluated across an unbiased probability-weighted range of outcomes.\n\n"
                    f"Source (ESMA 29th Extract): {ESMA_29TH}",
                ),
            ],
        ),
        make_case(
            code="ESMA Case: IFRS 13 & IAS 40",
            title="ESMA EECS Enforcement Decisions — Fair Value Classes & Rental Yield Ranges for Investment Property",
            display_title="EECS Case: Investment Property Fair Value Classes & Yield Ranges",
            doc_no="ESMA32-193237008-8267",
            pub_date="2024-05-27",
            source_url=ESMA_29TH,
            summary="Enforcer challenged an issuer's overly broad aggregation of investment property classes under IFRS 13 where disclosed rental yield ranges spanned 200–550 bps across separate geography and use dimensions.",
            cited_codes=["IFRS 13", "IAS 40"],
            sections=[
                (
                    "Decision Summary",
                    "Disaggregation of Level 3 Fair Value Inputs (IFRS 13.93(d) & 13.94)",
                    "[Issue & Enforcement Decision]\n"
                    "• The issuer presented Level 3 rental yield ranges separately by geography (6 classes) and by type of use (4 classes), with wide ranges of 200 to 550 basis points within classes.\n"
                    "• The enforcer disagreed with the issuer's determination of classes of investment properties, requiring finer disaggregation so users can evaluate valuation sensitivity meaningfully.\n\n"
                    "[Key Takeaway]\n"
                    "• Under IFRS 13.93(d) and IFRS 13.94, quantitative information about significant unobservable inputs (such as capitalisation rates and rental yields) must be disaggregated by nature, characteristics, and risks—not masked by wide multi-hundred-bps ranges.\n\n"
                    f"Source (ESMA 29th Extract): {ESMA_29TH}",
                ),
            ],
        ),
        make_case(
            code="ESMA Case: IAS 28 Influence",
            title="ESMA EECS Enforcement Decisions — Significant Influence Assessment with 10% Voting Rights (IAS 28)",
            display_title="EECS Case: Significant Influence with <20% Voting Rights (IAS 28)",
            doc_no="ESMA32-193237008-8267",
            pub_date="2024-05-27",
            source_url=ESMA_29TH,
            summary="Enforcer disagreed with an issuer claiming significant influence over an investee where it held only 10% of voting rights and lacked a contractual right to appoint a board representative at the reporting date.",
            cited_codes=["IAS 28", "IFRS 12"],
            sections=[
                (
                    "Decision Summary",
                    "Demonstrating Significant Influence Below 20% (IAS 28.5–6)",
                    "[Issue & Enforcement Decision]\n"
                    "• The issuer held 10% of voting rights in Entity B and had no contractual right to appoint a board director at year-end, arguing only that a representative would be appointed at the next general meeting.\n"
                    "• The enforcer concluded the issuer did NOT have significant influence at the reporting date.\n\n"
                    "[Regulatory Rationale]\n"
                    "• Under IAS 28.5, holdings below 20% are presumed NOT to confer significant influence unless clearly demonstrated by existing facts (board representation, policy participation, material transactions, or interchange of managerial personnel) as of the reporting date.\n\n"
                    f"Source (ESMA 29th Extract): {ESMA_29TH}",
                ),
            ],
        ),
        make_case(
            code="ESMA Case: IAS 24 Related Parties",
            title="ESMA EECS Enforcement Decisions — Scope of Related Party Transfers & Disclosures (IAS 24)",
            display_title="EECS Case: Related Party Resource Transfers & Disclosures (IAS 24)",
            doc_no="ESMA32-193237008-8267",
            pub_date="2024-05-27",
            source_url=ESMA_29TH,
            summary="Enforcer rejected an issuer's view that cash payments to an affiliated entity did not constitute related party transactions, clarifying that IAS 24.9 covers ANY transfer of resources regardless of service provision.",
            cited_codes=["IAS 24"],
            sections=[
                (
                    "Decision Summary",
                    "Broad Definition of Related Party Transaction (IAS 24.9 & IAS 24.18)",
                    "[Issue & Enforcement Decision]\n"
                    "• The issuer omitted disclosure of payments made to an affiliated company, arguing they were not payments for services.\n"
                    "• The enforcer disagreed and required full disclosure under IAS 24.18.\n\n"
                    "[Regulatory Rationale]\n"
                    "• Under IAS 24.9, a related party transaction is ANY transfer of resources, services, or obligations between a reporting entity and a related party, regardless of whether a price is charged.\n\n"
                    f"Source (ESMA 29th Extract): {ESMA_29TH}",
                ),
            ],
        ),
        make_case(
            code="ESMA Case: IAS 36 Impairment",
            title="ESMA EECS Enforcement Decisions — Interim Impairment Triggers, CGU Allocation & Sensitivity Disclosures",
            display_title="EECS Case: Interim Impairment Triggers & Goodwill CGU Disclosures",
            doc_no="ESMA32-193237008-8267",
            pub_date="2024-05-27",
            source_url=ESMA_29TH,
            summary="Compiles recurring ESMA EECS enforcement decisions on interim impairment testing (IAS 34 / IAS 36), goodwill allocation to CGUs, and mandatory sensitivity disclosures when headroom is limited (IAS 36.134(f)).",
            cited_codes=["IAS 36", "IAS 34"],
            sections=[
                (
                    "Decision Summary",
                    "Interim Impairment & Sensitivity Disclosures (IAS 34 & IAS 36.134)",
                    "[Recurring Enforcement Findings]\n"
                    "• Interim reporting (IAS 34.15B & IAS 36.9): significant macroeconomic shifts, market cap below net assets, or revised margin forecasts trigger interim impairment testing and full explanatory note disclosures.\n"
                    "• Reasonably possible changes (IAS 36.134(f)): when headroom is narrow, issuers must quantify the headroom, the value assigned to each key assumption (discount rate, terminal growth rate, EBITDA margin), and the amount by which the assumption must change for recoverable amount to equal carrying amount.\n\n"
                    f"Source (ESMA EECS Database): {ESMA_PORTAL}",
                ),
            ],
        ),
        make_case(
            code="ESMA Case: IFRS 15 Revenue",
            title="ESMA EECS Enforcement Decisions — Revenue Recognition (Principal vs. Agent, Over-Time & Bundled Contracts)",
            display_title="EECS Case: IFRS 15 Principal vs. Agent & Over-Time Judgements",
            doc_no="ESMA-EECS-IFRS15",
            pub_date="2026-10-13",
            source_url=ESMA_LIST,
            summary="Synthesises published ESMA EECS enforcement decisions on IFRS 15 covering gross vs. net principal/agent control assessment (IFRS 15.B34–B38), enforceability of right to payment for over-time revenue (IFRS 15.35(c)), and disaggregation disclosures.",
            cited_codes=["IFRS 15"],
            sections=[
                (
                    "Decision Summary",
                    "Key IFRS 15 Enforcement Hotspots (IFRS 15.35(c) & B34–B38)",
                    "[Recurring Enforcement Findings]\n"
                    "• Principal vs. Agent (IFRS 15.B34–B38): enforcers scrutinise platform, reseller, and software intermediaries claiming gross revenue—control before transfer must be evidenced by primary fulfilment responsibility, inventory risk, and pricing discretion, not merely billing/collection flow.\n"
                    "• Over-time revenue (IFRS 15.35(c)): enforceable right to payment must cover costs plus a reasonable profit margin at all times if terminated by the customer for convenience (merely receiving a deposit is insufficient).\n"
                    "• Significant judgements (IFRS 15.123–126): boilerplate disclosures are challenged; entity-specific judgements on SSP estimation and variable consideration constraints are required.\n\n"
                    f"Official ESMA EECS Decisions Index: {ESMA_LIST}",
                ),
            ],
        ),
        make_case(
            code="ESMA Case: IFRS 16 Leases",
            title="ESMA EECS Enforcement Decisions — Lease Term, Extension Options & Discount Rate Judgements (IFRS 16)",
            display_title="EECS Case: IFRS 16 Lease Term & Extension Option Judgements",
            doc_no="ESMA-EECS-IFRS16",
            pub_date="2026-10-13",
            source_url=ESMA_LIST,
            summary="Synthesises published ESMA EECS enforcement decisions on IFRS 16 focusing on enforceable lease period, broader economics of renewal/termination options (IFRS 16.B34–B40), and incremental borrowing rate (IBR) methodology.",
            cited_codes=["IFRS 16"],
            sections=[
                (
                    "Decision Summary",
                    "Lease Term & Enforceability Judgements (IFRS 16.18–21 & B34–B40)",
                    "[Recurring Enforcement Findings]\n"
                    "• Broader economics (IFRS 16.B34): aligned with the IFRIC Agenda Decision on lease term, entities must consider broader economic penalties (e.g., unamortised leasehold improvements, relocation costs)—not just contractual termination penalties—when determining enforceable period.\n"
                    "• Disclosure of future cash outflows not reflected in lease liabilities (IFRS 16.59(b)): material extension options excluded from the lease term require transparent quantitative disclosure.\n\n"
                    f"Official ESMA EECS Decisions Index: {ESMA_LIST}",
                ),
            ],
        ),
    ]

    payload = {
        "generated_at": dt.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "source": "ESMA (FRWG / EECS Database of Enforcement)",
        "count": len(cases),
        "documents": cases,
    }
    OUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Wrote {OUT_PATH.name}: {len(cases)} ESMA enforcement case compilations")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
