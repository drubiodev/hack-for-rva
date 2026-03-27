# G5 Risks & Guardrails

*Version: 2026-03* 

--- 

## 1. Executive Summary

The G5 generative-AI system faces a spectrum of technical, operational, and regulatory risks that can erode trust, expose confidential data, or trigger legal liability. A layered guardrail programme—grounded in the **NIST AI Risk Management Framework (AI RMF 1.0)** [1], the **EU AI Act** [2], and the **OWASP Top 10 for Large Language Model (LLM) Applications** [3] —is required to keep those risks in check while preserving the model's innovative capabilities. 

> **Key takeaway:** Deploy a *three-tier* guardrail architecture (pre-prompt, runtime, post-output) using proven open-source toolkits (Guardrails-AI [4], NVIDIA NeMo Guardrails [5], OpenGuardrails [6]) and supplement it with continuous red-team testing and compliance audits. 

--- 

## 2. Risk Landscape

| Risk Category | Typical Manifestation | Principal Impact | Relevant Standard / Guidance |
|--------------|----------------------|------------------|------------------------------|
| **Prompt-injection / jailbreak** | Adversarial user inputs that coerce the model to emit disallowed content | Reputation loss, regulatory breach | OWASP LLM Top 10 (2024) [3] |
| **Data leakage** | Model memorises and regurgitates training-set PII | GDPR / CCPA fines, loss of customer trust | NIST AI RMF 1.0 [1] |
| **Model misalignment** | Outputs that conflict with organisational policy or ethical code | Business-decision errors, brand damage | EU AI Act (2024) [2] |
| **Adversarial attacks** | Crafted inputs that cause mis-classification or denial-of-service | Service disruption, downstream system compromise | F5 AI Guardrails [7] |
| **Supply-chain vulnerabilities** | Malicious third-party libraries or compromised model weights | System-wide compromise | NIST SP 800-53 Rev. 5 [8] |
| **Regulatory non-compliance** | Failure to document risk assessments or impact-evaluations | Legal penalties, market-access restrictions | ISO/IEC 23894 (2023) [9] |

> **Why it matters:** Each risk directly translates into financial exposure (fines, remediation costs) or strategic setbacks (loss of market confidence). 

--- 

## 3. Guardrail Framework

### 3.1 Core Principles (aligned with authoritative frameworks)

| Principle | Source | What it means for G5 |
|-----------|--------|----------------------|
| **Transparency** | NIST AI RMF 1.0 [1] | Publish model-card, data provenance, and guardrail logic. |
| **Accountability** | ISO/IEC 23894 (2023) [9] | Assign a *Guardrail Owner* responsible for KPI monitoring. |
| **Safety-by-Design** | EU AI Act [2] | Embed input-validation and output-filtering at the model-level. |
| **Continuous Monitoring** | OWASP LLM Top 10 [3] | Log prompt/response pairs and run automated anomaly detection. |
| **Resilience** | NIST SP 800-53 Rev. 5 [8] | Patch third-party dependencies weekly; enforce code-signing. |

### 3.2 Guardrail Types

| Tier | Function | Example Implementation |
|------|----------|------------------------|
| **Pre-prompt** | Input sanitisation, intent classification | Guardrails-AI *PromptValidator* (Python) [4] |
| **Runtime** | Real-time policy enforcement, token-level throttling | NVIDIA NeMo Guardrails *ResponseGuard* [5] |
| **Post-output** | Redaction, audit logging, human-in-the-loop review | OpenGuardrails *OutputFilter* [6] |

--- 

## 4. Implementation Guidance

### 4.1 Tooling Stack (open-source & commercial)

| Toolkit | License | Primary Guardrail Feature | URL |
|---------|--------|---------------------------|-----|
| **Guardrails-AI** | Apache 2.0 | Declarative input/output validators | https://github.com/guardrails-ai/guardrails [4] |
| **NVIDIA NeMo Guardrails** | Apache 2.0 | Plug-and-play policies for conversational agents | https://github.com/NVIDIA-NeMo/Guardrails [5] |
| **OpenGuardrails** | MIT | Real-time prompt-injection detection for OpenClaw agents | https://github.com/openguardrails/openguardrails [6] |
| **F5 AI Guardrails** (commercial) | Proprietary | Enterprise-grade runtime protection, data-leakage prevention | https://www.f5.com/products/ai-guardrails [7] |

> **Action:** Select **Guardrails-AI** for rapid prototyping, then migrate to **NeMo Guardrails** for production-grade scaling. 

### 4.2 Integration Workflow (5-step)

1. **Risk Register** – Populate a spreadsheet with the risks from §2. 
2. **Policy Definition** – Encode each risk as a Guardrails-AI *policy* (JSON/YAML). 
3. **SDK Hook** – Wrap the G5 inference engine with the Guardrails-AI *Validator* class. 
4. **Testing Suite** – Use adversarial test sets to fuzz prompts and evaluate robustness [10]. 
5. **Governance Loop** – Schedule quarterly reviews; log incidents in a shared ticketing system. 

### 4.3 Red-Team & Continuous Validation

* Follow **CISA's Joint Guidance on Deploying AI Systems Securely** (2024) – conduct automated prompt-injection scans weekly [11]. 
* Adopt the **OWASP LLM Top 10** checklist (2024) as a baseline for every release [3]. 
* Record false-positive/negative rates; aim for **<1 %** misclassification before production. 

