#!/usr/bin/env python3
"""
为高频核心 IFRS 国际会计准则补充「官方段落号索引的深度技术精要」（公开合规原创技术拆解）。

说明：
- 严格遵循公开合规边界：不搬运 IFRS Foundation 受版权保护的逐字原文，而是按官方真实章节与段落号
  （如 IFRS 15.9–21、IFRS 15.B34–B38、IFRS 18.117–125、IAS 36.109–125）编写结构化英文技术要点
  与 CAS vs. IFRS 实务差异对照；
- 幂等写入 intl_data/ifrs_accounting.json（插在 Overview 之后、History 之前，重复运行不会产生重复章节）。
"""

from __future__ import annotations

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
IFRS_JSON = PROJECT_ROOT / "intl_data" / "ifrs_accounting.json"


TECHNICAL_MODULES: dict[str, list[tuple[str, str, str]]] = {
    "IFRS 15": [
        (
            "IFRS 15.1–8",
            "Objective & Scope",
            "Core principle (IFRS 15.2): recognise revenue to depict the transfer of promised goods or services to customers in an amount reflecting the consideration to which the entity expects to be entitled.\n\n"
            "[Scope Exclusions (IFRS 15.5–8)]\n"
            "• Lease contracts within IFRS 16 Leases\n"
            "• Insurance contracts within IFRS 17 Insurance Contracts\n"
            "• Financial instruments and other contractual rights/obligations within IFRS 9, IFRS 10, IFRS 11, IAS 27, and IAS 28\n"
            "• Non-monetary exchanges between entities in the same line of business to facilitate sales to customers\n"
            "• Partially in-scope contracts (IFRS 15.7): apply separation/measurement rules of other standards first, then apply IFRS 15 to the remainder.",
        ),
        (
            "IFRS 15.9–21",
            "Step 1: Identifying the Contract & Contract Modifications",
            "[Five Cumulative Contract Criteria (IFRS 15.9)]\n"
            "• Parties have approved the contract and are committed to perform their respective obligations\n"
            "• Each party's rights regarding goods or services to be transferred can be identified\n"
            "• Payment terms for the goods or services can be identified\n"
            "• Contract has commercial substance (risk, timing, or amount of future cash flows expected to change)\n"
            "• Collection of consideration is probable (evaluated considering customer's ability and intention to pay when due)\n\n"
            "[Combination & Modifications (IFRS 15.17–21)]\n"
            "• Combine two or more contracts entered into at or near the same time with the same customer if negotiated as a package with a single commercial objective, consideration depends on another contract, or goods/services form a single performance obligation (IFRS 15.17).\n"
            "• Account for a contract modification as a separate contract when it adds distinct goods/services at their stand-alone selling prices (IFRS 15.20).\n"
            "• Otherwise account prospectively (termination of old contract + creation of new contract) if remaining goods/services are distinct, or via cumulative catch-up adjustment if remaining goods/services are not distinct (IFRS 15.21).",
        ),
        (
            "IFRS 15.22–30",
            "Step 2: Identifying Performance Obligations",
            "At contract inception, assess promised goods or services and identify each distinct good or service (or a series of distinct goods/services that are substantially the same with the same pattern of transfer, IFRS 15.22–23).\n\n"
            "[Two-Step Distinctness Test (IFRS 15.27–29)]\n"
            "• Capable of being distinct (IFRS 15.27(a)): the customer can benefit from the good or service either on its own or together with other readily available resources.\n"
            "• Distinct within the context of the contract (IFRS 15.27(b) & 15.29): the promise to transfer the good or service is separately identifiable from other promises—indicators of NOT separately identifiable include significant integration service, significant modification/customisation, or high interdependence/interrelation.",
        ),
        (
            "IFRS 15.46–72",
            "Step 3: Determining the Transaction Price",
            "Transaction price is the amount of consideration an entity expects to be entitled to in exchange for transferring promised goods or services, excluding amounts collected on behalf of third parties such as sales taxes/VAT (IFRS 15.47).\n\n"
            "[Key Measurement Components]\n"
            "• Variable consideration (IFRS 15.50–59): estimate discounts, rebates, refunds, credits, performance bonuses, or penalties using expected value or most likely amount; include only to the extent it is highly probable that a significant reversal in cumulative revenue will not occur (the variable consideration constraint, IFRS 15.56).\n"
            "• Significant financing component (IFRS 15.60–65): adjust consideration for the time value of money when timing provides a significant financing benefit; practical expedient allows ignoring financing if the gap between transfer and payment is one year or less (IFRS 15.63).\n"
            "• Non-cash consideration (IFRS 15.66–69): measure at fair value (or indirectly by reference to stand-alone selling price of promised goods/services).\n"
            "• Consideration payable to a customer (IFRS 15.70–72): reduce transaction price unless the payment is for a distinct good or service received from the customer.",
        ),
        (
            "IFRS 15.73–90",
            "Step 4: Allocating the Transaction Price",
            "Allocate the transaction price to each performance obligation in proportion to its relative stand-alone selling price (SSP) determined at contract inception (IFRS 15.73–76).\n\n"
            "[Estimating Stand-Alone Selling Price (IFRS 15.78–79)]\n"
            "• Observable price when sold separately in similar circumstances is the best evidence (IFRS 15.77).\n"
            "• If not directly observable, estimate using: Adjusted market assessment approach, Expected cost plus a margin approach, or Residual approach (permitted only when SSP is highly variable or uncertain, IFRS 15.79(c)).\n"
            "• Discounts (IFRS 15.81–83) and variable consideration (IFRS 15.84–86) are allocated proportionately to all performance obligations unless specific criteria show they relate entirely to one or more specific obligations.",
        ),
        (
            "IFRS 15.31–45",
            "Step 5: Satisfying Performance Obligations (Over Time vs. Point in Time)",
            "Recognise revenue when (or as) the entity satisfies a performance obligation by transferring control of a promised good or service to the customer (IFRS 15.31–33).\n\n"
            "[Over-Time Recognition — Any ONE of Three Criteria (IFRS 15.35)]\n"
            "• (a) Customer simultaneously receives and consumes the benefits as the entity performs (e.g., routine cleaning/security services);\n"
            "• (b) Entity's performance creates or enhances an asset that the customer controls as it is created or enhanced (e.g., building on customer's land);\n"
            "• (c) Entity's performance does not create an asset with an alternative use to the entity AND the entity has an enforceable right to payment for performance completed to date (IFRS 15.35(c), 15.36–37).\n"
            "• Progress measurement (IFRS 15.39–45): select a single output or input method per obligation that faithfully depicts performance; exclude uninstalled materials or wasted inputs from cost-to-cost progress.\n\n"
            "[Point-in-Time Control Transfer Indicators (IFRS 15.38)]\n"
            "• Entity has a present right to payment; customer has legal title; entity has transferred physical possession; customer has significant risks and rewards of ownership; customer has accepted the asset.",
        ),
        (
            "IFRS 15.91–104",
            "Contract Costs (Acquisition & Fulfilment)",
            "• Incremental costs of obtaining a contract (IFRS 15.91–94): capitalise costs that would not have been incurred if the contract had not been obtained (e.g., sales commissions) if expected to be recovered. Practical expedient: expense immediately if the amortisation period is one year or less (IFRS 15.94).\n"
            "• Costs to fulfil a contract (IFRS 15.95–98): if not within IAS 2, IAS 16, or IAS 38, capitalise only when costs relate directly to a contract, generate or enhance resources used in satisfying future obligations, and are expected to be recovered. General/administrative costs and wasted materials are expensed as incurred.\n"
            "• Amortisation & impairment (IFRS 15.99–104): amortise on a systematic basis consistent with the transfer of related goods/services; recognise impairment if carrying amount exceeds remaining expected consideration minus directly related remaining costs.",
        ),
        (
            "IFRS 15.105–129",
            "Presentation & Disclosures",
            "• Statement of financial position presentation (IFRS 15.105–109): present a contract liability when payment is received (or unconditional right to payment arises) before transfer; present a contract asset when performance precedes unconditional right to consideration; present a receivable (under IFRS 9) when the right to consideration is unconditional (only passage of time required).\n"
            "• Core disclosures (IFRS 15.110–129): disaggregation of revenue by economic factors; contract balances and revenue recognised from opening contract liabilities; remaining performance obligations (transaction price allocated and expected timing of recognition, IFRS 15.120); significant judgements on timing, transaction price, and SSP; capitalised contract costs.",
        ),
        (
            "IFRS 15.B1–B89",
            "Key Application Guidance (Appendix B Hot Topics)",
            "• Principal vs. Agent (IFRS 15.B34–B38): an entity is a principal (gross revenue) if it controls the specified good/service before transfer to the customer; control indicators include primary responsibility for fulfilment, inventory risk, and discretion in establishing prices (B37). Otherwise it is an agent (net fee/commission).\n"
            "• Sale with a right of return (IFRS 15.B20–B27): recognise revenue for expected retained goods, a refund liability for expected returns, and a right-of-return asset (adjusted for recovery costs).\n"
            "• Warranties (IFRS 15.B28–B33): assurance-type warranties are accounted for under IAS 37; service-type warranties (customer has option to purchase separately or warranty provides an additional service) are a separate performance obligation.\n"
            "• Customer options for additional goods/services (IFRS 15.B39–B43): if the option provides a material right (e.g., loyalty points, volume renewal discounts), allocate transaction price to the material right.\n"
            "• Breakage / unexercised rights (IFRS 15.B44–B47): recognise expected breakage proportionately as customers exercise rights (if entitled), otherwise when likelihood of exercise becomes remote.\n"
            "• Licensing of intellectual property (IFRS 15.B52–B63B): right to access IP (over time) vs. right to use IP (point in time); sales- or usage-based royalties exception (B63) recognises revenue only when the subsequent sale/usage occurs.\n"
            "• Repurchase agreements (IFRS 15.B64–B76): forwards and call options are accounted for as a lease (IFRS 16) or financing arrangement, not a sale; put options depend on whether customer has a significant economic incentive to exercise.\n"
            "• Consignment & bill-and-hold (IFRS 15.B77–B82): bill-and-hold requires substantive reason, separate identification, readiness for physical transfer, and inability of seller to redirect the product.",
        ),
        (
            "CAS 14 vs IFRS 15",
            "Cross-Framework Practical Comparison (China CAS 14 vs. IFRS 15)",
            "China CAS 14 (2017 Revision) is substantially converged with IFRS 15 in its five-step model, over-time vs. point-in-time criteria, principal vs. agent assessment, and contract cost rules.\n\n"
            "[Key Practical Nuances to Watch]\n"
            "• Terminology & mapping: IFRS 15.35 corresponds directly to CAS 14 Art. 11; IFRS 15.B34–B38 (Principal vs. Agent) corresponds to CAS 14 Art. 34 and MOF Revenue Implementation Q&As.\n"
            "• Assurance-type warranty classification: under CAS (MOF Interpretation No. 18, 2024), assurance-type warranty expense is presented in Cost of Sales rather than Selling Expenses; under IFRS 18/IAS 1 it depends on nature/function classification.\n"
            "• Disclosure granularity: IFRS 15.110–129 mandates quantitative disclosure of remaining performance obligations (backlog) and detailed contract balance roll-forwards, which listed entities reporting under IFRS must maintain beyond basic CAS statutory notes.",
        ),
    ],
    "IFRS 16": [
        (
            "IFRS 16.9–21",
            "Identifying a Lease, Separating Components & Lease Term",
            "A contract is (or contains) a lease if it conveys the right to control the use of an identified asset for a period of time in exchange for consideration (IFRS 16.9, B9–B31).\n\n"
            "[Control Test & Lease Term]\n"
            "• Control requires BOTH: (a) right to obtain substantially all economic benefits from use of the identified asset, and (b) right to direct the use of the identified asset (no substantive substitution right by supplier, IFRS 16.B14–B19).\n"
            "• Separating components (IFRS 16.12–16): lessees allocate consideration to lease and non-lease components based on relative stand-alone prices, unless electing the practical expedient by class of underlying asset to account for them as a single lease component (IFRS 16.15).\n"
            "• Lease term (IFRS 16.18–21): non-cancellable period plus periods covered by an option to extend (if reasonably certain to exercise) or an option to terminate (if reasonably certain NOT to exercise).",
        ),
        (
            "IFRS 16.22–46",
            "Lessee Accounting: ROU Asset, Lease Liability & Modifications",
            "Single on-balance-sheet lessee model (IFRS 16.22): recognise a right-of-use (ROU) asset and a lease liability at commencement date.\n\n"
            "[Recognition Exemptions (IFRS 16.5–8)]\n"
            "• Short-term leases (lease term ≤ 12 months with no purchase option, by asset class) and leases of low-value assets (e.g., tablets, small IT equipment, on a lease-by-lease basis) may be expensed straight-line.\n\n"
            "[Measurement & Subsequent Accounting]\n"
            "• Lease liability (IFRS 16.26–28): present value of unpaid lease payments (fixed payments, index/rate-based variable payments, residual value guarantees, reasonably certain purchase/termination options) discounted at the interest rate implicit in the lease or lessee's incremental borrowing rate (IBR).\n"
            "• ROU asset (IFRS 16.23–25): initial lease liability + prepayments + initial direct costs + estimated restoration costs (IAS 37) − lease incentives received; depreciated under IAS 16 and tested for impairment under IAS 36.\n"
            "• Lease modifications (IFRS 16.44–46): separate lease if adding right to use one or more assets at stand-alone price; otherwise remeasure lease liability with revised discount rate and adjust ROU asset (recognising P&L gain/loss for scope decreases).",
        ),
        (
            "IFRS 16.61–103",
            "Lessor Accounting & Sale-and-Leaseback Transactions",
            "• Dual lessor model (IFRS 16.61–66): classify each lease as a finance lease (transfers substantially all risks and rewards incidental to ownership) or an operating lease.\n"
            "• Finance lessor (IFRS 16.67–78): derecognise underlying asset, recognise net investment in the lease receivable, and recognise finance income over the lease term.\n"
            "• Operating lessor (IFRS 16.81–87): keep asset on balance sheet and recognise lease income on a straight-line (or other systematic) basis.\n"
            "• Sale and leaseback (IFRS 16.98–103): apply IFRS 15 to test whether transfer is a sale. If a sale, seller-lessee measures ROU asset at the proportion of previous carrying amount retained and recognises gain/loss ONLY for rights transferred to the buyer-lessor (amended 2022 for variable lease payments in 16.102A). If not a sale, account as a financial liability under IFRS 9.",
        ),
        (
            "CAS 21 vs IFRS 16",
            "Cross-Framework Practical Comparison (China CAS 21 vs. IFRS 16)",
            "China CAS 21 (2018 Revision) is closely converged with IFRS 16 (single lessee balance-sheet model, dual lessor model, and IFRS 15-linked sale-and-leaseback test).\n"
            "• Low-value asset threshold: IFRS 16 Basis for Conclusions cites USD 5,000 as a reference benchmark; China CAS 21 Application Guidance commonly references RMB 40,000 for brand-new underlying assets.\n"
            "• Variable leaseback payments: IFRS 16.102A (effective 1 Jan 2024) explicitly prevents seller-lessees from recognising gains on retained rights for variable lease payments.",
        ),
    ],
    "IFRS 9": [
        (
            "IFRS 9.4.1–4.3",
            "Classification & Measurement (Business Model & SPPI Test)",
            "Financial assets are classified into Amortised Cost, FVOCI, or FVTPL based on TWO tests (IFRS 9.4.1.1–4.1.5):\n"
            "• Business Model Test (IFRS 9.B4.1.1–B4.1.6): Hold to Collect (HTC), Hold to Collect and Sell (HTC&S), or Other (trading/fair value managed).\n"
            "• Contractual Cash Flow Characteristics Test — SPPI (IFRS 9.4.1.2(b), B4.1.7–B4.1.26): cash flows are Solely Payments of Principal and Interest on principal outstanding (amended May 2024 for ESG-linked features effective 1 Jan 2026).\n"
            "• Debt instruments: HTC + SPPI → Amortised Cost; HTC&S + SPPI → FVOCI (with P&L recycling on derecognition); otherwise FVTPL.\n"
            "• Equity instruments: default FVTPL, with an irrevocable election at initial recognition for non-held-for-trading equities to present fair value changes in OCI with NO recycling to P&L (dividends recognised in P&L, IFRS 9.5.7.5–5.7.6).\n"
            "• Financial liabilities (IFRS 9.4.2.1): generally Amortised Cost; for FVTPL-designated liabilities, own credit risk changes are presented in OCI (IFRS 9.5.7.7).",
        ),
        (
            "IFRS 9.5.5",
            "Expected Credit Loss (ECL) Impairment Model",
            "Forward-looking Expected Credit Loss model applies to debt assets at Amortised Cost / FVOCI, lease receivables, contract assets (IFRS 15), and loan commitments / financial guarantee contracts (IFRS 9.5.5.1).\n\n"
            "[Three-Stage General Approach (IFRS 9.5.5.3–5.5.14)]\n"
            "• Stage 1 (No significant increase in credit risk — SICR): recognise 12-month ECL; interest revenue on gross carrying amount.\n"
            "• Stage 2 (SICR since initial recognition, rebuttable presumption at >30 days past due): recognise lifetime ECL; interest revenue still on gross carrying amount.\n"
            "• Stage 3 (Credit-impaired): recognise lifetime ECL; interest revenue calculated on net carrying amount (gross minus loss allowance).\n"
            "• Simplified approach (IFRS 9.5.5.15): mandatory (or permitted) lifetime ECL from day one for trade receivables and IFRS 15 contract assets without a significant financing component (often via a provision matrix).",
        ),
        (
            "IFRS 9.3.2–3.3 & 6",
            "Derecognition & Hedge Accounting",
            "• Financial asset derecognition (IFRS 9.3.2.3–3.2.6): derecognise when contractual rights to cash flows expire, or rights are transferred and substantially all risks and rewards are transferred (or control is not retained). Financial liability derecognition (IFRS 9.3.3.1–3.3.2): extinguish when discharged/cancelled/expired or modified substantially (10% present-value test, B3.3.6).\n"
            "• Hedge accounting (IFRS 9.6.1–6.7): three hedge types—Fair Value Hedge, Cash Flow Hedge, and Hedge of a Net Investment in a Foreign Operation. Effectiveness requires an economic relationship, credit risk not dominating value changes, and hedge ratio aligned with risk management (removing IAS 39's 80–125% bright line).",
        ),
        (
            "CAS 22–24 vs IFRS 9",
            "Cross-Framework Practical Comparison (China CAS 22/23/24 vs. IFRS 9)",
            "China split IFRS 9 into three standards—CAS 22 (Recognition & Measurement), CAS 23 (Transfer of Financial Assets), and CAS 24 (Hedge Accounting)—which are substantially converged with IFRS 9.\n"
            "• 2024 IFRS 9 amendments (effective 1 Jan 2026) clarify electronic cash settlement derecognition (IFRS 9.B3.1.2A) and SPPI assessment for ESG-linked/contingent features—entities dual-reporting under IFRS and CAS should track MOF follow-up interpretations.",
        ),
    ],
    "IFRS 18": [
        (
            "IFRS 18.46–74",
            "New Profit or Loss Structure: Five Categories & Mandatory Subtotals",
            "Effective for annual reporting periods beginning on or after 1 January 2027, IFRS 18 replaces IAS 1 and introduces a standardised Statement of Profit or Loss structure.\n\n"
            "[Five Income & Expense Categories (IFRS 18.47)]\n"
            "• Operating category (residual category capturing main business activities not classified elsewhere)\n"
            "• Investing category (returns from investments generating returns individually and largely independently, associates/JVs, cash & cash equivalents)\n"
            "• Financing category (income/expenses on liabilities arising from transactions involving only the raising of finance, plus interest on other liabilities such as lease/pension liabilities)\n"
            "• Income taxes category (IAS 12) and Discontinued operations category (IFRS 5)\n\n"
            "[Two New Mandatory Subtotals (IFRS 18.69)]\n"
            "• Operating profit or loss\n"
            "• Profit or loss before financing and income taxes (unless entity provides financing to customers as a specified main business activity, IFRS 18.73).",
        ),
        (
            "IFRS 18.49–64",
            "Specified Main Business Activities (Banks, Insurers & Investment Entities)",
            "Entities must assess whether they have a 'specified main business activity' of (a) investing in assets (e.g., investment property companies, insurers) or (b) providing financing to customers (e.g., banks, leasing/captive finance entities) (IFRS 18.49–51).\n"
            "• When applicable, income and expenses that would otherwise sit in the Investing or Financing categories (such as interest income/expense on customer loans or investment property fair value gains) are classified in the Operating category so Operating Profit reflects core business performance.",
        ),
        (
            "IFRS 18.117–125",
            "Management-Defined Performance Measures (MPMs)",
            "MPMs are subtotals of income and expenses used in public communications outside financial statements to communicate management's view of an aspect of financial performance, that are not listed by IFRS 18 or specifically required by another IFRS standard (e.g., 'Adjusted EBITDA', 'Adjusted Operating Profit') (IFRS 18.117–118).\n\n"
            "[Single-Note MPM Disclosure Requirements (IFRS 18.121–123)]\n"
            "• Statement that the MPM reflects management's view and is not necessarily comparable across entities\n"
            "• Description of why the MPM provides useful information and how it is calculated\n"
            "• Quantitative reconciliation between each MPM and the most directly comparable IFRS subtotal, showing the income tax effect and NCI effect for each reconciling item (subject to audit!).",
        ),
        (
            "IFRS 18.41–43 & 78–83",
            "Aggregation, Disaggregation & Operating Expense Analysis",
            "• Enhanced aggregation/disaggregation principles (IFRS 18.41–43, B16–B28): group items with shared characteristics; disaggregate items with dissimilar characteristics whenever material; avoid opaque 'Other' labels.\n"
            "• Operating expenses (IFRS 18.78–83): present by nature, by function, or a mixed presentation—whichever gives the most useful structured summary. If ANY operating expenses are presented by function (e.g., Cost of Sales), entities MUST disclose in a single note the specified totals for depreciation, amortisation, employee benefits, impairment losses/reversals, and inventory write-downs (IFRS 18.83).",
        ),
        (
            "IAS 1 / CAS 30 vs IFRS 18",
            "Transition Impact vs. IAS 1 & China CAS 30",
            "• Compared to IAS 1: IFRS 18 brings Operating Profit comparability, brings non-GAAP MPMs inside audited notes, and amends IAS 7 (using Operating Profit as the sole starting point for indirect-method operating cash flows and removing dividend/interest classification options for non-financial entities).\n"
            "• Compared to China CAS 30: China's income statement already mandates an 'Operating Profit (营业利润)' subtotal, but CAS 30 includes investment income (投资收益) inside Operating Profit and does not yet require audited MPM reconciliations.",
        ),
    ],
    "IFRS 3": [
        (
            "IFRS 3.4–36",
            "Acquisition Method, Concentration Test & Goodwill",
            "• Business vs. Asset Acquisition (IFRS 3.B5–B12D): a business requires at minimum an input and a substantive process that together significantly contribute to the ability to create outputs. Optional Concentration Test (B7B): if substantially all fair value of gross assets acquired is concentrated in a single identifiable asset (or group of similar assets), the transaction is an asset acquisition.\n"
            "• Four-step Acquisition Method (IFRS 3.5): (1) identify acquirer; (2) determine acquisition date; (3) recognise and measure identifiable assets acquired, liabilities assumed, and any NCI (at fair value or proportionate share of net identifiable assets, IFRS 3.19); (4) recognise goodwill or a bargain purchase gain (IFRS 3.32–36).\n"
            "• Acquisition-related costs (IFRS 3.53): advisory, legal, and valuation fees are expensed as incurred (not capitalised into goodwill).",
        ),
        (
            "IFRS 3.39–58 & CAS 20",
            "Contingent Consideration, Step Acquisitions & CAS 20 Comparison",
            "• Contingent consideration (IFRS 3.39–40, 58): recognised at acquisition-date fair value; subsequent fair value changes of liability-classified earn-outs are recognised in P&L.\n"
            "• Step acquisitions (IFRS 3.41–42): remeasure previously held equity interest to acquisition-date fair value and recognise gain/loss in P&L (or OCI if FVOCI equity).\n"
            "• Key CAS 20 vs. IFRS 3 difference: IFRS 3 explicitly scopes out business combinations under common control (IFRS 3.2(c)); China CAS 20 provides explicit book-value predecessor accounting rules for common-control combinations (同一控制下企业合并).",
        ),
    ],
    "IFRS 10": [
        (
            "IFRS 10.5–33",
            "Single Control Model, De Facto Control & Investment Entities",
            "An investor controls an investee when it has ALL THREE elements (IFRS 10.7):\n"
            "• (a) Power over the investee (existing rights giving current ability to direct the relevant activities, IFRS 10.10–14);\n"
            "• (b) Exposure, or rights, to variable returns from involvement with the investee (IFRS 10.15–16); and\n"
            "• (c) Ability to use its power over the investee to affect the amount of the investor's returns (principal vs. agent test, IFRS 10.17–18, B58–B72).\n\n"
            "[Practical Hotspots]\n"
            "• De facto control (IFRS 10.B41–B46): an investor holding <50% voting rights can still have power depending on relative size of holding and dispersion of other vote holders.\n"
            "• Investment entities exception (IFRS 10.27–33): qualifying investment entities measure subsidiaries at FVTPL under IFRS 9 instead of consolidating (converged in China CAS 33 Art. 21).",
        ),
    ],
    "IAS 36": [
        (
            "IAS 36.8–57",
            "Impairment Indicators, Annual Testing & Recoverable Amount",
            "• Impairment triggers (IAS 36.9–14): assess at each reporting date whether internal or external indicators of impairment exist.\n"
            "• Mandatory annual impairment test regardless of indicators (IAS 36.10): (a) intangible assets with indefinite useful lives, (b) intangible assets not yet available for use, and (c) goodwill acquired in a business combination.\n"
            "• Recoverable amount (IAS 36.18–57): higher of Fair Value Less Costs of Disposal (FVLCD, per IFRS 13) and Value in Use (VIU — present value of future pre-tax cash flows expected from continuing use and disposal, excluding uncommitted future restructurings or asset enhancements under IAS 36.44).",
        ),
        (
            "IAS 36.65–125 & CAS 8",
            "CGUs, Goodwill Allocation & Impairment Reversal (vs. CAS 8)",
            "• Cash-Generating Units — CGUs (IAS 36.66–108): smallest identifiable group of assets generating largely independent cash inflows; goodwill is allocated to CGUs/groups of CGUs not larger than an operating segment (IFRS 8). CGU impairment losses reduce goodwill FIRST, then other CGU assets pro rata (IAS 36.104).\n"
            "• Reversal of impairment losses (IAS 36.109–125): permitted (and required if estimates change) for assets OTHER than goodwill, capped at depreciated historical cost; reversal of goodwill impairment is STRICTLY PROHIBITED (IAS 36.124).\n"
            "• Major CAS 8 vs. IAS 36 difference: China CAS 8 Art. 17 prohibits reversal of impairment losses for ALL long-term assets within its scope (PPE, intangibles, investment property at cost, goodwill), whereas IAS 36 permits reversal for non-goodwill long-term assets.",
        ),
    ],
    "IAS 12": [
        (
            "IAS 12.15–56",
            "Deferred Tax Recognition, Initial Recognition Exemption & Measurement",
            "Balance-sheet liability method (IAS 12.15–36): recognise deferred tax liabilities (DTL) for all taxable temporary differences and deferred tax assets (DTA) for deductible temporary differences, unused tax losses, and tax credits to the extent probable future taxable profit will be available.\n\n"
            "[Initial Recognition Exemption & 2021 Single-Transaction Amendment (IAS 12.15(b), 24)]\n"
            "• DTL/DTA is not recognised on initial recognition of goodwill, or of an asset/liability in a non-business-combination transaction that affects neither accounting profit nor taxable profit AND does NOT give rise to equal taxable and deductible temporary differences (so leases under IFRS 16 and decommissioning provisions under IAS 37 DO recognise gross DTA and DTL).\n"
            "• Measurement (IAS 12.46–56): use tax rates enacted or substantively enacted by the reporting date; deferred tax assets and liabilities are NEVER discounted (IAS 12.53).",
        ),
        (
            "IAS 12.4A & 88A–88D",
            "OECD Pillar Two (GloBE) Temporary Exception & CAS 18 Comparison",
            "• Pillar Two amendments (IAS 12.4A, 88A–88D): mandatory temporary exception from recognising and disclosing deferred taxes arising from OECD Pillar Two (15% global minimum tax) legislation; entities must separately disclose current tax expense related to Pillar Two top-up taxes and qualitative/quantitative exposure prior to enactment.\n"
            "• CAS 18 convergence: China MOF Interpretation No. 16 aligned single-transaction deferred tax (leases/decommissioning) with IAS 12; multinational groups subject to GloBE rules should reconcile IAS 12.88A disclosures with domestic tax filings.",
        ),
    ],
    "IAS 37": [
        (
            "IAS 37.14–83",
            "Provisions, Measurement, Onerous Contracts & Contingencies",
            "• Three cumulative recognition criteria for a provision (IAS 37.14): (1) present obligation (legal or constructive) from a past event; (2) probable (>50%) outflow of economic resources; and (3) reliable estimate of the obligation.\n"
            "• Measurement (IAS 37.36–52): best estimate of expenditure required to settle at reporting date (expected value for large populations; most likely outcome for a single obligation), discounted at a pre-tax risk-adjusted rate when time value is material. Reimbursements are recognised as a separate asset only when virtually certain (IAS 37.53).\n"
            "• Onerous contracts (IAS 37.66–69): unavoidable costs include both incremental costs and an allocation of other directly related costs (2020 amendment, 37.68A).\n"
            "• Contingent liabilities (IAS 37.27–30) are disclosed unless remote; contingent assets (IAS 37.31–35) are disclosed when probable and recognised only when virtually certain (converged with China CAS 13).",
        ),
    ],
    "IAS 38": [
        (
            "IAS 38.8–111 & CAS 6",
            "Intangibles, R&D Capitalisation & Revaluation Model (vs. CAS 6)",
            "• Recognition (IAS 38.8–24): identifiable (separable or arising from contractual/legal rights), controlled by the entity, with probable future economic benefits and reliably measurable cost.\n"
            "• Internally generated intangibles (IAS 38.51–67): research phase expenditure is ALWAYS expensed as incurred (IAS 38.54); development phase expenditure MUST be capitalised when all 6 criteria in IAS 38.57 are demonstrated (technical feasibility, intention to complete, ability to use/sell, probable future economic benefits, availability of resources, reliable measurement). Internally generated goodwill, brands, and customer lists cannot be recognised (IAS 38.48, 63).\n"
            "• Subsequent measurement (IAS 38.72–111): Cost Model or Revaluation Model (revaluation only if an active market exists); finite-life assets are amortised systematically, while indefinite-life assets are NOT amortised and are tested annually for impairment under IAS 36.\n"
            "• Major CAS 6 vs. IAS 38 difference: China CAS 6 only permits the Cost Model for intangible assets (no Revaluation Model).",
        ),
    ],
}


def main() -> int:
    data = json.loads(IFRS_JSON.read_text(encoding="utf-8"))
    enriched_docs = 0
    inserted_sections = 0

    for d in data["documents"]:
        code = d.get("code", "")
        if code not in TECHNICAL_MODULES:
            continue
        modules = TECHNICAL_MODULES[code]
        mod_nos = {m[0] for m in modules}

        # 幂等去重：保留原有非本次技术拆解的章节，把深度技术模块插入 Overview 之后
        base_arts = [a for a in d.get("articles", []) if a.get("no") not in mod_nos]
        overview_arts = [a for a in base_arts if a.get("no") == "Overview"]
        rest_arts = [a for a in base_arts if a.get("no") != "Overview"]

        new_tech_arts = [
            {"no": no, "heading": heading, "text": text, "seq": 0}
            for no, heading, text in modules
        ]
        merged = overview_arts + new_tech_arts + rest_arts
        for idx, art in enumerate(merged):
            art["seq"] = idx
        d["articles"] = merged
        enriched_docs += 1
        inserted_sections += len(new_tech_arts)

    IFRS_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Enriched {enriched_docs} flagship IFRS standards with {inserted_sections} paragraph-indexed technical sections.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
