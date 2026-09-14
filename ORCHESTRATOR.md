# Master Orchestrator Guide & Execution Playbook

This document defines how to run the automated job application flow. 

---

## Quick Start: How to Run
- **Run for a single job**: Tell the Agent: `Apply to [Company] for [Role]: [Paste JD]`
- **Batch / Mass generation across multiple JDs**: Drop markdown JDs into `job_descriptions/`, then tell the Agent: `Run Option 8: Batch process all pending JDs`.
- **Run individual steps**: Open **[PROMPTS.md](file:///d:/JobApplicationsSeptemberFlow/PROMPTS.md)** to choose from the menu of options (e.g. `Run Option 2 for Stripe` or `Run Option 4 for Stripe`).

---

## 5-Phase Autonomous Pipeline

```
  (User Input: Company, Role, JD)
                 │
                 ▼
     [ PHASE 1: INITIALIZE JD ]
     - Assign unique APP-ID (e.g. APP-001)
     - Save raw JD to: job_descriptions/yyyy_mm_dd_APP-[ID]_[company]_[role]_jd.md
     - Add new entry to APPLICATIONS_TRACKER.md (Status: DRAFT)
                 │
                 ▼
     [ PHASE 1.5: ELIGIBILITY TRIAGE ]
     - Run Triage Check (Location, Auth, Seniority)
     - Halt if mismatch found, mark REJECTED_AT_TRIAGE
                 │
                 ▼
     [ PHASE 2: TRACEABLE TAILORING ]
     - Read candidate_profile.md + job_descriptions/yyyy_mm_dd_APP-[ID]_[company]_[role]_jd.md
     - Extract direct hard skill matches & metrics
     - Map every generated bullet to a source [ACH-ID]
     - Write to: resume_contents/yyyy_mm_dd_APP-[ID]_[company]_[role]_resume_content.md
                 │
                 ▼
     [ PHASE 3: LATEX GENERATION ]
     - Run python scripts/compile_latex.py to automatically escape characters and inject markdown into templates/modern_ats_resume.tex
     - Script handles rendering to: output_pdfs/yyyy_mm_dd_APP-[ID]_[company]_[role]_resume.tex
                 │
                 ▼
     [ PHASE 4: PDF COMPILATION & ATS VERIFY ]
     - compile_latex.py automatically runs pdflatex to generate the PDF
     - Run scripts/verify_ats.py output_pdfs/yyyy_mm_dd_APP-[ID]_[company]_[role]_resume.pdf
     - Verify 1-page PDF and machine readability
                 │
                 ▼
     [ PHASE 5: GLOBAL TRACKER SYNC ]
     - Update APPLICATIONS_TRACKER.md (Decoupled State):
       * Set Pipeline Stage: Applying
       * Set Activity Status: Ready to Apply
       * Link JD, Content, and PDF
```

---

## Workspace Structure (Flat & Categorized)

```
JobApplicationsSeptemberFlow/
├── candidate_profile.md             # Master source of truth (your background)
├── APPLICATIONS_TRACKER.md          # Global status sheet & active checklists
├── ORCHESTRATOR.md                  # Quick-start guide & playbook
├── IDEA.md                          # Full system architecture
├── job_descriptions/                # Dedicated folder for all JDs
│   └── yyyy_mm_dd_APP-001_stripe_backend_jd.md
├── resume_contents/                 # Dedicated folder for generated markdown resumes
│   └── yyyy_mm_dd_APP-001_stripe_backend_resume_content.md
├── output_pdfs/                     # Dedicated folder for output LaTeX & PDFs
│   ├── yyyy_mm_dd_APP-001_stripe_backend_resume.tex
│   └── yyyy_mm_dd_APP-001_stripe_backend_resume.pdf
├── scripts/                         # Helper scripts for automation
│   ├── compile_latex.py
│   └── verify_ats.py
└── templates/                       # Base LaTeX templates
    └── modern_ats_resume.tex
```

---

## Tracking & Status Updates via the Global Sheet

All statuses and checklists are centralized in **`APPLICATIONS_TRACKER.md`**. You can inspect the table, check off items, or simply instruct the agent:
- *"Mark Stripe as applied today and set a follow-up for 3 days from now."*
- *"Show me all applications currently in READY_TO_APPLY status."*
- *"Update Amazon status to SCREENING with interview on Friday."*
