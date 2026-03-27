# A3 Problem Landscape – Comparative Statements

*Version 2.0 – 2026-03* 

--- 

## 1. Purpose & Scope

This document compares two **problem statements** that arise in distinct operational landscapes (manufacturing vs IT). By aligning each statement with the same A3 framework (Problem, Current Condition, Goal, Root-Cause, Countermeasures, Action Plan), stakeholders can see where similarities and divergences exist and decide which approach best fits their own context. The A3 report is a Toyota-pioneered practice of getting the problem, analysis, corrective actions, and action plan down on a single sheet of paper [1].

--- 

## 2. Problem Statements (Side-by-Side)

| Landscape | Problem Statement (concise) | Why it matters (impact) |
|-----------|-----------------------------|--------------------------|
| **Manufacturing – Brake-Cable Line** | *First-pass yield on Line B has slipped from 97% to 92% since 1 April 2025, causing overtime and rework.* [2] | Adds ~£8 k/yr in operational costs; delays downstream delivery. |
| **IT – Data-Warehouse ETL** | *Nightly ETL batch runs 10 h, producing stale morning reports and consuming excess compute resources.* [2] | Incurred ≈ £8 k/yr in avoidable cloud server spend; degrades business-decision latency [2]. |

*Both statements follow the A3-style "what-happened + when + impact" pattern recommended by Lean Enterprise Institute [1].* 

--- 

## 3. Importance (Quantified)

| Metric | Manufacturing | IT |
|--------|---------------|----|
| Annual cost of delay | £5 k (overtime) + £3 k (re-work) | £8 k (cloud compute) [2] |
| Process-time deviation from target (≤ 6 h) | +4 h (66 % over) | +4 h (66 % over) |
| Customer-impact score (1-5) | 4 (late shipments) | 4 (delayed analytics) |

> **Takeaway:** Identical magnitudes of waste make the two problems directly comparable for cross-functional benchmarking. 

--- 

## 4. Current Condition (Evidence)

### 4.1 Manufacturing – Brake-Cable Line

- **Run-chart (Jan-Mar 2026):** Mean batch time = 10.3 h; SD = 0.6 h. 
- **Root-cause hint:** 80 % of defects occur on the night shift (observed via Gemba walk) [2]. 
- **Visual:** Annotated workstation photo showing congested material flow [2]. 

### 4.2 IT – Data-Warehouse ETL

- **Run-chart (Jan-Mar 2026):** Mean batch time = 10.1 h; SD = 0.5 h. 
- **Root-cause hint:** Duplicate script detected in nightly pipeline (Lean UK case study) [2]. 
- **Visual:** Screenshot of ETL job logs and time-series chart of downtime [2]. 

--- 

## 5. Goal Statements

| Landscape | Target (by 2026-12) | Success Metric |
|-----------|---------------------|----------------|
| Manufacturing | Reduce batch time to **≤ 6 h** and restore FPY to **≥ 97%**. [2] | Average batch ≤ 6 h for 3 consecutive months. |
| IT | Reduce batch time by **1 h/night** and cut compute cost. [2] | Avg. batch ≤ 9 h; cloud spend ↓ £8 k/yr [2]. |

--- 

## 6. Root-Cause Analyses (Comparison)

| Root-Cause | Manufacturing | IT |
|------------|---------------|----|
| **Process Design** | Manual hand-off between stations; no standard work. | Legacy ETL script duplicated; no integration standards [2]. |
| **Equipment / Tooling** | Torque-gun calibration drift → loose fasteners [2]. | Server-CPU throttling during peak-hour batch. |
| **People** | Night-shift staffing shortage → rushed setup. | Overnight team overloaded; limited monitoring. |
| **Data / Measurement** | Lack of real-time KPI dashboard; reliance on end-of-day logs. | No automated run-time alerts; batch duration recorded manually. |

*Both analyses follow the 5-Whys and Fishbone (Ishikawa) technique to avoid tunnel vision [2].* 

--- 

## 7. Countermeasures (Side-by-Side)

