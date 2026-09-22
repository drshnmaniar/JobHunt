# Job Applications Master Tracker

> **Global Status Sheet**: Central dashboard tracking all job applications, current stages, key dates, generated assets, and upcoming action items.

---

## 1. Pipeline Summary

Counts use the status names in [ORCHESTRATOR.md](ORCHESTRATOR.md). One status column. No second stage/activity pair.

| Status | Count | Notes |
| :--- | :---: | :--- |
| `TRIAGE` | 0 | JD saved, eligibility not decided |
| `REJECTED_AT_TRIAGE` | 0 | Hard mismatch, pipeline stopped |
| `DRAFT` | 0 | Tailoring in progress |
| `IN_REVIEW` | 1 | PDF failed the 1-page check (APP-006) |
| `READY_TO_APPLY` | 2 | Human-approved packet, not yet submitted |
| `APPLIED` | 0 | Submitted |
| `SCREENING` | 0 | Recruiter screen or outreach |
| `INTERVIEWING` | 0 | Interview in progress |
| `OFFER` | 0 | Offer received |
| `ACCEPTED` | 0 | Offer accepted |
| `REJECTED` | 2 | Closed after the pipeline started |
| **Total Tracked** | **5** | Must equal the board row count |

---

## 2. Master Applications Board

| Company | Role | Location | Salary | Status | Match Focus | Date Added | Next Action & Target | Assets |
| :--- | :--- | :--- | :--- | :---: | :--- | :---: | :--- | :--- |
| **Stripe** | Infrastructure & Backend Engineer (Payments Core) | SF / Remote (US) | $175k - $220k | `READY_TO_APPLY` | Go, Ledgers, Distributed Locks, Kafka, Raft | 2026-09-14 | Submit on Stripe portal (Due: 2026-09-14). PDF not in output_pdfs/. | [JD](job_descriptions/2026_09_14_APP-001_stripe_backend_jd.md) · [Content](resume_contents/2026_09_14_APP-001_stripe_backend_resume_content.md) |
| **SAP SE** | Working Student (f/m/d) IT Portfolio Team | Walldorf, Germany (Hybrid) | Student Rate | `READY_TO_APPLY` | React, Python, JavaScript, Data Wrangling, APIs, CI/CD, Executive Dashboards | 2026-09-21 | Submit on SAP portal (Req ID: 460102) | [JD](job_descriptions/2026_09_21_APP-005_sap_working_student_jd.md) · [Content](resume_contents/2026_09_21_APP-005_sap_working_student_resume_content.md) · [PDF](output_pdfs/2026_09_21_APP-005_sap_working_student_resume_content.pdf) · [Letter](output_pdfs/2026_09_21_APP-005_sap_working_student_cover_letter.pdf) |
| **SAP SE** | SAP iXp Intern (f/m/d) Cloud-native App Dev | Walldorf / St. Leon-Rot (Onsite) | Student Rate | `IN_REVIEW` | Node.js, JavaScript, React, Cloud Microservices, AI Tools (Claude Code), CI/CD, SQL | 2026-09-21 | Cut resume to 1 page, re-run verify_ats.py, then approve | [JD](job_descriptions/2026_09_21_APP-006_sap_ixp_intern_jd.md) · [Content](resume_contents/2026_09_21_APP-006_sap_ixp_intern_resume_content.md) · [PDF](output_pdfs/2026_09_21_APP-006_sap_ixp_intern_resume_content.pdf) · [Letter](output_pdfs/2026_09_21_APP-006_sap_ixp_intern_cover_letter.pdf) |
| **Siemens AG** | Working Student (f/m/d) eMobility Software | Erlangen, Germany (Hybrid) | Student Rate | `REJECTED` | Python, SQL, Dashboards, AI Tools, eMobility | 2026-09-14 | Rejection received on 2026-09-21 | [JD](job_descriptions/2026_09_14_APP-003_siemens_working_student_jd.md) · [Content](resume_contents/2026_09_14_APP-003_siemens_working_student_resume_content.md) · [PDF](output_pdfs/2026_09_14_APP-003_siemens_working_student_resume.pdf) |
| **Siemens AG** | Softwareentwickler (w/m/d) Smart Buildings | Karlsruhe, Germany (Hybrid) | TBD (Permanent) | `REJECTED` | C#, .NET, DI/IoC, Clean Code, CI/CD, Angular, Unit Testing | 2026-09-15 | Rejection received on 2026-09-21 | [JD](job_descriptions/2026_09_15_APP-004_siemens_smart_buildings_jd.md) · [Content](resume_contents/2026_09_15_APP-004_siemens_smart_buildings_resume_content.md) · [PDF](output_pdfs/2026_09_15_APP-004_siemens_smart_buildings_resume.pdf) |

