# Job Application Flow — Prompt Playbook

The only runbook. Status values and paths are defined in [ORCHESTRATOR.md](ORCHESTRATOR.md). Do not invent a second schema.

Tell the agent: **"Run Option [N] for [Company] [Role]"**.

---

## Menu

| Option | Step | Output |
| :---: | :--- | :--- |
| **1** | Ingest JD + eligibility halt | `job_descriptions/yyyy_mm_dd_APP-[ID]_[company]_[role]_jd.md` and a `TRIAGE` row |
| **2** | Gap briefing (advisory fit) | Briefing only. No match percentage. |
| **3** | Tailor resume | `resume_contents/yyyy_mm_dd_APP-[ID]_[company]_[role]_resume_content.md` |
| **4** | Compile PDF and verify ATS | `output_pdfs/..._resume.tex` and `.pdf`, then Status `IN_REVIEW` |
| **5** | Cover letter (optional) | `resume_contents/..._cover_letter.md` and matching PDF |
| **6** | Status update | One row in `APPLICATIONS_TRACKER.md` |
| **7** | Single pipeline | Options 1, 2, 3, 4, then wait for approval, then Option 6 |
| **8** | Batch pending JDs | Isolated run of 2–4 per pending JD, then wait for approval |

---

## Shared rules

- Next `APP-ID` is max existing ID in `APPLICATIONS_TRACKER.md` plus one. Never reuse an ID.
- Filename date is today, `yyyy_mm_dd`. Slug is lowercase `[company]_[role]` with spaces as underscores.
- Never hallucinate employers, dates, titles, metrics, authorization, or motivation. Every resume bullet maps to an `[ACH-ID]` in `candidate_profile.md`.
- `scripts/assess_fit.py` is advisory. It does not decide location, work authorization, or seniority, and its score is not a match percentage.
- Do not set `READY_TO_APPLY` until the user explicitly approves that `APP-ID`.
- A missing `pypdf` install is a failed ATS check, not a pass.

---

## Option 1: Ingest & parse

> *"Run Option 1 for [Company] - [Role]: [paste JD]"*

```markdown
### JOB INGESTION

Inputs: company, role, pasted JD text. Do not scrape.

1. Assign the next APP-ID from APPLICATIONS_TRACKER.md.
2. Save a normalized JD to:
   job_descriptions/yyyy_mm_dd_APP-[ID]_[company]_[role]_jd.md
   Include company, role, location, compensation if stated, job URL if the user supplied one, and the raw requirements.
3. Append a tracker row with Status `TRIAGE`, Date Added = today, and a link to the JD.
4. Eligibility (human-facing, then you apply the rule):
   - Location / remote policy vs candidate_profile.md (Heilbronn, Germany; working-student or internship now; full-time from early 2027).
   - Work authorization: do not assume. If the JD requires an authorization the profile does not state, halt and ask.
   - Seniority: do not apply to a role whose level the positioning rule forbids manufacturing.
5. Hard mismatch: set Status `REJECTED_AT_TRIAGE`, write the reason in the checklist, and stop.
6. Otherwise report Go, the saved path, and the key requirements. Leave Status at `TRIAGE` until Option 2 finishes.
```

---

## Option 2: Gap briefing

> *"Run Option 2 for [Company] [Role]"*

```markdown
### GAP BRIEFING

Inputs: candidate_profile.md and the JD file for this APP-ID.

1. Run:
   python scripts/assess_fit.py job_descriptions/yyyy_mm_dd_APP-[ID]_[company]_[role]_jd.md
   If TYPESAFE_API_KEY is missing, say so and continue from the profile. Do not invent a score.
2. Briefing (no match percentage):
   - Direct evidence: skills and [ACH-ID]s that match must-haves.
   - Genuine gaps: must-haves with no evidence. For each: `Gap: [skill] -> Bridge: [evidence from the profile]` or `Gap: [skill] -> Bridge: none`.
   - Positioning: student-first, experienced individual contributor, or no-go. Never recommend changing dates or titles.
3. If the script prints REVIEW, or a must-have has `Bridge: none` that the user is unwilling to omit, do not proceed to Option 3 until the user says to continue or to reject.
4. On continue, set Status `DRAFT`. On reject, set `REJECTED_AT_TRIAGE`.
```

---

## Option 3: Tailor resume

> *"Run Option 3 for [Company] [Role]"*

