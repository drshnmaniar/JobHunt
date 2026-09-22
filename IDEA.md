# Job Application Flow & End-to-End Tracking System

Design notes. The executable runbook is [PROMPTS.md](PROMPTS.md). Status values, paths, and the approval gate are defined in [ORCHESTRATOR.md](ORCHESTRATOR.md). If this file disagrees with those two, those two win.

A local, agent-run workflow: capture a pasted job description, tailor an ATS resume from `candidate_profile.md` without inventing facts, compile one PDF, and track the packet in `APPLICATIONS_TRACKER.md`. Nothing is `READY_TO_APPLY` until the user approves that APP-ID.

---

## 1. End-to-End Workflow Pipeline

```
  +------------------+
  |  1. Job Capture  |  --> Paste JD text / URL / company details
  +--------+---------+
           |
           v
  +------------------+
  |  2. AI Parsing   |  --> Extract skills, requirements, keywords & ATS criteria
  +--------+---------+
           |
           v
  +------------------+
  | 3. Tailor Resume |  --> Match Master Profile against JD; optimize summary & bullets
  +--------+---------+
           |
           v
  +------------------+
  |  4. PDF Generate |  --> Clean, ATS-compliant PDF rendered and version-locked
  +--------+---------+
           |
           v
  +------------------+
  |  5. Apply & Log  |  --> Application submitted; PDF + JD snapshot archived
  +--------+---------+
           |
           v
  +------------------+
  | 6. Track & Check |  --> Dynamic checklist, Kanban status board, follow-up alerts
  +------------------+
```

---

## 2. Detailed Lifecycle Stages & Status Machine

Each job application moves through distinct stages with automated status updates and action checklists:

Statuses are a single column. See ORCHESTRATOR.md. There is no separate Pipeline Stage / Activity Status pair.

| Status | When |
| :--- | :--- |
| `TRIAGE` | JD snapshot saved. Eligibility not decided. |
| `REJECTED_AT_TRIAGE` | Hard mismatch. Stop. |
| `DRAFT` | Tailoring. Not sendable. |
| `IN_REVIEW` | PDF compiled and `verify_ats.py` printed `VERIFICATION PASSED`. Waiting for the user. |
| `READY_TO_APPLY` | User explicitly approved this APP-ID. |
| `APPLIED` | Submitted. Date recorded. |
| `SCREENING` / `INTERVIEWING` / `OFFER` / `ACCEPTED` / `REJECTED` | After submission. |

Hard eligibility (location, work authorization, seniority) is a human check against `candidate_profile.md`. `scripts/assess_fit.py` is advisory and must not be reported as a match percentage or used as the halt condition.

---

## 3. Core System Modules

### A. Job Ingestion
- Input: pasted JD text, plus company and role. No scraping in v1.
- Output: one markdown snapshot under `job_descriptions/` and one tracker row. Not JSON.

### B. Master Profile & Traceability Engine
- **Master Profile Repository**: A unified Markdown file storing:
  - Contact details, summary options.
  - Comprehensive work history. **Every single achievement bullet has a stable, unique ID (e.g., `[ACH-042]`)**.
- **Tailoring Engine**:
  - Selects relevant `[ACH-ID]`s based on JD keywords.
  - Forces an explicit internal mapping from generated resume bullet to source `[ACH-ID]` to prevent hallucinated claims.

### C. PDF Generation & ATS Verification
- Modern, clean PDF renderer (via programmatic Python injection + pdflatex).
- **ATS check** (`scripts/verify_ats.py`): exactly one page, selectable text, email matches `candidate_profile.md`, and the words summary, experience, and education are present. A missing `pypdf` install is a failure, not a pass. Section order is not enforced: a student-first resume may put experience before skills.

### D. Application Tracking
- One board: `APPLICATIONS_TRACKER.md`. One status column. Checklists are section 3 of that file, not separate checklist files.
- Files use `yyyy_mm_dd_APP-[ID]_...` so a later application does not overwrite an earlier one.

---

## 4. Agent-Native Data Formats (Markdown-First)

