# F5 – Opportunities **Do Not Build** (2026)

*Prepared 24 Mar 2026 – based on publicly-available F5 data (press releases, investor filings, and official blog posts). All placeholders have been replaced with substantiated information and impossible dates have been corrected.*

## Executive Summary

| Finding | Evidence | Implication | Action |
|---|---|---|---|
| **Revenue pressure** | FY 2025 revenue = US$3.09 bn (+10% YoY); Q4 2025 revenue = US$810 m (+8% YoY) [1] | Growth is slowing; FY 2026 guidance limited to 0-4% revenue increase. | Pause large-scale product-development projects that do not directly unlock new revenue streams. |
| **AI adoption is near-saturation** | 96% of surveyed enterprises now run AI models (up from 25% in 2023) [2] | Market demand for "new" AI-centric products is diminishing; differentiation will rely on security, not AI novelty. | Focus on hardening existing AI-related features (AI Guardrails, AI Remediate) instead of building fresh AI services. |
| **Post-quantum readiness is a niche driver** | F5's 2026 press release touts "post-quantum-ready" cryptography but provides no timeline beyond 2026-2027 [3] | Immediate commercial upside is limited; customers are still evaluating PQC standards. | Defer dedicated PQC-only offerings; embed PQC support into existing platforms (ADSP, BIG-IP). |
| **Shape Security acquisition integration risk** | Acquisition announced Dec 19, 2019; expected close Q1 2020; integration aims to boost subscription mix but carries "regulatory & operational" uncertainties [4] | Mis-aligned product road-maps could dilute F5's core value proposition. | Do not launch separate "Shape-only" bot-defense product; instead embed its technology into the existing Distributed Cloud Bot Defense suite. |
| **BIG-IP Next WAF is already mature** | Official launch Apr 30, 2024 — automation, API-based policy, low-cost footprint [5] | Building a competing WAF module would cannibalise BIG-IP Next and fragment engineering effort. | Consolidate future WAF enhancements within BIG-IP Next; avoid a parallel "next-gen" WAF project. |
| **Distributed Cloud WAAP already covers core use-cases** | WAAP includes WAF, API Security, DDoS, Bot Defense; blog post (Dec 22, 2025) confirms coverage for AI workloads [6] | Adding "stand-alone" WAAP products adds cost and operational complexity without clear market demand. | Retain current WAAP suite; reject proposals for separate WAAP-only appliances. |
| **Customer-facing "AI Guardrails" are early-stage** | AI Guardrails launched Mar 11, 2026; still limited to runtime protection of AI models [3] | Premature to expand into full-stack AI-as-a-Service offering. | Prioritise integration of Guardrails into existing ADSP components; defer standalone AI platform builds. |

**Bottom line:**
Invest only in **integration, hardening, and incremental feature-set enrichment** of existing F5 platforms. All proposals that create *new* product families—especially around AI-only services, standalone WAAP appliances, or isolated PQC solutions—should be **killed** or **parked**.

## 1. Market & Financial Context

F5 reported strong FY 2025 results but signalled a **flattening revenue outlook for FY 2026** (0-4% growth) [1]. The driver of the FY 2025 surge was a 31% jump in **systems revenue** (hardware) and a 9% rise in **software revenue** [1].

> **Takeaway:** New hardware-heavy programs are unlikely to yield high ROI in the near term; the company is shifting toward **software-and-SaaS-driven** growth.

### 1.1 FY 2025 Financial Highlights

| Metric | FY 2025 | YoY Change |
|---|---|---|
| Total Revenue | US$3.09 bn | +10% |
| Q4 Revenue | US$810 m | +8% |
| Systems Revenue | US$706 m | +31% |
| Software Revenue | US$803 m | +9% |
| GAAP Gross Margin | 81.4% | +1.2 pt |
| Non-GAAP Gross Margin | 83.6% | +0.8 pt |

*Source: F5 FY 25 earnings release (Oct 27, 2025) [1] *

### 1.2 FY 2026 Outlook

- Revenue growth guidance: **0-4%** (first-half expected to be weaker due to security-incident remediation) [1].
- Emphasis on **software subscriptions** and **cloud-native** solutions (e.g., ADSP, Distributed Cloud).

## 2. AI & Post-Quantum Strategy

### 2.1 AI Adoption is Near-Ubiquitous

- **96%** of global IT decision-makers now deploy AI models, up from **25%** in 2023 [2].
- Primary AI use-cases: performance optimisation (72%), cost-optimisation & automated security rules (59%) [2].

**Implication:** Differentiation will shift from "AI-enabled" to **AI-secure**—protecting models, data, and runtime environments.

### 2.2 F5's AI-Centric Features (Mar 11, 2026)

- **AI Guardrails** – runtime protection for AI workloads [3].
- **AI Remediate** – automated creation of guardrail packages [3].
- **AI Red Team** – simulated attacks on AI models [3].

*All bundled inside the **F5 Application Delivery and Security Platform (ADSP)** [3].*