```markdown
### RESUME TAILORING

Inputs: candidate_profile.md, the JD file, and the Option 2 briefing if it exists.

1. Use only facts in candidate_profile.md.
2. Working-student roles: lead with enrollment and availability. Compress older roles to 1-2 bullets. Do not erase them.
3. Full-time engineering roles: keep the full history. Hands-on delivery, not invented leadership.
4. Completed roles in past tense.
5. One page: summary 2-3 sentences, skills in 4 groups, 2-3 roles, 1-2 projects, compact education.
6. In the markdown file, after the resume body, add a Traceability section. Every bullet line is `derived from [ACH-ID]`. Drop any bullet that cannot be mapped.
7. Write:
   resume_contents/yyyy_mm_dd_APP-[ID]_[company]_[role]_resume_content.md
8. Leave Status at `DRAFT`.
```

---

## Option 4: PDF and ATS check

> *"Run Option 4 for [Company] [Role]"*

```markdown
### PDF AND ATS CHECK

1. Compile (do not hand-write LaTeX):
   python scripts/compile_latex.py --content resume_contents/yyyy_mm_dd_APP-[ID]_[company]_[role]_resume_content.md --template templates/modern_ats_resume.tex --output output_pdfs/yyyy_mm_dd_APP-[ID]_[company]_[role]_resume.pdf
2. Verify:
   python scripts/verify_ats.py output_pdfs/yyyy_mm_dd_APP-[ID]_[company]_[role]_resume.pdf
   Require the literal line VERIFICATION PASSED. Any ERROR, including missing pypdf, is a failure. Do not claim the check passed.
3. Glyph rule for source markdown: do not use `~` or `→`.
4. On pass, set Status `IN_REVIEW` and link JD, content, and PDF.
5. On fail, leave Status `DRAFT` and report the error.
```

---

## Option 5: Cover letter (optional)

> *"Run Option 5 for [Company] [Role]"*

```markdown
### COVER LETTER

1. Three short paragraphs from the profile and the JD only. No invented motivation.
2. First line after the contact block: `**Subject:** Application for [Role]`.
3. Save resume_contents/yyyy_mm_dd_APP-[ID]_[company]_[role]_cover_letter.md
4. Compile:
   python scripts/compile_latex.py --content resume_contents/yyyy_mm_dd_APP-[ID]_[company]_[role]_cover_letter.md --template templates/cover_letter.tex --output output_pdfs/yyyy_mm_dd_APP-[ID]_[company]_[role]_cover_letter.pdf --doctype letter
5. Confirm the PDF exists and is one page. Do not run verify_ats.py on letters.
6. A letter does not change Status and does not replace approval.
```

---

## Option 6: Status update

> *"Run Option 6: APP-[ID] is now [STATUS]"*

```markdown
### STATUS UPDATE

Allowed Status values (ORCHESTRATOR.md only):
TRIAGE, REJECTED_AT_TRIAGE, DRAFT, IN_REVIEW, READY_TO_APPLY, APPLIED, SCREENING, INTERVIEWING, OFFER, ACCEPTED, REJECTED.

1. Edit only the matching APP-ID row and its section-3 checklist. Do not rewrite the file.
2. Recompute section 1 counts from the board. Counts must equal the number of rows.
3. READY_TO_APPLY only after the user explicitly approves that APP-ID.
4. APPLIED: record the submission date and add a follow-up task 7 days out.
5. Report the new status and the next open checklist item.
```

---

## Option 7: Single pipeline

> *"Run Option 7 for [Company] - [Role]: [paste JD]"*

```markdown
### SINGLE PIPELINE

Run in order, and stop at the first halt:

1. Option 1. Stop if REJECTED_AT_TRIAGE.
2. Option 2. Stop if the user has not said to continue past a REVIEW or an unbridged must-have.
3. Option 3.
4. Option 4. Stop if ATS verification fails.
5. Show: PDF link, direct matches, gaps, and a short list of what changed versus the profile.
6. Stop. Status stays IN_REVIEW.
7. Only after the user says "approve APP-[ID]": Option 6 sets READY_TO_APPLY.
```

---

## Option 8: Batch pending JDs

> *"Run Option 8: Batch process all pending JDs"*

```markdown
### BATCH

Pending means a tracker row whose Status is TRIAGE or DRAFT, or a JD file with no matching resume PDF.
Skip REJECTED_AT_TRIAGE, REJECTED, IN_REVIEW, READY_TO_APPLY, and every later status.
Do not reprocess a JD that already has a passing PDF unless the user names that APP-ID.

For each pending JD, in its own context (do not tailor two companies in one pass):

1. Option 2. If REVIEW or an unbridged must-have, leave Status TRIAGE and record the reason. Do not tailor.
2. Option 3, then Option 4.
3. Set Status IN_REVIEW. Do not set READY_TO_APPLY.

Finish with a table: APP-ID, company, role, status, PDF link or the blocking reason.
Approval stays per APP-ID, after the batch.
```
