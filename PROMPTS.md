# Job Application Flow — Prompt Playbook & Step Menu

A modular library of prompts for running each stage of the job application flow independently or in combination. You can copy any prompt or simply tell the Agent: **"Run Option [N] for [Company] [Role]"**.

---

## Menu of Step Options

| Option | Step Name | Primary Input | Output File / Result |
| :---: | :--- | :--- | :--- |
| **Option 1** | **Ingest & Parse Job Description** | Raw JD text or URL | `job_descriptions/yyyy_mm_dd_APP-[ID]_[company]_[role]_jd.md` & row in `APPLICATIONS_TRACKER.md` |
| **Option 2** | **Gap Analysis & Match Strategy** | `candidate_profile.md` + JD | Match scorecard, direct fits, and transferable pivots |
| **Option 3** | **Recursive Resume Tailoring** | `candidate_profile.md` + JD | `resume_contents/yyyy_mm_dd_APP-[ID]_[company]_[role]_resume_content.md` |
| **Option 4** | **LaTeX & PDF Generation** | Tailored Resume Markdown | `output_pdfs/yyyy_mm_dd_APP-[ID]_[company]_[role]_resume.tex` & `.pdf` |
| **Option 5** | **Generate Tailored Cover Letter** | Candidate Profile + JD | `resume_contents/yyyy_mm_dd_APP-[ID]_[company]_[role]_cover_letter.md` |
| **Option 6** | **Status & Checklist Update** | Application Name + Status | Updates `APPLICATIONS_TRACKER.md` board & tasks |
| **Option 7** | **End-to-End Single Pipeline** | Company + Role + Raw JD | Runs Options 1, 3, 4, & 6 in sequence for 1 role |
| **Option 8** | **Batch / Mass Content Generation** | Multiple JDs in `job_descriptions/` | Generates tailored content & PDFs in isolated contexts for all pending JDs |

---

## Option 1: Ingest & Parse Job Description

**Trigger Command for Agent**:
> *"Run Option 1 for [Company Name] - [Position Title]: [Paste JD text or URL]"*

```markdown
### SYSTEM DIRECTIVE: JOB INGESTION & PARSING

**Inputs**:
- Company: [Company Name]
- Position: [Position Title]
- Raw Content: [Pasted JD text or URL]

**Actions**:
1. Clean and structure the job posting into Markdown with the following sections:
   - Header metadata: Company, Role, Location (Remote/Hybrid/Onsite), Compensation range, Job URL, Source.
   - About the Role & Responsibilities.
   - Core / Must-Have Requirements.
2. **Triage Check (Eligibility & Fit)**:
   - Evaluate Location, Work Authorization, and Seniority against candidate profile.
   - If there is a hard disqualifier, mark as `REJECTED_AT_TRIAGE`, summarize the mismatch, and HALT execution.
3. Assign a unique ID (e.g. `APP-001`) and save the formatted file to:
   `job_descriptions/yyyy_mm_dd_APP-[ID]_[company]_[position]_jd.md`
   *(where `yyyy_mm_dd` is the current date, e.g. `2026_09_14`)*
4. Append a new row to `APPLICATIONS_TRACKER.md` in the Master Board table:
   - Set Pipeline Stage to `Triaging` and Activity Status to `Action Required`.
   - Record Date Added and links to `[JD]`.
5. Report back with:
   - Triage decision (Go/No-Go).
   - Key requirements extracted.
   - Confirmation of saved path and tracker update.
```

---

## Option 2: Gap Analysis & Match Strategy

**Trigger Command for Agent**:
> *"Run Option 2 for [Company Name] [Position Title]"*

