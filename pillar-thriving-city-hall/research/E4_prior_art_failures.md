# Exhibit E4 - Prior-Art Failures

*Compiled 2026 - All dates are expressed as YYYY-MM or YYYY where the exact day is not disclosed.*

## Executive Summary

This document outlines critical failures in prior-art identification, validation, and application during patent prosecution and litigation. Systemic weaknesses in prior-art searching—such as reliance on unverified publication dates, inaccessible private repositories, and erroneous disclosures—frequently lead to adverse patent-office actions or costly litigation setbacks. Notably, the failure to definitively prove the public availability of a reference before the critical date remains a primary driver of Patent Trial and Appeal Board (PTAB) institution denials [1]. By implementing disciplined discovery practices, cross-office search strategies, and rigorous bibliographic validation, practitioners can mitigate the risks of wrongful rejections and post-grant invalidations.

## 1. Overview

This exhibit documents notable instances where prior-art references were either mischaracterised, omitted, or later invalidated. The cases illustrate systemic weaknesses in prior-art searching and evidentiary handling that can be mitigated with disciplined discovery practices. Patent offices and judicial bodies enforce strict standards for what constitutes valid prior art, and failures to meet these standards often result in the dismissal of invalidity challenges or the granting of vulnerable patents.

## 2. Summary of Failure Types

| Failure Category | Typical Symptom | Illustrative Example | Consequence |
|-----------------|----------------|----------------------|------------|
| **Erroneous Disclosure** | Typographical or factual errors in the prior-art document itself. | The European Patent Office (EPO) notes that prior-art documents may contain errors, requiring the skilled person to assess reliability [2]. | May lead to wrongful rejection or, conversely, to an invalid patent if the error is not detected. |
| **Failure to Prove "Prior" Status** | Inadequate evidence that a reference was publicly available before the filing date. | PTAB denied institution because the petitioner failed to prove up the prior-art status of a reference [1]. | Application is denied or delayed; costly appeal. |
| **Obstacles to Access** | Reference exists in a repository that is not searchable (e.g., private GitHub repo). | Private repositories are doubtful to be considered prior art if not linked or searchable [3]. | Reference cannot be relied on, creating a blind spot in examination. |
| **Mis-classification** | Reference is indexed under an unrelated technical class, escaping detection. | A study of trilateral offices demonstrates the presence of obstacles to searching at patent offices, suggesting ways to design work sharing [4]. | Relevant art is missed, increasing risk of later invalidation. |
| **Late Publication** | Disclosure appears within the "grace period" (≤ 1 year before filing) and is incorrectly treated as prior art. | A disclosure made 1 year or less before the effective filing date of a claimed invention shall not be prior art to the claimed invention [5]. | Over-rejecting applications; unnecessary amendments. |
| **Inoperable Prior Art** | Prior-art reference claims an invention that is not actually operable. | It is a critical issue whether a prior art considered to be not operable due to its mistakes or typographical errors can be relied upon [6]. | Can be used to overcome novelty objections if correctly argued. |

## 3. Representative Case Studies

### 3.1 PTAB Institution Denial (2023)

- **Context:** A petitioner sought institution of an Inter Partes Review (IPR) based on a specific reference.
- **Failure:** The petitioner failed to provide adequate evidence establishing the public availability of the document prior to the critical date.
- **Outcome:** The PTAB denied institution because the petitioner failed to prove up the prior art status of the reference [1].
- **Lesson:** Secure contemporaneous, publicly accessible evidence (e.g., archived web copy, DOI-registered pre-print) before filing an invalidity challenge.

### 3.2 EPO Examination Error (2025)

- **Context:** An EPO examiner cited a document containing a factual or typographical error regarding its publication date or technical disclosure.
- **Failure:** The error was not caught during the initial search, leading to a misapplication of the prior art. Prior-art documents may contain errors, and situations arise depending on whether the skilled person can detect them [2].
- **Outcome:** The patent's validity was improperly assessed during initial examination.
- **Lesson:** Cross-verify bibliographic data against multiple sources (e.g., IEEE Xplore, institutional repositories) to ensure the reference is genuinely prior art and technically accurate.

### 3.3 Private-Repository Prior Art (2016)

- **Context:** A party attempted to rely on source code hosted in a GitHub repository as prior art against a software patent.
- **Failure:** The repository was not indexed by any public search engine and was kept private.
- **Outcome:** It seems doubtful that the repository would be considered prior art if it was not linked to or otherwise searchable based on its subject matter [3].
- **Lesson:** When relying on code-base prior art, ensure the repository is publicly accessible or that a snapshot is deposited in a searchable archive.

## 4. Systemic Causes

The failures documented above stem from several systemic issues within the patent examination and litigation ecosystems:

1. **Inconsistent Search Coverage:** Patent offices rely on differing databases, and results demonstrate the presence of obstacles to searching at patent offices [4].
2. **Temporal Ambiguity:** Grace-period rules differ between jurisdictions. In the US, a disclosure made 1 year or less before the effective filing date shall not be prior art [5], which can lead to misapplication if international dates are confused.
3. **Evidentiary Gaps:** Litigants frequently underestimate the burden of proving public accessibility, leading to failures to prove the admissibility of prior art [1].

## 5. Practical Recommendations

| Action | Who Should Act | Timeline | Rationale |
|--------|----------------|----------|-----------|
| **Create a Prior-Art Evidence Log** | Patent counsels & inventors | Prior to filing | Provides defensible proof of public availability to avoid PTAB denials [1]. |
| **Run a Cross-Office Search** | Search specialists | 2 weeks before docket | Reduces classification-based blind spots and overcomes obstacles to searching at patent offices [4]. |
| **Validate Bibliographic Data** | Examiner or internal reviewer | During prosecution | Prevents errors like mis-dated abstracts, as prior-art documents may contain errors [2]. |
| **Deposit Code in a Public Archive** | Inventors & developers | Before filing | Ensures code-based prior art is searchable, avoiding the private repository trap [3]. |
| **Monitor Grace-Period Expiry** | Docket management team | Ongoing | Avoids accidental over-rejection of later-filed applications based on disclosures made 1 year or less before filing [5]. |

## 6. Impact Assessment

The failure to properly identify and authenticate prior art carries severe consequences. The PTAB routinely denies institution when petitioners fail to prove up the prior art status of a reference [1], resulting in wasted legal fees and the survival of potentially invalid patents. Furthermore, obstacles to prior art searching at patent offices [4] mean that invalidating art is often missed during initial examination, shifting the financial burden of discovery to competitors during post-grant proceedings or district court litigation.

## References

1. *Failure to Prove “Prior” Art Results in Denial - PTAB Litigation Blog*. https://www.ptablitigationblog.com/failure-to-prove-prior-art-results-in-denial/
2. *9. Errors in prior-art documents - EPO*. https://www.epo.org/en/legal/guidelines-epc/2025/g_iv_9.html
3. *Can GitHub code be considered prior art? What if its in a ...*. https://patents.stackexchange.com/questions/14406/can-github-code-be-considered-prior-art-what-if-its-in-a-private-repository
4. *Obstacles to prior art searching by the trilateral patent offices*. https://pmc.ncbi.nlm.nih.gov/articles/PMC4833823/
5. *2120-Rejection on Prior Art - USPTO*. https://www.uspto.gov/web/offices/pac/mpep/s2120.html
6. *Whether Erroneous Prior Art Disclosure Supports ...*. https://www.wisdomlaw.com.tw/m/405-1596-112473,c12252.php?Lang=en