Working with AI agents makes **pure Markdown** (or **Markdown with YAML frontmatter**) vastly superior to JSON:
- **Zero syntax friction**: No escaping quotes, trailing comma errors, or bracket nesting when you edit your profile.
- **Agent-native comprehension**: LLMs read, generate, and diff Markdown headings and bullet points far more reliably and token-efficiently than deeply nested JSON.
- **Built-in Checklist support**: Markdown native task lists (`- [ ]`, `- [x]`) can be read, checked off, and updated directly by you or the agent.
- **Easy version control**: Clean git diffs for every job application and resume iteration.

The sample below is an illustration of the markdown shape, not a second storage layout. Live packets are flat files plus one tracker row. Do not create `applications/`.

### 1. Illustrative application note (not the live path)
```markdown
---
id: app_2026_001
company: TechCorp
role: Senior Full Stack Engineer
job_url: https://careers.techcorp.com/jobs/123
location: Remote (US/EU)
salary: $140k - $165k
status: APPLIED
applied_date: 2026-09-14
resume_pdf: resumes/TechCorp_Senior_Full_Stack_Resume.pdf
---

## Action Checklist
- [x] Tailor resume keywords and metrics against JD
- [x] Submit application via official portal
- [ ] Connect with hiring manager / recruiter on LinkedIn (Due: 2026-09-21)
- [ ] Prepare talking points on distributed event streams

## Job Description Snapshot
Senior Full Stack Engineer needed to lead event-driven microservices...
Required: TypeScript, React, Node.js, PostgreSQL, Docker. 5+ years experience.

## Interview & Follow-up Notes
- Met recruiter Sarah at virtual career fair. Referral from John D.
- 2026-09-14: Submitted application.
```

### 2. Master Profile (`master_profile.md`)
```markdown
# Alex Candidate
- **Email:** alex@example.com | **Phone:** +1 234 567 8900 | **Location:** Berlin, Germany
- **Links:** [LinkedIn](https://linkedin.com/in/alex) | [GitHub](https://github.com/alex) | [Portfolio](https://alex.dev)

## Summary
Senior Full Stack Engineer with 7+ years of experience building high-scale distributed systems and resilient web platforms...

## Core Skills
- **Languages:** TypeScript, Python, Go, SQL
- **Frameworks:** React, Next.js, Node.js, Express, FastAPI
- **Cloud & Infrastructure:** AWS, Docker, Kubernetes, CI/CD, Terraform

## Work Experience

### Staff Engineer | PrevTech *(2022-01 - Present)*
- **[ACH-001]** Architected event-driven microservices handling 20M+ daily events using Kafka, Node.js, and Redis. *(Tags: #backend, #scaling, #kafka)*
- **[ACH-002]** Reduced P99 API latency by 42% through query optimization and distributed caching in PostgreSQL. *(Tags: #performance, #database)*
- **[ACH-003]** Mentored 8 mid-level engineers and established CI/CD automated test standards across 4 squads. *(Tags: #leadership, #ci-cd)*

### Senior Software Engineer | EarlyStage Inc *(2019-03 - 2021-12)*
- **[ACH-004]** Built customer-facing dashboard in React/Next.js used by 50,000+ monthly active enterprise users. *(Tags: #frontend, #react)*
- **[ACH-005]** Designed REST and GraphQL APIs powering payment integration pipelines. *(Tags: #api, #payments)*
```

---

## 5. Agentic Prompt Loop & File Generation Flow

```
                      +-----------------------------+
                      |   1. candidate_profile.md   |
                      +--------------+--------------+
                                     |
                                     v
+------------------------+     +-------------------------------+
| [company]_[pos]_jd.md  | --> | 2. Recursive Tailoring Prompt |
+------------------------+     |    - Direct skills match      |
                               |    - Transferable / Interest  |
                               |      alignment if skill gaps  |
                               |    - Critique & Refine Loop   |
                               +---------------+---------------+
                                               |
                                               v
                      +------------------------------------------------+
                      | 3. [company]_[position]_resume_content.md      |
                      +------------------------+-----------------------+
                                               |
                                               v
                      +------------------------------------------------+
                      | 4. LaTeX Conversion Prompt                     |
                      |    - Injects content into ATS LaTeX template   |
                      |    - Produces [company]_[position]_resume.tex  |
                      +------------------------+-----------------------+
                                               |
                                               v
                      +------------------------------------------------+
                      | 5. Compile to PDF                              |
                      |    - [company]_[position]_resume.pdf           |
                      |    - Updates job checklist & status            |
                      +------------------------------------------------+
```