```markdown
### SYSTEM DIRECTIVE: GAP ANALYSIS & STRATEGY

**Inputs**:
- `candidate_profile.md`
- `job_descriptions/yyyy_mm_dd_APP-[ID]_[company]_[position]_jd.md`

**Actions**:
1. Perform a comparative audit across 3 dimensions:
   - **Direct Hard Skill Matches**: Skills, languages, tools, and scale metrics that match 1-to-1 between candidate and JD.
   - **Skill Gaps & Weaknesses**: Requirements in the JD where the candidate has no direct professional experience.
   - **Transferable Alignment Angles**: For every gap identified, locate adjacent experiences, foundational principles, or personal projects from the candidate profile that prove capability (e.g., Kafka gap answered by RabbitMQ/Redis Streams + Raft consensus).
2. Compute an estimated **Match Score** (0 - 100%) based on must-haves vs. nice-to-haves.
3. Output a concise strategic briefing including:
   - Top 3 career achievements to highlight.
   - Which bullet points to prioritize.
   - For every skill gap identified, you MUST output a 1-sentence bridging strategy using the syntax: `Gap: [Skill] -> Bridge: [Transferable skill from candidate_profile.md]`.
```

---

## Option 3: Recursive Resume Tailoring

**Trigger Command for Agent**:
> *"Run Option 3 for [Company Name] [Position Title]"*

```markdown
### SYSTEM DIRECTIVE: RECURSIVE RESUME TAILORING

**Inputs**:
- `candidate_profile.md`
- `job_descriptions/yyyy_mm_dd_APP-[ID]_[company]_[position]_jd.md`

**Tailoring Guidelines**:
1. **Never Hallucinate**: Only use factual career history, metrics, and technologies documented in `candidate_profile.md`.
2. **Keyword Optimization**: Naturally incorporate top keywords from the JD into the professional summary and achievement bullets.
3. **XYZ Impact Phrasing**: Structure every bullet point using Google's XYZ formula: *Accomplished [X] as measured by [Y] by doing [Z]*.
4. **Strict Single-Page Budget**:
   - Professional Summary: 2-3 sentences focused on role pain points.
   - Technical Skills: 4 organized categories.
   - Work Experience: Top 2-3 most relevant roles with 3-5 high-impact bullets each.
   - Technical Projects: 1-2 projects directly addressing nice-to-haves or gaps.
   - Education & Certifications: Compact 1-2 lines.

**Recursive Pass Protocol (Chain of Thought)**:
- *Pass 1 (Drafting)*: Assemble the raw tailored content in a `<draft>` block matching JD priorities.
- *Pass 2 (Critique)*: Write a `<critique>` block evaluating the draft against the 1-page word count budget (~450-500 words maximum) and eliminating passive verbs.
  **CRITICAL TRACEABILITY**: Within the critique block, explicitly state the mapping for every single work experience bullet back to its source ID. Example: `Resume Bullet 1 derived from [ACH-042]`. Do not output any bullet that cannot be mapped.
- *Pass 3 (Output)*: Write the final, polished result to:
  `resume_contents/yyyy_mm_dd_APP-[ID]_[company]_[position]_resume_content.md`
```

---

## Option 4: LaTeX & PDF Generation

**Trigger Command for Agent**:
> *"Run Option 4 for [Company Name] [Position Title]"*

```markdown
### SYSTEM DIRECTIVE: LATEX TYPESETTING & PDF COMPILATION

**Inputs**:
- `resume_contents/yyyy_mm_dd_APP-[ID]_[company]_[position]_resume_content.md`
- `templates/modern_ats_resume.tex`

**Directives**:
1. Do not manually escape characters or generate raw LaTeX. Instead, run the automated compilation script which handles safe escaping and PDF generation:
   ```powershell
   python scripts/compile_latex.py --content resume_contents/yyyy_mm_dd_APP-[ID]_[company]_[position]_resume_content.md --template templates/modern_ats_resume.tex --output output_pdfs/yyyy_mm_dd_APP-[ID]_[company]_[position]_resume.pdf
   ```
   The script auto-detects resume vs. cover letter from the H1 (`--doctype auto`); pass `--doctype letter` with `templates/cover_letter.tex` for cover letters (see Option 5).
2. **Glyph rules (ATS extraction fidelity)**: never use `~` (extracts as `˜` — write "about"/"approx.") or `→` (pdflatex drops it — write "to"). Bullets, ligatures, and dashes are handled by the template's `glyphtounicode` mapping; do not fight it with manual escapes.
2. Verify the ATS compliance programmatically:
   - Run the ATS text extraction script:
     ```powershell
     python scripts/verify_ats.py output_pdfs/yyyy_mm_dd_APP-[ID]_[company]_[position]_resume.pdf
     ```
   - Confirm the script prints "VERIFICATION PASSED" (checks for selectable text, correct section order, and intact contact info).
3. Clean up the PDF folder (runs automatically inside `compile_latex.py`, Step 7):
   - Deletes pdflatex sidecar files (`.aux`, `.log`, `.out`, `.toc`, `.synctex.gz`, `.fls`, `.fdb_latexmk`) next to the output.
   - Keeps only `.tex` + `.pdf`. To clean manually:
     ```powershell
     Get-ChildItem output_pdfs -Include *.aux,*.log,*.out,*.toc,*.synctex.gz,*.fls,*.fdb_latexmk -Recurse | Remove-Item
     ```
3. Return a direct link to `output_pdfs/yyyy_mm_dd_APP-[ID]_[company]_[position]_resume.pdf`.
```

