# Job Application Sprint

## Problem Statement

How might we help one technical job seeker turn a trustworthy candidate profile and a pasted job description into a high-quality, approved application in under 15 minutes, using only local files and agent commands?

## Recommended Direction

Build an evidence-grounded tailoring workflow rather than a broad job-search platform. The user supplies a company, role, and pasted job description. The system saves a normalized JD snapshot, compares it with `candidate_profile.md`, proposes a concise tailored resume, identifies direct matches and honest gaps, and explains the factual changes it made.

The workflow must include an explicit human approval step before an application is considered ready or submitted. Its value is speed and reliability: the user should be able to move from JD capture to an approved application packet quickly, without keyword stuffing or invented experience.

## Key Assumptions to Validate

- [ ] A pasted JD is sufficient for the first version; validate that scraping is not needed for normal use.
- [ ] A trusted Markdown profile provides enough evidence to produce useful tailoring; measure factual corrections across the first 10 applications.
- [ ] Human approval can remain fast if the system presents only the proposed resume, direct matches, gaps, and change summary.
- [ ] A local-file workflow can reduce median JD-to-approved-submission time below 15 minutes.

## MVP Scope

- Accept company, role, and pasted JD text.
- Save a normalized JD snapshot locally.
- Compare JD requirements with `candidate_profile.md`.
- Produce direct matches, genuine gaps, transferable evidence, and a tailored one-page resume.
- Produce a short factual change summary for review.
- Require explicit approval before marking the packet ready to submit.
- Generate and validate one searchable PDF.
- Add or update one tracker record with links to the JD, resume content, PDF, submission state, and one follow-up date.
- Use one canonical status model and one consistent directory layout.

## Not Doing (and Why)

- JD scraping — dynamic pages, access restrictions, and expired postings add fragility; pasted text is enough to validate the core workflow.
- Match percentages as a decision — `scripts/assess_fit.py` may print an advisory score, but the runbook must not treat it as a go/no-go percentage or a reason to keyword-stuff.
- Unapproved batch submission — Option 8 may tailor pending JDs, but every packet stays `IN_REVIEW` until that APP-ID is explicitly approved.
- Kanban UI and analytics — local Markdown tracking is sufficient for the first user.
- Autonomous submission or status transitions — consequential actions require human confirmation.
- Multiple PDF renderers — choose and validate one renderer before adding alternatives.
- Automatic cover letters — optional and secondary to producing a strong resume quickly.
- Reminder infrastructure — record follow-up dates first; automate reminders only after the workflow proves useful.

## Open Questions

- PDF path is `scripts/compile_latex.py` plus `pdflatex`. Do not add a second renderer unless this one fails a real packet.
- Canonical statuses live in `ORCHESTRATOR.md`: `TRIAGE`, `REJECTED_AT_TRIAGE`, `DRAFT`, `IN_REVIEW`, `READY_TO_APPLY`, `APPLIED`, `SCREENING`, `INTERVIEWING`, `OFFER`, `ACCEPTED`, `REJECTED`.
- What review format lets the user approve a tailored application in under two minutes?