### File Hierarchy & Naming Convention (Flat & Categorized)

```
JobHuntSeptemberFlow/
├── candidate_profile.md                      # Master source of truth (all skills, history, projects)
├── APPLICATIONS_TRACKER.md                   # Global tracking sheet for all applications & statuses
├── ORCHESTRATOR.md                           # Orchestrator guide & playbook
├── IDEA.md                                   # Full architecture & prompt specifications
├── job_descriptions/                         # Dedicated folder for all job descriptions
│   ├── yyyy_mm_dd_APP-001_stripe_backend_jd.md
│   └── yyyy_mm_dd_APP-002_google_sre_jd.md
├── resume_contents/                          # Dedicated folder for tailored resume markdown files
│   ├── yyyy_mm_dd_APP-001_stripe_backend_resume_content.md
│   └── yyyy_mm_dd_APP-002_google_sre_resume_content.md
├── output_pdfs/                              # Dedicated folder for output LaTeX and PDFs
│   ├── yyyy_mm_dd_APP-001_stripe_backend_resume.tex
│   ├── yyyy_mm_dd_APP-001_stripe_backend_resume.pdf
│   ├── yyyy_mm_dd_APP-002_google_sre_resume.tex
│   └── yyyy_mm_dd_APP-002_google_sre_resume.pdf
└── templates/
    └── modern_ats_resume.tex                 # Base clean single-page LaTeX template
```

---

## 6. Master Orchestrator Prompt (historical)

Superseded by [PROMPTS.md](PROMPTS.md) Option 7. Kept so older notes remain readable. Do not execute this block if it conflicts with PROMPTS.md. In particular: do not set `READY_TO_APPLY` before approval, and do not write `applications/`.

```markdown
# MASTER ORCHESTRATOR PROMPT: Job Application Tailoring & Tracking

## TRIGGER / USER INPUT:
Company: [e.g. Acme Corp]
Position: [e.g. Senior Backend Engineer]
Job Description: [Pasted JD text or file path]

---

## EXECUTION PROTOCOL:

### PHASE 1: Job Description Initialization
1. Save raw JD to: `job_descriptions/yyyy_mm_dd_APP-[ID]_[company]_[position]_jd.md`
2. Add new row to `APPLICATIONS_TRACKER.md` with:
   - Status: `DRAFT`
   - Initial timestamps and metadata.

### PHASE 2: Candidate Gap Analysis & Recursive Tailoring Loop
1. Read `candidate_profile.md` and `job_descriptions/yyyy_mm_dd_APP-[ID]_[company]_[position]_jd.md`.
2. Execute the **Recursive Tailoring Prompt**:
   - Extract exact skill matches and prioritize corresponding career achievements.
   - For skill gaps: highlight transferable engineering concepts and personal/adjacent projects showing genuine interest and quick learning.
   - Run critique pass: enforce strong impact verbs, quantifiable metrics (XYZ format), and strict 1-page budget.
3. Write result to: `resume_contents/yyyy_mm_dd_APP-[ID]_[company]_[position]_resume_content.md`.

### PHASE 3: LaTeX Generation
1. Read `templates/modern_ats_resume.tex` and `resume_contents/yyyy_mm_dd_APP-[ID]_[company]_[position]_resume_content.md`.
2. Convert markdown into clean, valid LaTeX:
   - Escape all LaTeX special characters (`&`, `%`, `$`, `_`, `#`, `~`, `^`).
   - Fit within a single page geometry (0.55in margins).
3. Write result to: `output_pdfs/yyyy_mm_dd_APP-[ID]_[company]_[position]_resume.tex`.

### PHASE 4: Compilation & Verification
1. Run: `pdflatex -halt-on-error -disable-installer -output-directory=output_pdfs output_pdfs/yyyy_mm_dd_APP-[ID]_[company]_[position]_resume.tex`.
2. Verify PDF generation and page budget (must be exactly 1 page).