---

## Option 5: Generate Tailored Cover Letter (Optional)

**Trigger Command for Agent**:
> *"Run Option 5 for [Company Name] [Position Title]"*

```markdown
### SYSTEM DIRECTIVE: TAILORED COVER LETTER

**Inputs**:
- `candidate_profile.md`
- `job_descriptions/yyyy_mm_dd_APP-[ID]_[company]_[position]_jd.md`

**Directives**:
1. Write a compelling, conversational, high-signal 3-paragraph cover letter:
   - **Subject line (mandatory)**: `**Subject:** Application for [Role] (Job ID [ID])` directly after the contact line.
   - **Paragraph 1 (The Hook)**: Why this company and role? Reference a specific engineering challenge or product aspect mentioned in the JD.
   - **Paragraph 2 (The Proof)**: Highlight 1-2 major past technical achievements with real metrics that prove you can solve their exact problems.
   - **Paragraph 3 (The Alignment & Call to Action)**: Emphasize culture, mutual interest, and invite further conversation.
   - Close with `Best regards,` + name on separate lines. Never use `~` or `→` (see Option 4 glyph rules).
2. Save to:
   `resume_contents/yyyy_mm_dd_APP-[ID]_[company]_[position]_cover_letter.md`
3. Compile the letter PDF with the dedicated letter template (block-letter layout, real paragraph breaks):
   ```powershell
   python scripts/compile_latex.py --content resume_contents/yyyy_mm_dd_APP-[ID]_[company]_[position]_cover_letter.md --template templates/cover_letter.tex --output output_pdfs/yyyy_mm_dd_APP-[ID]_[company]_[position]_cover_letter.pdf --doctype letter
   ```
   Then run the folder cleanup substep (Option 4, step 3). Note: `verify_ats.py` does not apply to letters (no Experience section) — confirm 1 page and selectable text via extraction instead.
```

---

## Option 6: Status & Checklist Update

**Trigger Command for Agent**:
> *"Run Option 6: [Company Name] is now [APPLIED / SCREENING / INTERVIEWING / OFFER / REJECTED]"*

```markdown
### SYSTEM DIRECTIVE: STATUS & TRACKER UPDATE

**Inputs**:
- Company: [Company Name]
- APP-ID: [APP-ID]
- New Pipeline Stage: [Triaging | Applying | Screening | Interviewing | Offer | Accepted | Rejected]
- New Activity Status: [Action Required | Waiting on Employer | Blocked | Complete]
- Optional Notes / Dates: [e.g. Applied via portal, Interview on Friday, etc.]

**Actions**:
1. In `APPLICATIONS_TRACKER.md`:
   - Use targeted file edit tools (like `replace_file_content` or `sed`) to update ONLY the specific row for this `APP-ID` in the **Master Applications Board** table, rather than rewriting the entire file. Update both the Stage and Activity Status columns.
   - Update the **Pipeline Summary** count for each stage using targeted edits.
   - In Section 3 (**Active Checklists**), use targeted edits to mark completed tasks `- [x]` and update next action target dates.
   - If Stage is `Applying` and Status becomes `Waiting on Employer` (meaning applied), record submission timestamp and add LinkedIn outreach task (due in 2 days) and follow-up reminder (due in 7 days).
   - If Stage is `Screening` or `Interviewing`, add interview preparation items (company research, system design talking points, questions for interviewer).
2. Report the updated status and next pending action to the user.
```