---

## 3. Active Checklists & Next Actions

### SAP SE — SAP iXp Intern (f/m/d) Cloud-native Application Development (APP-006)
- **Status**: `IN_REVIEW`
- **Requisition ID**: 458620 | **Location**: Walldorf / St. Leon-Rot, DE (Onsite/Hybrid)
- **Job URL**: [jobs.sap.com](https://jobs.sap.com/search/?q=458620)
- **Checklist**:
  - [x] Ingest & parse JD &rarr; [2026_09_21_APP-006_sap_ixp_intern_jd.md](job_descriptions/2026_09_21_APP-006_sap_ixp_intern_jd.md)
  - [x] Tailor resume content &rarr; [2026_09_21_APP-006_sap_ixp_intern_resume_content.md](resume_contents/2026_09_21_APP-006_sap_ixp_intern_resume_content.md)
  - [x] Tailor cover letter &rarr; [2026_09_21_APP-006_sap_ixp_intern_cover_letter.md](resume_contents/2026_09_21_APP-006_sap_ixp_intern_cover_letter.md)
  - [ ] Compile single-page ATS Resume PDF. Current file is 2 pages: [2026_09_21_APP-006_sap_ixp_intern_resume_content.pdf](output_pdfs/2026_09_21_APP-006_sap_ixp_intern_resume_content.pdf)
  - [x] Compile cover letter PDF &rarr; [2026_09_21_APP-006_sap_ixp_intern_cover_letter.pdf](output_pdfs/2026_09_21_APP-006_sap_ixp_intern_cover_letter.pdf)
  - [ ] Re-run `python scripts/verify_ats.py` and get `VERIFICATION PASSED`
  - [ ] Approve APP-006, then submit on SAP Careers portal
- **Key Talking Points**: Full-stack Node.js & JavaScript, cloud microservices, active AI tool integration (Claude Code), automated testing & CI/CD delivery, Master's enrollment at HHN, commutable Heilbronn to Walldorf.
- **Fit Assessment**: Score: 1.29 (Competitive), Critical Gap Probability: 73% (SAP CAP & UI5 bridged via decoupled REST APIs, relational SQL databases, and enterprise React/Angular architecture).

### SAP SE — Working Student (f/m/d) IT Portfolio Team (APP-005)
- **Status**: `READY_TO_APPLY`
- **Requisition ID**: 460102 | **Location**: Walldorf, DE (Hybrid 3x/week)
- **Job URL**: [jobs.sap.com](https://jobs.sap.com/search/?q=460102)
- **Checklist**:
  - [x] Ingest & parse JD &rarr; [2026_09_21_APP-005_sap_working_student_jd.md](job_descriptions/2026_09_21_APP-005_sap_working_student_jd.md)
  - [x] Tailor resume content &rarr; [2026_09_21_APP-005_sap_working_student_resume_content.md](resume_contents/2026_09_21_APP-005_sap_working_student_resume_content.md)
  - [x] Tailor cover letter &rarr; [2026_09_21_APP-005_sap_working_student_cover_letter.md](resume_contents/2026_09_21_APP-005_sap_working_student_cover_letter.md)
  - [x] Compile single-page ATS Resume PDF &rarr; [2026_09_21_APP-005_sap_working_student_resume_content.pdf](output_pdfs/2026_09_21_APP-005_sap_working_student_resume_content.pdf)
  - [x] Compile cover letter PDF &rarr; [2026_09_21_APP-005_sap_working_student_cover_letter.pdf](output_pdfs/2026_09_21_APP-005_sap_working_student_cover_letter.pdf)
  - [ ] **Submit application on SAP Careers portal** *(Target Date: 2026-09-21)*
  - [ ] **7-day follow-up if no response** *(Target Date: 2026-09-28)*
- **Key Talking Points**: React & Python fullstack experience, real-time dashboarding across 50+ enterprise apps (8h to 15m MTTD), Python/SQL data wrangling & ETL pipelines, cross-platform REST APIs, Master's enrollment at HHN, hybrid availability at Walldorf.
- **Fit Assessment**: Score: 1.69 (Competitive), Critical Gap Probability: 67% (bridged via data wrangling, cross-platform API integration, and executive reporting).

### Stripe — Infrastructure & Backend Engineer
- **Status**: `READY_TO_APPLY`
- **Job URL**: [stripe.com/jobs/payments-core-infra-2026](https://stripe.com/jobs/payments-core-infra-2026)
- **Checklist**:
  - [x] Ingest & parse JD &rarr; [2026_09_14_APP-001_stripe_backend_jd.md](job_descriptions/2026_09_14_APP-001_stripe_backend_jd.md)
  - [x] Tailor resume content &rarr; [2026_09_14_APP-001_stripe_backend_resume_content.md](resume_contents/2026_09_14_APP-001_stripe_backend_resume_content.md)
  - [ ] Compile single-page ATS PDF. No Stripe PDF is in `output_pdfs/`.
  - [ ] **Submit on company portal** *(Target Date: 2026-09-14)*
  - [ ] **LinkedIn outreach to Payments Core hiring manager** *(Target Date: 2026-09-16)*
  - [ ] **7-day follow-up if no response** *(Target Date: 2026-09-21)*
- **Key Talking Points**: 15k tx/sec ledger ingestion, Raft consensus (`minikv`), Redis Redlock duplicate charge prevention.

### Siemens AG — Working Student (f/m/d) eMobility Software
- **Status**: `REJECTED`
- **Job ID**: 519321
- **Checklist**:
  - [x] Ingest & parse JD &rarr; [2026_09_14_APP-003_siemens_working_student_jd.md](job_descriptions/2026_09_14_APP-003_siemens_working_student_jd.md)
  - [x] Tailor resume content &rarr; [2026_09_14_APP-003_siemens_working_student_resume_content.md](resume_contents/2026_09_14_APP-003_siemens_working_student_resume_content.md)
  - [x] Compile single-page ATS PDF &rarr; [2026_09_14_APP-003_siemens_working_student_resume.pdf](output_pdfs/2026_09_14_APP-003_siemens_working_student_resume.pdf)
  - [x] **Application Outcome**: Rejection received (2026-09-21)
- **Key Talking Points**: Python, SQL, Dashboards & AI tools, Master's enrollment in Germany (Hochschule Heilbronn), hybrid availability.

### Siemens AG — Softwareentwickler (w/m/d) Smart Buildings (APP-004)
- **Status**: `REJECTED`
- **Job ID**: 521614
- **Checklist**:
  - [x] Ingest & parse JD &rarr; [2026_09_15_APP-004_siemens_smart_buildings_jd.md](job_descriptions/2026_09_15_APP-004_siemens_smart_buildings_jd.md)
  - [x] Tailor resume content &rarr; [2026_09_15_APP-004_siemens_smart_buildings_resume_content.md](resume_contents/2026_09_15_APP-004_siemens_smart_buildings_resume_content.md)
  - [x] Compile single-page ATS PDF &rarr; [2026_09_15_APP-004_siemens_smart_buildings_resume.pdf](output_pdfs/2026_09_15_APP-004_siemens_smart_buildings_resume.pdf)
  - [x] **Application Outcome**: Rejection received (2026-09-21)
- **Key Talking Points**: C# primary language (7+ yrs), DI/IoC in .NET 8 microservices, CI/CD across 200+ apps, Angular modernization, real-time monitoring across 50+ global systems, Clean Code standards leadership.

---

## 4. Status Transition Guide

Allowed values are only those in [ORCHESTRATOR.md](ORCHESTRATOR.md). `READY_TO_APPLY` requires an explicit approval of that APP-ID.

- *"Approve APP-006"* → `READY_TO_APPLY`.
- *"Mark Stripe as applied today"* → `APPLIED`, record the date, add a 7-day follow-up.
- *"Scheduled recruiter screen with Stripe for Friday"* → `SCREENING`.