### PHASE 5: Global Tracker Sync & Next Actions
1. Update `APPLICATIONS_TRACKER.md`:
   - Change `status` to `READY_TO_APPLY`.
   - Update links: `[JD]`, `[Content]`, `[PDF]`.
   - Update active checklist: check off resume and PDF generation tasks.
   - Set next immediate action: `- [ ] Submit application via company portal (Target: [Date])`.
   - Set follow-up reminder: `- [ ] Recruiter / hiring manager outreach (Target: [Date + 2 days])`.
2. Present the user with:
   - Summary of tailored highlights & interest alignments.
   - Clickable link to `output_pdfs/[company]_[position]_resume.pdf`.
   - Next actions due.
```

---

## 7. The Sub-Prompts


### Stage A: Recursive Tailoring Loop Prompt (`JD + Candidate -> resume_content.md`)

```markdown
**System Role**: You are an expert technical career strategist and executive resume writer.
**Inputs**:
1. `candidate_profile.md`: Complete history, skills, achievements, and projects.
2. `[company]_[position]_jd.md`: Target job description, requirements, and company mission.

**Evaluation & Tailoring Rules**:
1. **Direct Match Extraction**:
   - Identify exact skills, architectures, and tools that appear in both the JD and candidate profile.
   - Front-load these technologies and relevant metrics in the bullet points.
2. **Gap Handling & Interest Alignment**:
   - If the candidate lacks direct experience in a required technology or domain:
     - DO NOT fabricate experience or invent claims.
     - Pivot to transferable patterns: e.g., if JD wants Kafka and candidate has RabbitMQ/Redis Streams, frame as "high-throughput distributed event streaming (Redis/RabbitMQ, architecture transferrable to Kafka)".
     - Emphasize deep curiosity and relevant personal projects, open-source contributions, or adjacent architectural experience demonstrating rapid mastery.
3. **Recursive Critique Loop**:
   - *Pass 1 (Draft)*: Select top 3-4 roles, filter top 3-4 high-impact bullets per role with measurable outcomes (XYZ format: Accomplished [X] as measured by [Y] by doing [Z]).
   - *Pass 2 (Critique)*: Does this fit cleanly within a 1-page budget? Are the top 5 JD keywords present in the first third of the page? Are passive verbs removed?
   - *Pass 3 (Final Polish)*: Output the tailored content into `[company]_[position]_resume_content.md`.
```

### Stage B: LaTeX Generation & PDF Compilation Prompt (`resume_content.md -> .tex -> .pdf`)

```markdown
**System Role**: You are a LaTeX typesetter specialized in high-conversion, ATS-parsable resumes.
**Input**: `[company]_[position]_resume_content.md` and `templates/modern_ats_resume.tex`.

**LaTeX Formatting Directives**:
1. Single-column, clean layout (no dual columns or icons that confuse ATS parsers).
2. Proper escaping of LaTeX special characters (`&`, `%`, `$`, `_`, `#`, `^`, `~`).
3. Strict single-page geometry (`geometry` package with 0.5 - 0.75 in margins).
4. Standard ATS section headings: `\section{Summary}`, `\section{Technical Skills}`, `\section{Work Experience}`, `\section{Projects}`, `\section{Education}`.
5. Save as `output_pdfs/yyyy_mm_dd_APP-[ID]_[company]_[role]_resume.tex` via `scripts/compile_latex.py`. Do not hand-author LaTeX.
6. Compile with `pdflatex` / `xelatex` (or tectonic) to generate `[company]_[position]_resume.pdf`.
```

### Stage C: Automatic Checklist & Status Update

On a passing PDF, set the tracker Status to `IN_REVIEW` and link the JD, content, and PDF. Set `READY_TO_APPLY` only after the user approves that APP-ID. Checklist edits happen in section 3 of `APPLICATIONS_TRACKER.md`.

---

## 7. Implementation Roadmap

1. **Step 1**: Create `candidate_profile.md` template with structured sections (Summary, Skills, Experience with tags, Projects, Education).
2. **Step 2**: Create `templates/modern_ats_resume.tex` (battle-tested, clean, single-page LaTeX template).
3. **Step 3**: Create application runner / prompt workflow (either CLI script, agent workflow, or dashboard) that accepts a company name, position, and JD text, then executes the pipeline.