---

## Option 7: End-to-End Single Pipeline (All-in-One)

**Trigger Command for Agent**:
> *"Run Option 7 for [Company Name] - [Position Title]: [Paste JD text or URL]"*

```markdown
### SYSTEM DIRECTIVE: END-TO-END AUTONOMOUS PIPELINE

Executes the following options sequentially:
1. **Option 1**: Ingest JD & Triage -> `job_descriptions/yyyy_mm_dd_APP-[ID]_[company]_[position]_jd.md`.
2. **Option 3**: Tailor Resume -> `resume_contents/yyyy_mm_dd_APP-[ID]_[company]_[position]_resume_content.md`.
3. **Option 4**: Typeset, Compile LaTeX, and Verify ATS -> `output_pdfs/yyyy_mm_dd_APP-[ID]_[company]_[position]_resume.pdf`.
4. **Option 6**: Sync Global Tracker -> Sets Stage to `Applying`, Status to `Action Required` in `APPLICATIONS_TRACKER.md`.
5. Present final summary with links to all generated assets and next immediate action.
```

---

## Option 8: Batch / Mass Content Generation (Multiple JDs)

**Trigger Command for Agent**:
> *"Run Option 8: Batch process all pending JDs"*  
> *(or: "Run Option 8 for: 2026_09_14_APP-002_google_sre_jd.md, 2026_09_14_APP-003_siemens_working_student_jd.md")*

```markdown
### SYSTEM DIRECTIVE: MASS BATCH GENERATION (ISOLATED CONTEXTS)

**Goal**: Process multiple JDs in bulk, tailoring custom resumes and compiling PDFs for each, while enforcing strict context isolation to prevent keyword bleed between companies.

**Inputs**:
- `candidate_profile.md` (shared single source of truth)
- Target JDs: All files in `job_descriptions/*.md` where `output_pdfs/*.pdf` does not yet exist, OR explicitly listed JD files.

---

### BATCH EXECUTION ALGORITHM:

1. **Discovery & Queueing**:
   - Scan `job_descriptions/`.
   - Identify all JDs where Stage in `APPLICATIONS_TRACKER.md` is `Triaging` or where PDF does not exist.
   - List the queue of target roles: `[Job 1, Job 2, ... Job N]`.

2. **Isolated Sub-Agent Execution** (For each JD in queue):
   
   > [!IMPORTANT]
   > **Context Isolation Rule**: Do not process multiple JDs in the same conversational thread. For each JD in the queue, spawn a **new independent sub-agent** or execute a fresh, isolated API call passing ONLY:
   > `candidate_profile.md` + `job_descriptions/yyyy_mm_dd_APP-[ID]_[current_jd].md`.

   - **Step 2A (Tailor Content - via Sub-Agent)**:
     - Sub-agent maps achievements to `[ACH-ID]` for this specific JD.
     - Save to: `resume_contents/yyyy_mm_dd_APP-[ID]_[company]_[role]_resume_content.md`.
   
   - **Step 2B (Typeset, Compile & Verify)**:
     - Run `python scripts/compile_latex.py` and `scripts/verify_ats.py`.
     - Verify: Ensure exit code 0, 1-page geometry, and machine readability.

   - **Step 2C (Tracker Sync)**:
     - Update `APPLICATIONS_TRACKER.md` with:
       * Stage: `Applying` | Status: `Action Required`
       * Clickable links to `[JD]`, `[Content]`, and `[PDF]`.
       * Default submission checklist items and follow-up target dates.

3. **Batch Completion Report**:
   - Output a summary table of all processed jobs:
     | Company | Role | Tailored Focus | PDF Status | Tracker Link |
   - Alert the user if any job had compilation issues or exceeded 1 page.
```

