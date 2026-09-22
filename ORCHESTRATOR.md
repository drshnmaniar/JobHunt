# Master Orchestrator Guide

How to run the job application flow. The only runbook is [PROMPTS.md](PROMPTS.md). This file is the short version of that runbook.

Do not invent a second status model, directory layout, or checklist. The live tracker is [APPLICATIONS_TRACKER.md](APPLICATIONS_TRACKER.md).

---

## Quick start

- One job: `Run Option 7 for [Company] - [Role]: [paste JD]`
- One step: `Run Option [N] for [Company] [Role]`
- Batch: `Run Option 8: Batch process all pending JDs`

Option 7 stops for approval before anything is marked `READY_TO_APPLY`.

---

## Status (one column)

Use only these values in the tracker Status column:

| Status | Meaning |
| :--- | :--- |
| `TRIAGE` | JD saved. Eligibility not yet decided. |
| `REJECTED_AT_TRIAGE` | Hard mismatch (location, authorization, seniority, or unwilling constraints). Pipeline stops. |
| `DRAFT` | Tailoring in progress. Not ready to send. |
| `IN_REVIEW` | PDF exists. Waiting for explicit human approval. |
| `READY_TO_APPLY` | Human approved the packet. Not yet submitted. |
| `APPLIED` | Submitted. Record the date. |
| `SCREENING` | Recruiter screen or active outreach. |
| `INTERVIEWING` | Interview scheduled or in progress. |
| `OFFER` | Offer received. |
| `ACCEPTED` | Offer accepted. |
| `REJECTED` | Closed after apply, or declined by candidate. |

Pipeline Summary counts must use these same names. Do not add a second Stage / Activity pair.

---

## Pipeline

```
User: company, role, pasted JD
        |
        v
1. Ingest (Option 1)
   - Next APP-ID from the tracker (do not reuse or guess)
   - Save job_descriptions/yyyy_mm_dd_APP-[ID]_[company]_[role]_jd.md
   - Tracker row, Status: TRIAGE
        |
        v
2. Eligibility (human) + fit note (Option 2)
   - Human checks location, work authorization, seniority, constraints
   - python scripts/assess_fit.py <jd> is advisory only
   - Hard mismatch -> REJECTED_AT_TRIAGE and stop
   - Otherwise Status: DRAFT
        |
        v
3. Tailor (Option 3)
   - Map every bullet to an [ACH-ID] in candidate_profile.md
   - Write resume_contents/yyyy_mm_dd_APP-[ID]_[company]_[role]_resume_content.md
        |
        v
4. PDF + ATS check (Option 4)
   - python scripts/compile_latex.py ...
   - python scripts/verify_ats.py <pdf>   must print VERIFICATION PASSED
   - Status: IN_REVIEW
        |
        v
5. Human approval (required)
   - Show proposed resume, direct matches, gaps, and what changed
   - Only after an explicit "approve" set Status: READY_TO_APPLY
```

Cover letters (Option 5) are optional and never replace the approval step.

---

## Career-level positioning

Never alter, omit, or shorten factual employment dates or verifiable job titles to manufacture a seniority level.

### Working-student and student roles

- Lead with current enrollment, degree timeline, and working-student availability.
- Compress older roles (1-2 bullets). Do not erase them.
- Do not invent motivation, relocation, work authorization, or a long-term commitment.

### Full-time software-engineering roles

- Keep the full career history.
- Target scope that matches the work performed. Do not claim entry-level to broaden eligibility.
- Describe completed roles in the past tense.

---

## Workspace

```
JobHuntSeptemberFlow/
├── candidate_profile.md
├── APPLICATIONS_TRACKER.md
├── ORCHESTRATOR.md
├── PROMPTS.md
├── IDEA.md
├── job_descriptions/
├── resume_contents/
├── output_pdfs/
├── scripts/
│   ├── assess_fit.py
│   ├── compile_latex.py
│   └── verify_ats.py
└── templates/
    ├── modern_ats_resume.tex
    └── cover_letter.tex
```

There is no `applications/` tree and no per-job checklist file. Checklists live in section 3 of the tracker.

---

## Tracker commands

- "Approve APP-006" sets `READY_TO_APPLY`.
- "Mark Stripe as applied today" sets `APPLIED` and records the date.
- "Show applications in IN_REVIEW."