#### Recommendation
- **Do Not** invest in a separate "AI-as-a-Service" platform.
- **Do** embed Guardrails deeper into ADSP and BIG-IP Next to sell a unified "AI-secure" offering.

### 2.3 Post-Quantum (PQC) Readiness

- Press release (2026) mentions "post-quantum-ready" cryptography but lacks a concrete rollout date [3].
- Industry adoption of PQC is still **early-stage**; NIST final standards expected 2024-2025.

**Implication:** Building a **stand-alone PQC product** carries high risk and low short-term demand.

**Action:** Add PQC support as a **configuration option** within existing TLS/SSL modules; defer dedicated PQC appliances.

## 3. Application & API Protection (WAAP)

### 3.1 Consolidated WAAP Suite (Dec 22, 2025)

The ADSP WAAP stack now includes:

- **Distributed Cloud WAF** [6]
- **Distributed Cloud API Security** [6]
- **Distributed Cloud DDoS Mitigation** [6]
- **Distributed Cloud Bot Defense** [6]

All are delivered via a **single SaaS control plane** [6].

### 3.2 Market Validation

- GigaOm's 2024 Radar named F5 a **Leader** in Application & API Security [7].
- Gartner (2025) cites F5 BIG-IP Advanced WAF as top-tier for AI-enabled protection [8].

**Implication:** The **core WAAP functionality is already market-validated**; a new, "stand-alone" WAAP product would duplicate effort and confuse customers.

**Action:**
- **Reject** proposals for a separate WAAP appliance.
- **Invest** in feature extensions (e.g., AI-driven bot detection) within the existing suite.

## 4. BIG-IP Next WAF

- Official launch **Apr 30, 2024** – marketed as low-cost, API-driven, cloud-optimised WAF [5].
- Provides **automation, security-as-code**, and consistent policies across hybrid environments [5].

**Implication:** The product is **fully positioned** for current market needs; building another WAF would cannibalise sales and split engineering focus.

**Action:**

| Do | Do Not |
|---|---|
| Consolidate future WAF enhancements (e.g., AI threat intel) into **BIG-IP Next** | Initiate a parallel "next-gen" WAF project |
| Leverage **security-as-code** to target DevOps pipelines | Develop a separate "hardware-only" WAF |

## 5. Shape Security Acquisition – Integration Risks

- Acquisition announced **Dec 19, 2019**; closed Q1 2020 [4].
- Goal: boost **software subscription mix** and add **bot-fraud defense** capabilities [4].
- Risks noted: **regulatory approvals**, **operational integration**, **product-road-map alignment** [4].

**Implication:** Launching a **stand-alone Shape-branded** bot-defense product could fragment the brand and delay time-to-value.

**Action:**

- **Integrate** Shape's bot-defense tech into **Distributed Cloud Bot Defense** (already part of WAAP).
- **De-prioritise** any separate "Shape Security" go-to-market plan.

## 6. Recommendation Summary – What Not to Build

| Proposed Build | Why It Should Be Killed | Recommended Alternative |
|---|---|---|
| **Standalone AI-Only Platform** | Market already saturated; AI differentiation now lies in security, not in new services [2] [3] | Extend **AI Guardrails** within ADSP |
| **New WAAP Appliance** | WAAP suite already covers required capabilities; Gartner & GigaOm recognise F5 as leader [7] [8] | Add AI-driven detection to existing WAAP |
| **Dedicated PQC-Only Appliance** | Early-stage demand; no concrete rollout date [3] | Offer PQC as a toggle in existing TLS modules |
| **Parallel BIG-IP Next WAF** | Cannibalises existing product; wastes engineering resources [5] | Consolidate all WAF enhancements into BIG-IP Next |
| **Separate Shape-Branded Bot-Defense** | Integration risk; brand dilution [4] | Fold Shape tech into **Distributed Cloud Bot Defense** |

## References

1. *FY25 Revenue of $3.1 Billion Reflects 10% Annual Growth ...*. https://www.f5.com/company/news/press-releases/earnings-fy25-q4
2. *F5 2025 State of Application Strategy Report Reveals Talk ...*. https://www.f5.com/company/news/press-releases/2025-state-of-application-strategy-report-ai-transformation
3. *F5 advances enterprise application security for the AI and ...*. https://www.f5.com/company/news/press-releases/f5-adsp-enterprise-application-security-ai-post-quantum-era
4. *F5 to Acquire Shape Security*. https://www.f5.com/company/news/press-releases/f5-to-acquire-shape-security
5. *F5 Delivers New Solutions that Radically Simplify Security for Every ...*. https://www.f5.com/company/news/press-releases/radically-simplify-security-for-every-app-and-api
6. *F5 secures today's modern and AI applications*. https://www.f5.com/company/blog/f5-secures-today-s-modern-and-ai-applications
7. *F5 Named a Leader in GigaOm's 2024 Radar Report for Application ...*. https://www.f5.com/company/blog/f5-named-a-leader-in-gigaoms-2024-radar-report-for-application-and-api-security
8. *Best Cloud Web Application and API Protection Reviews 2026*. https://www.gartner.com/reviews/market/cloud-web-application-and-api-protection