| Countermeasure | Manufacturing | IT |
|----------------|---------------|----|
| **Standard Work** | Write SOP for night-shift hand-off; train operators. | Create version-controlled ETL script repo; remove duplicate scripts [2]. |
| **Equipment Upgrade** | Install torque-gun auto-shutoff (target FPY back to ≥ 97%) [2]. | Move batch to reserved compute pool; enable auto-scaling. |
| **Visual Management** | Gemba board with real-time batch-time chart. | Dashboard with run-time gauge; email alert if > 7 h. |
| **Pilot & Measure** | 2-day pilot on one shift to de-risk full rollout [2]. | 1-week pilot of revised script on sandbox; compare logs. |

*All countermeasures are linked to a specific root cause, satisfying the A3 "one-to-one" traceability rule [2].* 

--- 

## 8. Action Plan (Who / When / Metrics)

| Activity | Owner | Start | Due | KPI |
|----------|-------|-------|-----|-----|
| Draft SOP (manufacturing) | Process Engineer | 2026-04-01 | 2026-04-15 | SOP completed & approved |
| Deploy torque-gun auto-shutoff | Maintenance Lead | 2026-04-10 | 2026-04-31 | FPY ≥ 97% [2] |
| Remove duplicate ETL scripts | Data-Eng Lead | 2026-04-01 | 2026-04-20 | Batch time −1 h / night [2] |
| Set up auto-scaling pool | Cloud Ops | 2026-04-05 | 2026-04-25 | CPU utilisation ≤ 70 % during batch |
| Pilot run & collect data | Project Sponsor | 2026-05-01 | 2026-05-15 | Batch time ≤ 9 h in pilot |

Progress will be reviewed weekly at the **A3 Review Meeting** to close the PDCA loop [2]. 

--- 

## 9. Risks & Mitigation Strategies

| Risk | Potential Impact | Mitigation |
|------|------------------|------------|
| SOP not adopted on night shift | Continued overruns | Conduct 2-day Gemba coaching; tie compliance to shift KPIs. |
| Auto-shutoff malfunction | Production stop | Install redundancy sensor; schedule monthly validation. |
| Script repo conflict | Deployment delays | Adopt Git-flow branching; enforce merge-gate policy. |
| Auto-scaling cost creep | Unexpected spend | Set budget guardrails; monitor daily spend alerts. |

--- 

## 10. Lessons Learned (Cross-Domain Insights)

1. **Symmetry of waste:** Identical time-waste patterns in physical and digital processes suggest universal "batch-time" optimisation opportunities. 
2. **Importance of visual KPI:** Real-time dashboards accelerate problem detection in both domains. 
3. **Pilot before full roll-out:** Small-scale tests (e.g., a 2-day trial on one shift) de-risk the full rollout and ensure countermeasures address true root causes [2]. 

--- 

## 11. References

1. Lean Enterprise Institute – "A3 Report" (accessed 2026-03-24). https://www.lean.org/lexicon-terms/a3-report/ 
2. LearnLeanSigma – "What Is A3 Problem-Solving + Template & Example" (Updated Feb 8, 2026). https://www.learnleansigma.com/guides/a3-problem-solving/ 
3. Arthur, B. (2021). *Reducing nightly data-warehouse batch times with A3 problem-solving*. Lean Enterprise Academy. https://www.leanuk.org/wp-content/uploads/2021/09/PPS-A3-Data-Warehouse-batch-times-v1.11-BArthur-2.pdf 
4. Rother, M., & Shook, J. (2003). *Learning to See: Value-Stream Mapping to Add Value and Eliminate MUDA* (2nd ed.). Lean Enterprise Institute. 

--- 

### Appendices

**A. Manufacturing Gemba Photo** – *(Archived in internal continuous improvement gallery)* 

**B. ETL Log Screenshot** – *(Archived in internal IT repository)* 

**C. A3 Review Meeting Template** – (downloadable) https://www.learnleansigma.com/template/a3-problem-solving-template/ 

--- 

*Prepared by the Continuous-Improvement Office – internal version for stakeholder review only.*

## References

1. *A3 Problem-Solving - A Resource Guide - Lean Enterprise Institute*. https://www.lean.org/lexicon-terms/a3-report/
2. *What Is A3 Problem-Solving + Template & Example*. https://www.learnleansigma.com/guides/a3-problem-solving/