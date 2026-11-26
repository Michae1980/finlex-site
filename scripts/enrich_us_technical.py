#!/usr/bin/env python3
"""
为高频核心 US GAAP 美国会计准则补充「FASB ASC 官方小节号索引的深度技术精要」（公开合规原创技术拆解）。

说明：
- 严格遵循公开合规边界：不搬运 FASB Accounting Standards Codification 受版权保护的逐字原文，
  而是按官方真实 Topic-Subtopic-Section-Paragraph 编号（如 ASC 606-10-25、ASC 606-10-32、
  ASC 606-10-55、ASC 842-20-25、ASC 326-20-30 等）编写结构化英文技术精要与中美欧三方实务差异对照；
- 幂等写入 intl_data/us_gaap_accounting.json（保留 Overview 与 Official Access，
  并用结构化多章节深度技术精要替换原本单条精简摘要，重复运行不会产生重复章节）。
"""

from __future__ import annotations

import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
US_GAAP_JSON = PROJECT_ROOT / "intl_data" / "us_gaap_accounting.json"


TECHNICAL_MODULES: dict[str, list[tuple[str, str, str]]] = {
    "ASC 606": [
        (
            "ASC 606-10-05 / 15",
            "Core Principle, Scope Exclusions & Companion Topics",
            "Core principle (ASC 606-10-05-3 / 10-2): recognize revenue to depict the transfer of promised goods or services to customers in an amount that reflects the consideration to which the entity expects to be entitled in exchange for those goods or services.\n\n"
            "[Scope Exclusions (ASC 606-10-15-2)]\n"
            "• Lease contracts within ASC 842 Leases\n"
            "• Insurance contracts within ASC 944 Financial Services — Insurance\n"
            "• Financial instruments and other contractual rights/obligations within ASC 310, 320, 321, 323, 326, 460, 815, 825, and 860\n"
            "• Guarantees (other than product or service warranties) within ASC 460\n"
            "• Nonmonetary exchanges between entities in the same line of business to facilitate sales to customers (ASC 845)\n"
            "• Companion US GAAP Topics: incremental costs of obtaining/fulfilling customer contracts sit in ASC 340-40 (NOT inside ASC 606); sales of nonfinancial assets to non-customers sit in ASC 610-20.",
        ),
        (
            "ASC 606-10-25-1~13",
            "Step 1: Identifying the Contract, Collectibility & Contract Modifications",
            "[Five Cumulative Contract Criteria (ASC 606-10-25-1)]\n"
            "• (a) Parties have approved the contract (written, oral, or implied by customary business practices) and are committed to perform\n"
            "• (b) Each party's rights regarding goods or services to be transferred can be identified\n"
            "• (c) Payment terms for the goods or services can be identified\n"
            "• (d) Contract has commercial substance (risk, timing, or amount of future cash flows expected to change)\n"
            "• (e) Collectibility is PROBABLE — under US GAAP (ASC 450 convention), 'probable' means likely to occur (~75%–80%+ in practice), evaluated only for the consideration the entity expects to be entitled to (after implied price concessions).\n\n"
            "[Failed Collectibility (ASC 606-10-25-7)]\n"
            "• Cash received before Step 1 is met is recorded as a deposit liability; recognize revenue only when (i) no remaining obligations and substantially all consideration is received and nonrefundable, (ii) contract is terminated and consideration is nonrefundable, or (iii) control transferred, transfer ceased, and consideration is nonrefundable (ASC 606-10-25-7(c), unique US GAAP clarification).\n\n"
            "[Contract Combination & Modifications (ASC 606-10-25-9~13)]\n"
            "• Combine contracts entered into at or near the same time with the same customer (or related parties) when negotiated as a single commercial package, interdependent in price, or forming a single performance obligation.\n"
            "• Modifications: (1) Separate contract if adding distinct goods/services at SSP (25-12); (2) Prospective termination/new contract if remaining goods/services are distinct (25-13(a)); (3) Cumulative catch-up if remaining goods/services are NOT distinct (25-13(b)).",
        ),
        (
            "ASC 606-10-25-14~22",
            "Step 2: Identifying Performance Obligations & Shipping/Handling Election",
            "Identify each promise to transfer either (a) a distinct good or service (or bundle), or (b) a series of distinct goods or services that are substantially the same and have the same pattern of transfer (ASC 606-10-25-14~15).\n\n"
            "[Two-Step Distinctness Test (ASC 606-10-25-19~21)]\n"
            "• Capable of being distinct (25-19(a)): customer can benefit from the good/service on its own or with other readily available resources.\n"
            "• Distinct within the context of the contract (25-19(b) & 25-21): separately identifiable from other promises — indicators of NOT separately identifiable include significant integration service, significant modification/customization, or high interdependence/interrelation.\n\n"
            "[US GAAP-Specific Practical Expedients]\n"
            "• Immaterial Promises (ASC 606-10-25-16A): Entities need NOT assess whether promised goods/services are performance obligations if they are immaterial in the context of the contract.\n"
            "• Shipping & Handling Activities (ASC 606-10-25-18B): Entities may make an accounting policy election to treat shipping and handling performed AFTER the customer obtains control of the good as a FULFILLMENT ACTIVITY (accruing shipping costs when goods revenue is recognized) rather than a separate performance obligation.",
        ),
        (
            "ASC 606-10-32-2~27",
            "Step 3: Determining the Transaction Price",
            "Transaction price is the amount of consideration an entity expects to be entitled to in exchange for transferring promised goods or services (ASC 606-10-32-2).\n\n"
            "[Key Measurement Components & US GAAP Elections]\n"
            "• Sales & Similar Taxes Policy Election (ASC 606-10-32-2A): Unique US GAAP election permitting entities to exclude ALL taxes assessed by a governmental authority directly imposed on a revenue-producing transaction (sales, use, VAT, excise) from the transaction price without jurisdiction-by-jurisdiction principal/agent analysis.\n"
            "• Variable Consideration & Constraint (ASC 606-10-32-5~14): Estimate discounts, rebates, refunds, credits, price concessions, incentives, or penalties via expected value or most likely amount; include only to the extent it is PROBABLE (~75%+) that a significant reversal in cumulative revenue will not occur.\n"
            "• Significant Financing Component (ASC 606-10-32-15~20): Adjust for time value of money using a separate-financing discount rate; practical expedient ignores financing when transfer-to-payment gap <= 1 year (32-18).\n"
            "• Noncash Consideration (ASC 606-10-32-21~24): US GAAP explicitly requires measuring fair value of noncash consideration at CONTRACT INCEPTION (32-21); subsequent fair value changes due to the FORM of consideration (e.g., stock price swings) are excluded from the transaction price.\n"
            "• Consideration Payable to a Customer (ASC 606-10-32-25~27): Accounted for as a reduction of transaction price unless paid for a distinct good/service received from the customer at or below fair value.",
        ),
        (
            "ASC 606-10-32-28~45",
            "Step 4: Allocating the Transaction Price (SSP, Discounts & Variable Amounts)",
            "Allocate transaction price to each performance obligation in proportion to its relative Standalone Selling Price (SSP) determined at contract inception (ASC 606-10-32-28~31).\n\n"
            "[Estimating Standalone Selling Price (ASC 606-10-32-32~34)]\n"
            "• Best evidence: observable price when sold separately in similar circumstances to similar customers.\n"
            "• Suitable estimation methods when not directly observable: (1) Adjusted market assessment approach; (2) Expected cost plus a margin approach; (3) Residual approach — strictly limited to goods/services with highly variable or uncertain selling prices (32-34(c)).\n\n"
            "[Targeted Allocation Rules]\n"
            "• Allocating a Discount (ASC 606-10-32-36~38): Allocate proportionately across all obligations unless observable evidence shows the entire discount relates to only one or more specific obligations.\n"
            "• Allocating Variable Consideration (ASC 606-10-32-39~41): Allocate entirely to a specific performance obligation (or distinct good/service within a series) when terms relate specifically to efforts to satisfy that obligation and the allocation depicts expected entitlement.\n"
            "• Subsequent Changes in Transaction Price (ASC 606-10-32-42~45): Allocate on the same basis as at contract inception; amounts allocated to already-satisfied obligations are recognized as a cumulative catch-up adjustment in the period of change.",
        ),
        (
            "ASC 606-10-25-23~37",
            "Step 5: Satisfying Performance Obligations (Over Time vs. Point in Time)",
            "Recognize revenue when (or as) control of the promised asset transfers to the customer — control means the ability to direct the use of, and obtain substantially all remaining benefits from, the asset (ASC 606-10-25-23~26).\n\n"
            "[Over-Time Recognition — Meet Any ONE of Three Criteria (ASC 606-10-25-27)]\n"
            "• (a) Customer simultaneously receives and consumes the benefits as the entity performs (e.g., SaaS hosting, routine maintenance);\n"
            "• (b) Entity's performance creates or enhances an asset that the customer controls as it is created or enhanced (e.g., construction on customer's site);\n"
            "• (c) Asset created has NO alternative use to the entity AND the entity has an enforceable right to payment (cost + reasonable profit margin) for performance completed to date (25-27(c), 25-28~29).\n\n"
            "[Measuring Progress & Point-in-Time Indicators]\n"
            "• Progress Measurement (ASC 606-10-25-31~37): Apply a single output or input method consistently; 'right-to-invoice' practical expedient (55-18) permits recognizing revenue at invoiced amount when billing corresponds directly with value transferred; exclude uninstalled materials (zero-margin pass-through) and wasted costs from cost-to-cost measures.\n"
            "• Point-in-Time Indicators (ASC 606-10-25-30): Present right to payment, legal title, physical possession, significant risks and rewards of ownership, and customer acceptance.",
        ),
        (
            "ASC 606-10-55-22~53",
            "Implementation Guidance I: Principal vs. Agent, Returns, Warranties & Material Rights",
            "• Principal vs. Agent — Gross vs. Net (ASC 606-10-55-36~40): Determine for EACH specified good or service whether the entity controls it before transfer to the customer. Control indicators (55-39): (a) primary responsibility for fulfilling the promise; (b) inventory risk before/after transfer; (c) discretion in establishing price. Principals record gross revenue; agents record net fee/commission.\n"
            "• Sale with a Right of Return (ASC 606-10-55-22~29): Recognize revenue only for expected retained units, a refund liability for expected returns, and a return asset (carrying amount of inventory minus recovery costs, presented separately from inventory).\n"
            "• Warranties (ASC 606-10-55-30~35): Assurance-type warranties (promise that product complies with agreed specs) are accrued as a cost/liability under ASC 460/450; Service-type warranties (separately purchasable or providing additional service) are a separate performance obligation.\n"
            "• Customer Options for Additional Goods/Services (ASC 606-10-55-41~45): If an option grants a 'material right' (discount incremental to what other customers receive, e.g., loyalty points or discounted renewal), allocate transaction price to the material right and recognize when exercised or expired.\n"
            "• Breakage / Unexercised Rights (ASC 606-10-55-46~49): Recognize expected breakage (e.g., unused gift cards) proportionately as customers redeem rights if entity expects to be entitled to breakage; otherwise when likelihood of exercise becomes remote.\n"
            "• Nonrefundable Upfront Fees (ASC 606-10-55-50~53): Generally an advance payment for future goods/services unless tied to a distinct upfront transfer; administrative setup activities do NOT transfer a good/service.",
        ),
        (
            "ASC 606-10-55-54~84",
            "Implementation Guidance II: IP Licensing (Functional vs. Symbolic), Royalties & Repurchases",
            "• Licensing of Intellectual Property (ASC 606-10-55-54~64): Unique US GAAP framework dividing distinct IP licenses into TWO categories:\n"
            "  – Functional IP (55-59(a)): Significant standalone functionality (e.g., on-premise software, biological compounds, completed media/films) → POINT-IN-TIME recognition at the later of license transfer or start of license period.\n"
            "  – Symbolic IP (55-59(b)): Value depends substantially on ongoing entity activities supporting the brand (e.g., trademarks, franchise trade names, sports logos) → OVER-TIME recognition over the license period.\n"
            "• Sales- or Usage-Based Royalties Exception (ASC 606-10-55-65): When IP license is the sole or predominant item to which a royalty relates, recognize revenue ONLY at the later of (a) subsequent sale/usage occurring or (b) satisfaction of the performance obligation.\n"
            "• Repurchase Agreements (ASC 606-10-55-66~78): Forwards and call options are NOT sales — account as a lease (ASC 842) if repurchase price < original price, or a financing arrangement if >= original price. Put options depend on whether the customer has a significant economic incentive to exercise.\n"
            "• Consignment & Bill-and-Hold (ASC 606-10-55-79~84): Bill-and-hold revenue requires (1) substantive reason requested by customer, (2) product separately identified, (3) ready for physical transfer, and (4) seller cannot use or redirect the product.",
        ),
        (
            "ASC 606-10-45 / 50",
            "Presentation, Disclosures, ASU 2021-08 & SEC Focus Areas",
            "• Balance Sheet Presentation (ASC 606-10-45-1~5): Present a Contract Liability when payment is received (or unconditional right to payment arises) before performance; present a Contract Asset when performance precedes an unconditional right to payment; present a Receivable (ASC 310/326) when only the passage of time is required for payment.\n"
            "• Core Footnote Disclosures (ASC 606-10-50): (1) Disaggregation of revenue by economic factors (geography, product line, timing, contract type); (2) Opening/closing contract assets, liabilities, receivables, and revenue recognized from opening contract liabilities; (3) Remaining Performance Obligations (RPO / Backlog) with expected timing (practical expedients for contracts <= 1 year or right-to-invoice); (4) Significant judgments (timing, variable consideration, SSP).\n"
            "• ASU 2021-08 (Contract Assets/Liabilities in Business Combinations): Acquirers MUST recognize and measure acquired contract assets and deferred revenue under ASC 606 as if the acquirer had originated the contract (eliminating the former ASC 805 fair-value 'haircut' on deferred revenue).\n"
            "• Companion Contract Cost Rules: See ASC 340-40 for capitalization, amortization, and impairment (no reversal) of sales commissions and fulfillment costs.",
        ),
        (
            "ASC 606 vs IFRS 15 / CAS 14",
            "Three-Way Divergence Summary (US GAAP vs. IFRS 15 vs. China CAS 14)",
            "Although ASC 606 and IFRS 15 were jointly developed (and China CAS 14 closely converged), practitioners face recurring cross-border differences:\n"
            "• Step 1 Collectibility Threshold: ASC 606 'probable' (~75%–80%+) is higher than IFRS 15 / CAS 14 'probable' (>50%).\n"
            "• Shipping & Handling Election: ASC 606-10-25-18B allows treating post-control shipping as a fulfillment cost; IFRS 15 / CAS 14 have NO such election (often a separate performance obligation).\n"
            "• Sales Tax Exclusion Election: ASC 606-10-32-2A allows blanket exclusion of sales/VAT taxes; IFRS 15 requires assessing principal vs. agent per tax.\n"
            "• Noncash Consideration Measurement Date: ASC 606 fixes fair value at contract inception; IFRS 15 does not mandate inception date.\n"
            "• IP Licensing Model: ASC 606 uses Functional vs. Symbolic IP; IFRS 15 uses a 3-criteria right-to-access vs. right-to-use test (can yield different results for certain software/franchise licenses).\n"
            "• Contract Cost Impairment Reversal: Prohibited under ASC 340-40-35-6; required (up to carrying amount) under IFRS 15.104 / CAS 14.\n"
            "• Interim Disclosures & SEC Scrutiny: SEC registrants face intensive SEC comment letters on Principal vs. Agent (SaaS/marketplaces), RPO backlog, disaggregation consistency with MD&A/earnings calls, and ASU 2021-08 acquisition accounting.",
        ),
    ],
    "ASC 842": [
        (
            "ASC 842-10-15",
            "Identifying a Lease, Separating Components & Lease Term",
            "A contract is or contains a lease if it conveys the right to control the use of identified property, plant, or equipment for a period of time in exchange for consideration (ASC 842-10-15-3).\n\n"
            "[Control Test & Practical Expedients]\n"
            "• Control requires BOTH: (a) right to obtain substantially all economic benefits from use of the identified asset, AND (b) right to direct the use of the asset (supplier holds no substantive substitution right, 15-10~16).\n"
            "• Separating Components (ASC 842-10-15-28~37): Lessees allocate consideration between lease and nonlease components by relative standalone price, unless electing by asset class to combine them as a single lease component (15-37). Property taxes and insurance are NOT separate components.\n"
            "• Lease Term (ASC 842-10-30-1): Noncancellable period plus renewal/purchase option periods reasonably certain to be exercised (and termination option periods reasonably certain NOT to be exercised).",
        ),
        (
            "ASC 842-20-25 / 30",
            "Lessee Dual Model: Finance Leases vs. Operating Leases",
            "ALL leases > 12 months are recognized on the lessee's balance sheet (ROU Asset + Lease Liability), EXCEPT short-term leases (<= 12 months with no purchase option, elected by asset class). NOTE: ASC 842 has NO 'low-value asset' exemption.\n\n"
            "[Five Classification Criteria (ASC 842-10-25-2) — Finance if ANY One Met]\n"
            "• (1) Transfer of ownership by end of lease term; (2) Purchase option reasonably certain of exercise; (3) Lease term is for the major part of remaining economic life (75% bright-line benchmark in practice); (4) PV of lease payments >= substantially all fair value (90% benchmark); (5) Specialized asset with no alternative use to lessor.\n\n"
            "[Dual Income Statement & Cash Flow Accounting]\n"
            "• Finance Lease: Front-loaded expense = ROU straight-line amortization + effective interest on lease liability; principal payments in Financing Cash Flows, interest in Operating Cash Flows.\n"
            "• Operating Lease: SINGLE STRAIGHT-LINE lease expense in operating income; ROU amortization is plugged each period (straight-line rent minus interest accretion on lease liability); ALL cash payments remain in Operating Cash Flows.\n"
            "• Discount Rate (ASC 842-20-30-3): Rate implicit in the lease if readily determinable; otherwise lessee's Incremental Borrowing Rate (IBR) on a collateralized basis (private companies may elect risk-free rate by asset class).",
        ),
        (
            "ASC 842-30",
            "Lessor Accounting: Sales-Type, Direct Financing & Operating Leases",
            "• Three Lessor Classifications (ASC 842-10-25-2~3): (1) Sales-Type Lease (any of the 5 lessee finance criteria met → derecognize asset, recognize net investment in lease and Day-1 selling profit/loss); (2) Direct Financing Lease (none of the 5 criteria met, but PV of payments + third-party residual value guarantee >= substantially all FV and collectibility probable → defer Day-1 selling profit into net investment); (3) Operating Lease (keep asset on balance sheet, recognize straight-line rental income).\n"
            "• Collectibility Guardrail (ASC 842-30-25-3): If collectibility of lease payments is NOT probable for an operating lease, lessor limits lease income to cash collected (cash-basis ceiling).",
        ),
        (
            "ASC 842-40",
            "Sale-and-Leaseback Transactions & Lease Modifications",
            "• Sale-and-Leaseback (ASC 842-40-25): Apply ASC 606 control-transfer criteria first. A finance leaseback automatically FAILS sale accounting (treated as a failed sale / financing liability). If the transfer qualifies as a sale (operating leaseback), the seller-lessee derecognizes the asset and recognizes 100% OF THE GAIN OR LOSS IMMEDIATELY (adjusted for off-market terms).\n"
            "• Lease Modifications (ASC 842-10-25-8~14): Separate contract if granting an additional ROU asset at standalone price; otherwise reallocate consideration, reassess lease classification, remeasure lease liability at updated discount rate, and adjust ROU asset (partial terminations recognize proportional P&L gain/loss).",
        ),
        (
            "ASC 842 vs IFRS 16 / CAS 21",
            "Key Cross-Framework Divergences (US GAAP vs. IFRS 16 vs. CAS 21)",
            "• Lessee P&L & EBITDA Impact: ASC 842 preserves a straight-line Operating Lease expense inside Operating Expenses (EBITDA unchanged vs. ASC 840); IFRS 16 and CAS 21 apply a single front-loaded finance model (shifting rent into Depreciation + Interest, boosting EBITDA).\n"
            "• Low-Value Asset Exemption: Permitted under IFRS 16.5(b) (~USD 5,000) and CAS 21 (~RMB 40,000); NOT permitted under ASC 842.\n"
            "• Sale-and-Leaseback Gain: ASC 842 recognizes 100% of gain immediately; IFRS 16 / CAS 21 restrict gain recognition strictly to the proportion of rights transferred to the buyer-lessor.\n"
            "• Subleases & Variable Payments: ASC 842 classifies subleases by reference to the underlying asset (IFRS 16 references the head-lease ROU asset); index/rate-linked lease payments are NOT remeasured under ASC 842 solely for index resets (IFRS 16 remeasures upon cash-flow reset).",
        ),
    ],
    "ASC 326": [
        (
            "ASC 326-20-30",
            "CECL Model: Day-1 Lifetime Expected Credit Losses & Pooling",
            "Applies to financial assets measured at amortized cost (loans, trade receivables, HTM debt securities), net investments in leases, reinsurance receivables, and off-balance-sheet credit exposures (ASC 326-20-15).\n\n"
            "[Core Measurement Mechanics (ASC 326-20-30-1~11)]\n"
            "• Day-1 Lifetime Loss: Immediately upon origination or purchase, estimate full LIFETIME expected credit losses over the contractual term (adjusted for expected prepayments, NOT expected extensions unless reasonably expected TDR/modification).\n"
            "• Mandatory Collective Pooling (30-2): Assets sharing similar risk characteristics MUST be evaluated on a collective (pool) basis; evaluate individually only when an asset no longer shares similar risk characteristics.\n"
            "• Three Information Pillars (30-7~9): Historical loss experience + current economic conditions + reasonable and supportable (R&S) forecasts, reverting systematically (e.g., straight-line) to historical loss information beyond the R&S forecast horizon.\n"
            "• Acceptable Methods: Loss-rate, roll-rate, vintage analysis, discounted cash flow (DCF), or PD/LGD/EAD models (no single method prescribed).",
        ),
        (
            "ASC 326-20-35",
            "PCD Assets, Collateral-Dependent Loans & Write-Offs",
            "• Purchased Financial Assets with Credit Deterioration — PCD (ASC 326-20-30-13): Acquired loans with more-than-insignificant credit deterioration since origination use the 'gross-up' approach — initial CECL allowance is added to the purchase price to establish amortized cost basis (NO Day-1 P&L credit loss expense).\n"
            "• Collateral-Dependent Practical Expedient (ASC 326-20-35-4~5): When repayment is expected substantially through operation or sale of collateral and the borrower is in financial difficulty, measure ECL based on the fair value of collateral (less costs to sell if sale is expected).\n"
            "• Write-Offs & Recoveries (ASC 326-20-35-8): Write off in the period deemed uncollectible; expected recoveries of previously written-off amounts are included in the CECL allowance (can result in a negative allowance capped at prior write-offs).",
        ),
        (
            "ASC 326-30",
            "Available-for-Sale (AFS) Debt Securities Credit Loss Model",
            "AFS debt securities are EXCLUDED from CECL and follow a targeted impairment model (ASC 326-30-35):\n"
            "• Evaluated INDIVIDUALLY at each reporting date whenever Fair Value < Amortized Cost.\n"
            "• If entity intends to sell (or more likely than not will be required to sell) before recovery, write down amortized cost directly to fair value through P&L.\n"
            "• Otherwise, separate credit loss (PV of expected cash flows < amortized cost) from non-credit loss (recorded in OCI). Credit loss is recorded via an ALLOWANCE (reversible if credit improves) and strictly capped at the excess of amortized cost over fair value (the 'fair value floor').",
        ),
        (
            "ASC 326 vs IFRS 9 / CAS 22",
            "Key Cross-Framework Divergences (CECL vs. IFRS 9 3-Stage ECL)",
            "• Day-1 Provisioning Cliff: ASC 326 recognizes FULL LIFETIME ECL on Day 1 for all amortized-cost loans (larger initial reserves, especially for long-dated mortgages/corporate loans); IFRS 9 / CAS 22 recognize only 12-month ECL at Stage 1 and move to lifetime ECL only after a Significant Increase in Credit Risk (Stage 2).\n"
            "• AFS / FVOCI Debt Securities: ASC 326-30 caps credit allowance at the fair value floor and avoids CECL; IFRS 9 applies the same 3-stage ECL model to FVOCI debt without a fair value floor.\n"
            "• Vintage Disclosures: Public business entities under ASC 326-20-50 must disclose amortized cost and gross write-offs by credit quality indicator and year of origination (5-year vintage table).",
        ),
    ],
    "ASC 740": [
        (
            "ASC 740-10-25 / 30",
            "Asset-Liability Method, Enacted Rates & Valuation Allowance",
            "• Balance Sheet Asset-and-Liability Approach (ASC 740-10-25-2): Recognize current tax payable/refundable and deferred tax liabilities (DTLs) / deferred tax assets (DTAs) for all temporary differences and carryforwards.\n"
            "• Enacted Tax Rates ONLY (ASC 740-10-30-8): Measure deferred taxes strictly using tax rates ENACTED into law by the balance sheet date (in the US, signed by the President) — never 'substantively enacted'. Effect of tax law changes is recognized in continuing operations in the period of enactment.\n"
            "• Gross DTA + Valuation Allowance (ASC 740-10-30-5): Recognize 100% of DTAs first, then establish a contra-asset Valuation Allowance if it is 'more likely than not' (>50%) that some or all DTAs will not be realized, weighing four sources of taxable income (reversing DTLs, future taxable income, carrybacks, and tax-planning strategies). Cumulative 3-year losses constitute strong negative evidence.\n"
            "• Indefinite Reinvestment Exception (ASC 740-30-25-17): No DTL on outside basis differences of foreign subsidiaries if earnings are indefinitely reinvested.",
        ),
        (
            "ASC 740-10-25-6",
            "Uncertain Tax Positions (UTPs — FIN 48 Two-Step Model)",
            "Applies to all income tax positions taken or expected to be taken on a tax return, assuming full examination by tax authorities with full knowledge of all relevant facts (zero detection risk assumption):\n"
            "• Step 1 — Recognition (ASC 740-10-25-6): Recognize a tax benefit ONLY if it is 'more likely than not' (>50%) that the position will be sustained upon examination based purely on its technical merits.\n"
            "• Step 2 — Measurement (ASC 740-10-30-7): Measure at the LARGEST amount of tax benefit that has a GREATER THAN 50% CUMULATIVE LIKELIHOOD of being realized upon ultimate settlement.\n"
            "• Classification & Interest/Penalties: Present unrecognized tax benefits as a separate noncurrent liability (or DTA reduction for NOL/credit carryforwards); policy election to classify interest/penalties in income tax expense or operating/interest expense.",
        ),
        (
            "ASC 740-10-50",
            "ASU 2023-09 Disclosures (FY2025+) & OECD Pillar Two Treatment",
            "• ASU 2023-09 Income Tax Disclosures (effective FY2025+ for PBEs): Mandates a standardized 8-category tabular effective tax rate reconciliation showing BOTH percentages AND dollar amounts (state/local, foreign tax effects, tax law changes, tax credits, valuation allowance, nontaxable/nondeductible items, cross-border tax laws, changes in UTPs) with a 5% quantitative disaggregation threshold, plus disaggregated cash income taxes paid by federal, state, and foreign jurisdictions (>= 5% threshold).\n"
            "• OECD Pillar Two (GloBE 15% Minimum Tax): FASB staff confirmed that Pillar Two top-up taxes are accounted for as an Alternative Minimum Tax (AMT) under ASC 740-10-30-10 — recognized as a PERIOD COST as incurred, with NO deferred tax assets or liabilities recorded or remeasured for GloBE.",
        ),
        (
            "ASC 740 vs IAS 12 / CAS 18",
            "Key Cross-Framework Divergences (US GAAP vs. IAS 12 / IFRIC 23)",
            "• Tax Rate Enactment: ASC 740 requires ENACTED rates; IAS 12 uses enacted OR substantively enacted rates.\n"
            "• Intra-Entity Inventory Transfers: ASC 740-10-25-3(e) defers the seller's tax expense as a prepaid asset until inventory is sold outside the group (no DTA at buyer's rate); IAS 12 recognizes DTA immediately at the buyer's tax rate. (Note: ASU 2016-16 aligned non-inventory intra-entity transfers with IAS 12.)\n"
            "• UTP Measurement: ASC 740 uses cumulative-probability largest >50% amount; IFRIC 23 uses most likely amount or expected value.\n"
            "• Backward Tracing: Prohibited under ASC 740 (subsequent rate/valuation allowance changes hit P&L even if original item was in OCI/equity); IAS 12 requires backward tracing to OCI/equity.",
        ),
    ],
    "ASC 805": [
        (
            "ASC 805-10-55",
            "Definition of a Business & Mandatory Screen Test",
            "Before applying acquisition accounting, determine whether the acquired set is a BUSINESS or an ASSET ACQUISITION (ASC 805-10-55-3A~9):\n"
            "• Mandatory Screen Test (55-5A): If substantially all fair value of the gross assets acquired is concentrated in a single identifiable asset or group of similar identifiable assets, the set is NOT a business (account as an asset acquisition — capitalize transaction costs, no goodwill, no Day-1 bargain purchase gain).\n"
            "• Framework when Screen Fails: Must include at minimum an input AND a substantive process that together significantly contribute to the ability to create outputs (higher bar when no outputs exist yet — requires an organized workforce).",
        ),
        (
            "ASC 805-20 / 30",
            "Acquisition Method, Full Goodwill, Contingent Consideration & Measurement Period",
            "• Four Steps (ASC 805-10-05-4): (1) Identify acquirer; (2) Determine acquisition date; (3) Recognize & measure identifiable assets acquired, liabilities assumed, and Noncontrolling Interest (NCI); (4) Recognize goodwill or bargain purchase gain.\n"
            "• Mandatory Full Goodwill (ASC 805-20-30-1): NCI MUST be measured at acquisition-date FAIR VALUE (incorporating both controlling and NCI goodwill — no partial goodwill option).\n"
            "• Acquisition-Related Costs (ASC 805-10-25-23): Expensed as incurred (banker, legal, audit fees).\n"
            "• Contingent Consideration / Earn-Outs (ASC 805-30-25-5): Recognized at acquisition-date fair value; liability-classified earn-outs are remeasured to fair value through P&L each period (equity-classified earn-outs are not remeasured).\n"
            "• Measurement Period (ASC 805-10-25-13~19): Up to 1 year from acquisition date to finalize provisional fair values; adjustments are recognized in the REPORTING PERIOD identified (ASU 2015-16 — no retrospective restatement of prior comparative periods).",
        ),
        (
            "ASC 805-50",
            "Pushdown Accounting, Common-Control Transfers & JV Formations",
            "• Pushdown Accounting Election (ASC 805-50-25-4): An acquired entity may ELECT to apply pushdown accounting in its separate financial statements upon a change-in-control event (stepping up assets/liabilities and recording goodwill on the subsidiary's own books).\n"
            "• Common-Control Transactions (ASC 805-50-30-5): Accounted for at historical carrying amounts (carryover basis) with retrospective combination for periods under common control.\n"
            "• Joint Venture Formations (ASU 2023-05, ASC 805-60, effective Jan 1, 2025): Newly formed JVs measure contributed net assets at FAIR VALUE upon formation (recognizing goodwill if total JV fair value exceeds identifiable net assets).",
        ),
        (
            "ASC 805 vs IFRS 3 / CAS 20",
            "Key Cross-Framework Divergences (US GAAP vs. IFRS 3 vs. CAS 20)",
            "• NCI & Goodwill: ASC 805 mandates Fair Value (full goodwill); IFRS 3 allows transaction-by-transaction choice between fair value and proportionate share of identifiable net assets.\n"
            "• Screen Test: Mandatory under ASC 805; optional Concentration Test under IFRS 3.B7B.\n"
            "• Pushdown Accounting: Permitted under ASC 805-50; NOT permitted under IFRS.\n"
            "• Pre-Acquisition Contingencies: ASC 805-20-25-19 recognizes contingent liabilities at fair value only if determinable during the measurement period (otherwise falls back to ASC 450 probable/estimable); IFRS 3 recognizes all present-obligation contingent liabilities if fair value is reliably measurable.\n"
            "• Measurement Period Adjustments: Recognized in current period under ASC 805; applied retrospectively to acquisition date under IFRS 3.45.",
        ),
    ],
    "ASC 810": [
        (
            "ASC 810-10-15",
            "Dual Consolidation Framework: Step 1 VIE Scope & Criteria",
            "US GAAP requires evaluating consolidation in strict sequence: FIRST the Variable Interest Entity (VIE) model, and ONLY IF not a VIE, the Voting Interest Entity (VOE) model.\n\n"
            "[When Is an Entity a VIE? (ASC 810-10-15-14) — Meet ANY One Criterion]\n"
            "• (a) Insufficient Equity at Risk: Total equity investment at risk is insufficient to finance activities without subordinated financial support (<10% rule-of-thumb rebuttable presumption).\n"
            "• (b) Equity Holders Lack Characteristics of a Controlling Financial Interest: As a group, equity holders at risk lack (i) power to direct the most significant economic activities, (ii) obligation to absorb expected losses, OR (iii) right to receive expected residual returns.\n"
            "• (c) Anti-Abuse / Disproportionate Voting Rights: Voting rights of some investors are not proportional to their economics AND substantially all activities are conducted on behalf of an investor with disproportionately few voting rights.\n"
            "• Note: Classic China-concept US-listed VIE structures (contractual control via WFOE agreements) are consolidated directly under the VIE model.",
        ),
        (
            "ASC 810-10-25",
            "VIE Primary Beneficiary: Power + Economics & Kick-Out Rights",
            "The party that consolidates a VIE is its Primary Beneficiary — the variable interest holder with BOTH (ASC 810-10-25-38A):\n"
            "• (1) Power Criterion: The power to direct the activities of the VIE that MOST SIGNIFICANTLY impact the VIE's economic performance (unilateral substantive kick-out rights held by a single unrelated party can negate power).\n"
            "• (2) Economics Criterion: The obligation to absorb losses OR the right to receive benefits from the VIE that COULD POTENTIALLY BE SIGNIFICANT to the VIE.\n"
            "• Related-Party Tiebreaker (ASC 810-10-25-42~44): When no single party meets both criteria individually, a related-party group under common control evaluates who is 'most closely associated' with the VIE.",
        ),
        (
            "ASC 810-10-15 / 40",
            "Step 2 Voting Interest Model (VOE) & Deconsolidation",
            "• Voting Interest Model (ASC 810-10-15-8): For non-VIE corporations, consolidation generally requires >50% of outstanding voting shares, UNLESS noncontrolling shareholders hold substantive participating rights (e.g., veto over budgets/CEO hiring). Unlike IFRS 10, US GAAP has NO 'de facto control' concept for <50% stakes and ignores unexercised potential voting rights.\n"
            "• Limited Partnerships (non-VIE): General Partner consolidates unless Limited Partners hold substantive kick-out rights (simple majority) or participating rights.\n"
            "• Deconsolidation (ASC 810-10-40-4~5): Upon loss of controlling financial interest in a subsidiary (business), derecognize assets/liabilities/NCI, remeasure any retained noncontrolling investment to FAIR VALUE, and recognize full gain/loss in net income.",
        ),
        (
            "ASC 810 vs IFRS 10 / CAS 33",
            "Key Cross-Framework Divergences (Dual VIE/VOE vs. Single Control Model)",
            "• Architecture: ASC 810 uses a rules-heavy TWO-TIER model (VIE then VOE); IFRS 10 / CAS 33 apply a SINGLE principles-based control model (power + variable returns + link).\n"
            "• De Facto Control & Potential Voting Rights: IFRS 10 consolidates a <50% holder with de facto control over dispersed shareholders and factors in substantive options/convertibles; ASC 810 VOE strictly requires >50% voting shares.\n"
            "• Uniform Accounting Policies & Reporting Dates: IFRS 10 requires uniform accounting policies across the group; ASC 810 does NOT require conforming a subsidiary's valid alternative GAAP policy (e.g., LIFO vs. FIFO). Both allow up to a 3-month lag for subsidiary reporting dates (with significant intervening events disclosed/adjusted).",
        ),
    ],
    "ASC 718": [
        (
            "ASC 718-10-25 / 30",
            "Equity vs. Liability Classification & Award Conditions",
            "Covers share-based payment awards granted to BOTH employees and nonemployees (aligned by ASU 2018-07), measured at grant-date fair value (option pricing models such as Black-Scholes or Monte Carlo).\n\n"
            "[Equity vs. Liability Classification (ASC 718-10-25-6~19A)]\n"
            "• Equity-Classified Awards: Fixed at grant-date fair value (no subsequent remeasurement); includes stock options, RSUs, and PSUs settled in shares (net-share settlement up to MAXIMUM statutory individual tax rate retains equity classification under ASU 2016-09).\n"
            "• Liability-Classified Awards: Cash-settled awards (e.g., cash SARs) or share-settled awards with a fixed monetary value (ASC 480) — remeasured to fair value through P&L at every reporting date until settlement.\n\n"
            "[Three Award Conditions]\n"
            "• Service & Performance Conditions: Affect the QUANTITY of awards expected to vest (expense recognized only when performance condition is PROBABLE, ~75%+).\n"
            "• Market Conditions (e.g., stock price hurdle, relative TSR): Baked into grant-date fair value via Monte Carlo simulation; expense is NEVER reversed if the market target is missed (provided service is rendered).",
        ),
        (
            "ASC 718-10-35",
            "Graded Vesting Election, Forfeitures, Modifications & Income Taxes",
            "• Graded Vesting Attribution (ASC 718-10-35-8): For awards with ONLY service conditions and graded vesting (e.g., 25% per year over 4 years), US GAAP allows an accounting policy election between (a) STRAIGHT-LINE recognition over the total requisite service period (subject to floor of vested portion) OR (b) accelerated tranche-by-tranche attribution.\n"
            "• Forfeiture Policy Election (ASU 2016-09): Entities may elect either to estimate expected forfeitures upfront OR recognize forfeitures as they actually occur.\n"
            "• Modifications (ASC 718-20-35-3): Categorized into four types (Type I Probable-to-Probable recognizes incremental FV; Type III Improbable-to-Probable resets measurement to modification-date FV).\n"
            "• Excess Tax Benefits/Deficiencies (ASC 718-740): Recognized entirely in Income Tax Expense (P&L) upon vesting/exercise, increasing EPS volatility.",
        ),
        (
            "ASC 718 vs IFRS 2 / CAS 11",
            "Key Cross-Framework Divergences (US GAAP vs. IFRS 2 vs. CAS 11)",
            "• Graded Vesting: ASC 718 permits straight-line attribution; IFRS 2 / CAS 11 MANDATE accelerated tranche-by-tranche attribution (front-loading SBC expense).\n"
            "• Forfeitures: ASC 718 allows accounting for forfeitures as incurred; IFRS 2 requires estimating forfeitures upfront.\n"
            "• Deferred Taxes: ASC 718 books DTA based on grant-date GAAP expense and sends excess tax benefits/deficiencies to P&L; IFRS 2 remeasures DTA each period based on intrinsic value at current stock price, capping P&L tax benefit at book expense and crediting excess to Equity.\n"
            "• Payroll Taxes: Recognized upon the triggering event (exercise/vesting) under ASC 718; accrued over the vesting period as a cash-settled liability under IFRS 2.",
        ),
    ],
    "ASC 480": [
        (
            "ASC 480-10-25",
            "Three Mandatory Liability Classes for Freestanding Instruments",
            "ASC 480-10 requires classifying THREE specific classes of freestanding financial instruments as LIABILITIES (rather than equity):\n"
            "• (1) Mandatorily Redeemable Financial Instruments (25-4): Shares embodying an unconditional obligation requiring the issuer to redeem them by transferring assets at a specified/determinable date or upon an event CERTAIN to occur (e.g., death of holder).\n"
            "• (2) Obligations to Repurchase Issuer's Equity Shares by Transferring Assets (25-8): e.g., written put options or forward purchase contracts on own shares settled physically or net in cash.\n"
            "• (3) Certain Obligations to Issue a Variable Number of Shares (25-14): Obligations whose monetary value at inception is based solely or predominantly on (a) a fixed monetary amount known at inception (e.g., 'settle $10M in shares'), (b) variations in something other than the issuer's equity fair value, or (c) variations inversely related to the issuer's share price.",
        ),
        (
            "ASC 480-10-S99-3A",
            "SEC Temporary / Mezzanine Equity & Interaction with ASC 815-40",
            "• SEC Temporary / Mezzanine Equity (ASC 480-10-S99-3A / ASR 268): For SEC registrants, redeemable equity securities whose redemption is OUTSIDE THE SOLE CONTROL of the issuer (e.g., VC/PE convertible preferred stock redeemable upon a deemed liquidation / change of control, or puttable at holder's option after 5 years) CANNOT be presented in permanent stockholders' equity — they are presented between Total Liabilities and Stockholders' Equity as 'Temporary / Mezzanine Equity'.\n"
            "• Accretion to Redemption Value: If redemption is probable (or currently redeemable), accrete carrying amount to redemption value through retained earnings/APIC (impacting EPS via numerator adjustment, NOT net income).\n"
            "• Freestanding Warrants & Conversion Features: Instruments outside ASC 480 are next tested under ASC 815-40 (2-step indexation & equity-classification test) to determine equity vs. derivative liability.",
        ),
        (
            "ASC 480 vs IAS 32 / CAS 37",
            "Key Cross-Framework Divergences (Mezzanine Equity vs. IAS 32 Liability)",
            "• Conditionally Redeemable Preferred Stock (Huge Impact on Pre-IPO / Tech Companies): Under IAS 32 / CAS 37, preferred shares with redemption triggers outside the issuer's sole control are generally FINANCIAL LIABILITIES (often measured at FVTPL, creating massive P&L fair-value losses as company valuation rises!); under US GAAP (ASC 480 + SEC S99-3A), they sit in Temporary/Mezzanine Equity with ZERO net income fair-value volatility.\n"
            "• Fixed-for-Fixed vs. Indexation: IAS 32 applies a strict 'fixed-for-fixed' rule for equity derivatives; US GAAP applies ASC 815-40's two-step indexation and settlement framework.",
        ),
    ],
    "ASC 815": [
        (
            "ASC 815-10-15",
            "Derivative Definition, Scope Exceptions & Embedded Derivatives",
            "• Three Cumulative Derivative Characteristics (ASC 815-10-15-83): (1) One or more underlyings AND one or more notional amounts/payment provisions; (2) No initial net investment (or smaller than similar market-response contracts); (3) Net settlement (contractual net settlement, market mechanism, or delivery of an asset readily convertible to cash).\n"
            "• Key Scope Exceptions: Normal Purchases and Normal Sales (NPNS, 15-22 — requires documentation), regular-way security trades, insurance contracts, and contracts indexed to and classified in the entity's own equity (ASC 815-40).\n"
            "• Embedded Derivatives (ASC 815-15-25-1): Bifurcate and measure at FVTPL if (a) economic characteristics/risks are NOT 'clearly and closely related' to the host contract (e.g., equity-linked feature in a debt host), (b) hybrid is not remeasured at FVTPL, and (c) standalone instrument meets the derivative definition.",
        ),
        (
            "ASC 815-20 / 25 / 30",
            "Hedge Accounting (Fair Value, Cash Flow, Net Investment & Portfolio Layer)",
            "All derivatives are carried on the balance sheet at Fair Value (default FVTPL) unless qualifying for optional Hedge Accounting:\n"
            "• Qualification (ASC 815-20-25): Formal contemporaneous documentation at inception + expected to be 'HIGHLY EFFECTIVE' (80%–125% quantitative corridor in practice) at inception and ongoing (ASU 2017-12 allows qualitative ongoing assessments after initial quantitative proof).\n"
            "• Fair Value Hedge (ASC 815-25): Hedging derivative and hedged item basis adjustment both hit the SAME income statement line item. Portfolio Layer Method (ASU 2022-01) allows multiple layers of closed portfolios of prepayable financial assets.\n"
            "• Cash Flow Hedge (ASC 815-30): ENTIRE change in fair value of the hedging instrument (for included components) is recorded in OCI and reclassified into the SAME P&L line when the hedged forecasted transaction impacts earnings (ASU 2017-12 eliminated separate ineffectiveness measurement).\n"
            "• Net Investment Hedge (ASC 815-35): FX gains/losses recorded in CTA (OCI) to offset foreign subsidiary translation.",
        ),
        (
            "ASC 815-40",
            "Contracts in an Entity's Own Equity (SPAC Warrants & Convertibles)",
            "Two-step model to qualify for equity classification (and avoid FVTPL derivative liability):\n"
            "• Step 1 — Indexation (ASC 815-40-15): Contingent exercise provisions cannot be based on an observable market/index other than the issuer's own stock or operations; settlement amount must equal the difference between fair value of a fixed number of shares and a fixed monetary amount (inputs restricted to standard fixed-for-fixed option pricing inputs).\n"
            "• Step 2 — Equity Classification Conditions (ASC 815-40-25): Issuer must have sufficient authorized shares, explicit share cap, no net cash settlement outside issuer's control, and no top-off/collateral requirements. (Tender-offer cash-out provisions caused the 2021 SEC SPAC warrant restatement wave.)",
        ),
        (
            "ASC 815 vs IFRS 9 / CAS 24",
            "Key Cross-Framework Divergences (US GAAP vs. IFRS 9 Hedge Accounting)",
            "• Hedge Effectiveness Threshold: ASC 815 retains the 'highly effective' (80%–125%) bar; IFRS 9 / CAS 24 eliminated the bright line in favor of a principles-based economic relationship test.\n"
            "• Cash Flow Hedge Ineffectiveness: ASC 815 records 100% of qualifying derivative FV change in OCI (no separate P&L ineffectiveness line); IFRS 9 measures and books over-hedge ineffectiveness directly to P&L.\n"
            "• Embedded Derivatives in Financial Asset Hosts: ASC 815 bifurcates embedded derivatives from BOTH financial asset and liability hosts; IFRS 9 prohibits bifurcation for financial asset hosts (evaluates hybrid as a whole under SPPI).",
        ),
    ],
    "ASC 350": [
        (
            "ASC 350-20",
            "Goodwill Impairment Testing (Reporting Unit Single-Step Model)",
            "Goodwill is NOT amortized (for public business entities) and is tested for impairment at least ANNUALLY (and between annual dates upon a triggering event) at the REPORTING UNIT level (an operating segment or one level below, ASC 350-20-35-34).\n"
            "• Optional Qualitative 'Step 0' Screen (35-3A): If more likely than not (>50%) that Reporting Unit fair value exceeds carrying amount, no quantitative test is needed.\n"
            "• Quantitative Single-Step Test (ASU 2017-04, 35-4~8B): Compare Reporting Unit FAIR VALUE to carrying amount (including goodwill). Recognize impairment for any excess of carrying amount over fair value, capped at allocated goodwill. Reversal of goodwill impairment is STRICTLY PROHIBITED.\n"
            "• Private Company Alternative (35-63): Private companies may elect to amortize goodwill straight-line over <= 10 years and test for impairment only upon a triggering event.",
        ),
        (
            "ASC 350-40",
            "Internal-Use Software & Cloud Computing Arrangements (SaaS)",
            "• Three Development Stages (ASC 350-40-25): (1) Preliminary Project Stage → EXPENSE as incurred; (2) Application Development Stage (coding, hardware installation, testing) → CAPITALIZE direct costs & payroll; (3) Post-Implementation / Operation Stage (training, maintenance) → EXPENSE as incurred.\n"
            "• Cloud Computing / Hosting Arrangements (ASU 2018-15): Customers in a SaaS hosting arrangement (service contract without a software license) capitalize qualifying implementation costs following ASC 350-40 stages and amortize them over the hosting term into the SAME P&L line as hosting fees.",
        ),
        (
            "ASC 350-60",
            "Crypto Assets Fair Value Model (ASU 2023-08) & Cross-Framework Comparison",
            "• Mandatory Fair Value Through Net Income (ASC 350-60, ASU 2023-08, effective FY2025+): Applies to fungible, blockchain-secured crypto assets meeting intangible definition that do NOT provide enforceable rights to underlying goods/services/assets and are not created by the reporting entity (e.g., Bitcoin, Ether; excludes NFTs, wrapped tokens, and stablecoins). Measured at FAIR VALUE each reporting period with changes in NET INCOME, presented separately on the balance sheet and income statement.\n"
            "• Key Divergences vs. IAS 36 / IAS 38 / CAS 6 & 8: (1) Goodwill tested at Reporting Unit level via Fair Value under ASC 350 vs. CGU level via Recoverable Amount (higher of FVLCD and VIU) under IAS 36; (2) Indefinite-lived intangible impairment reversal is prohibited under ASC 350-30, permitted under IAS 36; (3) Crypto assets are FVTPL under ASC 350-60 vs. indefinite-lived cost/OCI revaluation under IAS 38 (IFRIC Agenda Decision 2019).",
        ),
    ],
    "ASC 360": [
        (
            "ASC 360-10-35",
            "Historical Cost Model & Two-Step Undiscounted Impairment Test",
            "• Strict Historical Cost Only: PP&E is carried at cost less accumulated depreciation and impairment — upward revaluation is strictly prohibited.\n"
            "• Asset Group Level (ASC 360-10-35-23): Test long-lived assets held and used at the lowest level for which identifiable cash flows are largely independent of other asset groups.\n"
            "• Two-Step Impairment Test (ASC 360-10-35-17~21) — Triggered ONLY by Impairment Indicators:\n"
            "  – Step 1 (Recoverability Screen): Compare carrying amount of the asset group to the sum of UNDISCOUNTED future net cash flows over the remaining useful life of the primary asset. If undiscounted cash flows >= carrying amount, NO impairment is recorded (even if Fair Value < carrying amount!).\n"
            "  – Step 2 (Measurement): Only if Step 1 fails, recognize impairment equal to carrying amount minus FAIR VALUE (ASC 820). Allocate loss pro rata across long-lived assets (not reducing any asset below its individual determinable fair value).\n"
            "• Prohibition of Reversals (35-20): Impairment losses on held-and-used assets establish a new cost basis and can NEVER be reversed.",
        ),
        (
            "ASC 360-10-45",
            "Long-Lived Assets Held for Sale & Component Depreciation",
            "• Six Held-for-Sale Criteria (ASC 360-10-45-9): Management committed to plan to sell; available for immediate sale; active program to locate buyer; sale probable within 1 year; actively marketed at reasonable price; unlikely plan will change significantly.\n"
            "• Measurement (45-9 & 35-43): Cease depreciation; measure at lower of carrying amount or Fair Value Less Cost to Sell. Subsequent fair value recoveries ARE recognized up to cumulative prior write-downs while held for sale.\n"
            "• Component Depreciation: Permitted under US GAAP but NOT mandatory (unlike IAS 16.43).",
        ),
        (
            "ASC 360 vs IAS 16 / IAS 36 / CAS 4 & 8",
            "Key Cross-Framework Divergences (2-Step Undiscounted vs. 1-Step Discounted)",
            "• Impairment Trigger Frequency: ASC 360's Step 1 uses UNDISCOUNTED cash flows, making impairments significantly less frequent than IAS 36 / CAS 8's 1-step discounted Recoverable Amount test.\n"
            "• Reversals & Revaluation: Both upward revaluation (IAS 16) and non-goodwill impairment reversal (IAS 36) are permitted under IFRS, whereas US GAAP strictly prohibits both (China CAS 4/8 also prohibit both).",
        ),
    ],
    "ASC 330": [
        (
            "ASC 330-10-30",
            "Inventory Cost Formulas, LIFO & IRS Conformity Rule",
            "• Permitted Cost Flow Assumptions (ASC 330-10-30-9): FIFO, Weighted Average, Specific Identification, AND Last-In, First-Out (LIFO).\n"
            "• LIFO Conformity Rule (IRC §472(c)): Under US tax law, a company using LIFO for federal income tax returns MUST also use LIFO for primary financial reporting to shareholders/creditors — making LIFO prevalent in US energy, retail, and manufacturing sectors during inflationary periods.\n"
            "• LIFO Reserve Disclosure: Public LIFO users must disclose the LIFO reserve (excess of FIFO/current cost over LIFO carrying amount) and any LIFO liquidation gains in footnotes.",
        ),
        (
            "ASC 330-10-35",
            "Subsequent Measurement (LCNRV vs. LCM) & No Reversals",
            "• Two Subsequent Measurement Models (ASU 2015-11, ASC 330-10-35-1B~2):\n"
            "  – FIFO & Average Cost Inventory: Lower of Cost and Net Realizable Value (LCNRV — estimated selling price minus reasonably predictable costs of completion, disposal, and transportation).\n"
            "  – LIFO & Retail Inventory Method: Lower of Cost or Market (LCM), where 'Market' is current replacement cost bounded by NRV (ceiling) and NRV minus normal profit margin (floor).\n"
            "• Strict Prohibition of Reversals (ASC 330-10-35-14): Once written down, the reduced value becomes the NEW cost basis — subsequent recoveries CANNOT be reversed (except interim-period recoveries within the same fiscal year under ASC 270).",
        ),
        (
            "ASC 330 vs IAS 2 / CAS 1",
            "Key Cross-Framework Divergences (LIFO & Write-Down Reversals)",
            "• LIFO: Permitted under ASC 330; STRICTLY PROHIBITED under IAS 2.25 and China CAS 1.\n"
            "• Reversal of Inventory Write-Downs: Strictly prohibited across fiscal years under ASC 330; REQUIRED (up to original cost) under IAS 2.33 and CAS 1.\n"
            "• Measurement Basis: IAS 2 / CAS 1 use LCNRV universally; ASC 330 retains LCM for LIFO and retail inventory.",
        ),
    ],
    "ASC 450": [
        (
            "ASC 450-20 / 30",
            "Loss Contingencies (~75% Probable Bar, Range Minimum) & Gain Contingencies",
            "• Loss Contingency Accrual Criteria (ASC 450-20-25-2): Accrue a liability when BOTH (a) it is PROBABLE (likely to occur, ~70%–75%+ in US practice) that a liability has been incurred at the balance sheet date, AND (b) the amount of loss can be reasonably estimated.\n"
            "• Range of Loss (ASC 450-20-30-1): When a range of loss is estimable and NO amount within the range is a better estimate than any other, accrue the MINIMUM amount in the range and disclose the reasonably possible additional exposure up to the upper bound.\n"
            "• Reasonably Possible Losses (ASC 450-20-50-3~4): If loss is 'reasonably possible' (more than remote, less than probable), do NOT accrue — disclose the nature of contingency and estimated range of loss (or state an estimate cannot be made).\n"
            "• Discounting: Generally prohibited unless aggregate amount and timing of cash flows are fixed or reliably determinable.\n"
            "• Gain Contingencies (ASC 450-30): Never recognized prior to realization; avoid misleading disclosures.",
        ),
        (
            "ASC 450 vs IAS 37 / CAS 13",
            "Key Cross-Framework Divergences (75% vs. >50%; Minimum vs. Midpoint)",
            "• Recognition Threshold: ASC 450 'probable' (~70%–75%+) is materially higher than IAS 37 / CAS 13 'more likely than not' (>50%), delaying litigation/claim accruals under US GAAP.\n"
            "• Equal-Probability Range: ASC 450 accrues the MINIMUM of the range; IAS 37 / CAS 13 accrue the MIDPOINT (or expected value for large populations).\n"
            "• Discounting & Constructive Obligations: IAS 37 requires discounting when time value is material and covers constructive obligations broadly; ASC 450 generally prohibits discounting and focuses on legal/incurred obligations (restructuring exit costs sit separately in ASC 420).",
        ),
    ],
    "ASC 470": [
        (
            "ASC 470-20",
            "Convertible Debt Single-Liability Model (ASU 2020-06) & Debt Classification",
            "• Simplified Convertible Debt (ASU 2020-06, effective FY2022+ for PBEs): Eliminated the Cash Conversion Feature (CCF) and Beneficial Conversion Feature (BCF) separation models. Most traditional convertible debt is now accounted for as a SINGLE LIABILITY at amortized cost (no equity bifurcation and no non-cash interest accretion from debt discounts), unless the conversion option must be bifurcated as an embedded derivative (ASC 815) or issued at a substantial premium.\n"
            "• EPS Impact (ASC 260): Mandatory 'if-converted' method (eliminating treasury stock method for net-share-settled convertibles where principal may be settled in shares).\n"
            "• Covenant Violations & Refinancing (ASC 470-10-45): Short-term debt refinanced on a long-term basis AFTER balance sheet date but BEFORE financial statement issuance qualifies as NONCURRENT (contrast with IAS 1, which requires refinancing agreement before balance sheet date).",
        ),
        (
            "ASC 470-50",
            "Debt Modifications vs. Extinguishments (10% Cash Flow Test)",
            "• 10% Present-Value Test (ASC 470-50-40-10): Compare present value of modified cash flows to remaining original cash flows discounted at the ORIGINAL effective interest rate (EIR).\n"
            "  – >= 10% Change (Substantially Different) → EXTINGUISHMENT: Derecognize old debt, record new debt at FAIR VALUE, recognize gain/loss in P&L; lender fees capitalized, third-party costs expensed.\n"
            "  – < 10% Change (Non-Substantial Modification) → PROSPECTIVE ADJUSTMENT: NO immediate P&L gain or loss! Adjust effective interest rate prospectively; lender fees deferred, third-party costs expensed.\n"
            "• Troubled Debt Restructuring — Debtor (ASC 470-60): If debtor is in financial difficulty and lender grants a concession, recognize gain ONLY if total UNDISCOUNTED future cash flows < carrying amount.",
        ),
        (
            "ASC 470 vs IAS 32 / IFRS 9",
            "Key Cross-Framework Divergences (Convertibles & Non-Substantial Modifications)",
            "• Convertible Bonds: IAS 32 ALWAYS bifurcates compound convertible debt into Liability + Equity (creating higher effective interest expense); ASU 2020-06 keeps most US GAAP convertibles as a single liability with lower GAAP interest expense.\n"
            "• Non-Substantial Modifications (<10%): IFRS 9.5.4.3 requires an IMMEDIATE P&L modification gain/loss (recalculating PV at original EIR); ASC 470-50 amortizes the difference prospectively with NO Day-1 P&L impact.\n"
            "• Post-Year-End Refinancing / Waivers: Allowed to keep debt noncurrent under ASC 470-10 if completed before issuance; IAS 1 requires completion on or before the reporting date.",
        ),
    ],
}


# 保留 Official Access，并用深度技术精要替换原本的单条核心摘要与单条简短差异，实现完全幂等
def main() -> int:
    data = json.loads(US_GAAP_JSON.read_text(encoding="utf-8"))
    enriched_docs = 0
    total_sections = 0

    for d in data["documents"]:
        code = d.get("code", "")
        if code not in TECHNICAL_MODULES:
            continue
        modules = TECHNICAL_MODULES[code]
        overview_arts = [a for a in d.get("articles", []) if a.get("no") == "Overview"]
        access_arts = [a for a in d.get("articles", []) if a.get("no") == "Official Access"]

        new_tech_arts = [
            {"no": no, "heading": heading, "text": text, "seq": 0}
            for no, heading, text in modules
        ]
        merged = overview_arts + new_tech_arts + access_arts
        for idx, art in enumerate(merged):
            art["seq"] = idx
        d["articles"] = merged
        enriched_docs += 1
        total_sections += len(new_tech_arts)

    US_GAAP_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Enriched {enriched_docs} flagship US GAAP standards with {total_sections} paragraph-indexed technical sections.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