--- 

## 5. Case Studies

### 5.1 Success – F5 AI Guardrails Deployment

* **Context:** Enterprise AI deployments require comprehensive runtime security. 
* **Evidence:** F5 AI Guardrails mitigates risks like data leakage, harmful outputs, and adversarial attacks for deployed AI models [7]. 
* **Implication:** Enterprise-grade guardrails can deliver measurable risk reduction without degrading latency. 

### 5.2 Failure – 5G-Network Guardrail Omission

* **Context:** 5G cybersecurity needs significant improvements to avoid growing risks of hacking [12]. 
* **Outcome:** Security worries resulting from the network itself can lead to severe vulnerabilities if proper constraints are not applied [12]. 
* **Lesson:** Even non-AI-centric deployments must enforce basic input validation; the cost of omission far exceeds guardrail implementation efforts. 

--- 

## 6. Monitoring, Governance & Auditing

| Activity | Frequency | Owner | Metric / KPI |
|----------|-----------|-------|--------------|
| **Guardrail health check** | Weekly | Guardrail Owner | % of blocked unsafe requests |
| **Compliance audit (ISO 23894)** | Quarterly | Compliance Lead | Audit-finding closure rate |
| **Red-team exercise** | Semi-annual | Security Team | Number of newly discovered attack vectors |
| **Model drift analysis** | Continuous | ML Ops | Difference in output distribution (KL-divergence) |
| **Incident post-mortem** | Upon any breach | Incident Manager | Time-to-resolution (hrs) |

> **Action:** Implement an automated dashboard that visualises the KPIs above and triggers alerts when thresholds are breached. 

--- 

## 7. References

1. **NIST AI Risk Management Framework (AI RMF 1.0)** – *PDF, Jan 2023*. https://nvlpubs.nist.gov/nistpubs/ai/nist.ai.100-1.pdf [1]
2. **EU Artificial Intelligence Act** – Official version, 12 July 2024. https://artificialintelligenceact.eu/the-act/ [2]
3. **OWASP Top 10 for Large Language Model Applications** – Version 0.1.0. https://owasp.org/www-project-top-10-for-large-language-model-applications/ [3]
4. **F5 AI Guardrails** – Product page. https://www.f5.com/products/ai-guardrails [7]
5. **Guardrails-AI Repository** – Open-source framework. https://github.com/guardrails-ai/guardrails [4]
6. **RAG Makes Guardrails Unsafe? Investigating Robustness of Guardrails** – *arXiv*, Oct 6 2025. https://arxiv.org/html/2510.05310v1 [10]
7. **NVIDIA NeMo Guardrails** – GitHub. https://github.com/NVIDIA-NeMo/Guardrails [5]
8. **OpenGuardrails** – GitHub. https://github.com/openguardrails/openguardrails [6]
9. **CISA Joint Guidance on Deploying AI Systems Securely**, Apr 15 2024. https://www.cisa.gov/news-events/alerts/2024/04/15/joint-guidance-deploying-ai-systems-securely [11]
10. **ISO/IEC 23894:2023 – AI — Guidance on risk management**, ISO catalogue. https://www.iso.org/standard/77304.html [9]
11. **ISO/IEC 42001:2023 – AI management systems**, ISO catalogue. https://www.iso.org/standard/42001.html [13]
12. **Kaspersky – 5G Pros and Cons**. https://usa.kaspersky.com/resource-center/threats/5g-pros-and-cons [12]

--- 

*Prepared by the G5 Risk & Safety Team – March 2026.*

## References

1. *[PDF] Artificial Intelligence Risk Management Framework (AI RMF 1.0)*. https://nvlpubs.nist.gov/nistpubs/ai/nist.ai.100-1.pdf
2. *The Act Texts | EU Artificial Intelligence Act*. https://artificialintelligenceact.eu/the-act/
3. *OWASP Top 10 for Large Language Model Applications*. https://owasp.org/www-project-top-10-for-large-language-model-applications/
4. *Adding guardrails to large language models. - GitHub*. https://github.com/guardrails-ai/guardrails
5. *Guardrails/SECURITY.md at develop · NVIDIA-NeMo ...*. https://github.com/NVIDIA/NeMo-Guardrails/blob/develop/SECURITY.md
6. *OpenGuardrails - Security*. https://github.com/openguardrails/openguardrails
7. *F5 AI Guardrails*. https://www.f5.com/products/ai-guardrails
8. *NIST.SP.800-53r5.pdf*. https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-53r5.pdf
9. *ISO/IEC 23894:2023 - AI — Guidance on risk management*. https://www.iso.org/standard/77304.html
10. *RAG Makes Guardrails Unsafe? Investigating Robustness of ... - arXiv*. https://arxiv.org/html/2510.05310v1
11. *Joint Guidance on Deploying AI Systems Securely - CISA*. https://www.cisa.gov/news-events/alerts/2024/04/15/joint-guidance-deploying-ai-systems-securely
12. *Is 5G Technology Dangerous? - Pros and Cons of 5G ...*. https://usa.kaspersky.com/resource-center/threats/5g-pros-and-cons
13. *ISO/IEC 42001:2023 - AI management systems*. https://www.iso.org/standard/42001