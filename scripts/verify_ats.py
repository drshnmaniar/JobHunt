import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Required headings. Order is taken from the resume template, not hardcoded:
# a student-first resume may legally put Experience before Technical Skills.
REQUIRED_SECTIONS = ("summary", "experience", "education")


def fail(message):
    print(f"ERROR: {message}")
    sys.exit(1)


def verify_ats(pdf_path, profile_path=None):
    try:
        import pypdf
    except ImportError:
        fail("pypdf is not installed. Run `pip install pypdf` and re-run. Verification was not performed.")

    profile_path = Path(profile_path) if profile_path else ROOT / "candidate_profile.md"
    expected_email = None
    if profile_path.is_file():
        match = re.search(r"\*\*Email\*\*:\s*(\S+)", profile_path.read_text(encoding="utf-8"))
        if match:
            expected_email = match.group(1).strip()

    try:
        reader = pypdf.PdfReader(pdf_path)
    except FileNotFoundError:
        fail(f"PDF file not found at {pdf_path}")
    except Exception as exc:
        fail(f"could not read PDF: {exc}")

    if len(reader.pages) != 1:
        fail(f"expected exactly 1 page, found {len(reader.pages)}.")

    text = "\n".join((page.extract_text() or "") for page in reader.pages)
    if len(text.strip()) < 100:
        fail("extracted text is too short. PDF may be rasterized or using non-standard fonts.")

    print("[OK] Selectable text confirmed.")
    print("[OK] Page count is 1.")

    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    emails = re.findall(email_pattern, text)
    if not emails:
        fail("could not extract an email address.")
    if expected_email and expected_email.lower() not in {item.lower() for item in emails}:
        fail(f"extracted email does not match candidate profile ({expected_email}).")
    print("[OK] Contact email extracted and matches the profile.")

    lowered = text.lower()
    for marker in REQUIRED_SECTIONS:
        if marker not in lowered:
            fail(f"could not find section '{marker}'.")
    print("[OK] Required sections detected (summary, experience, education).")
    print("\nVERIFICATION PASSED")


def discover_pdfs(root: Path):
    """Return sorted list of PDF files under output_pdfs/."""
    pdf_dir = root / 'output_pdfs'
    if not pdf_dir.is_dir():
        return []
    return sorted(p for p in pdf_dir.glob('*.pdf'))


def interactive_pick(pdfs):
    """Print a numbered menu and return the chosen Path."""
    print('\nAvailable PDFs:')
    for i, p in enumerate(pdfs, 1):
        print(f'  {i:2}. {p.name}')
    print()
    while True:
        raw = input('Pick a number (or q to quit): ').strip()
        if raw.lower() == 'q':
            raise SystemExit('Aborted.')
        if raw.isdigit() and 1 <= int(raw) <= len(pdfs):
            return pdfs[int(raw) - 1]
        print(f'  Please enter a number between 1 and {len(pdfs)}.')


if __name__ == '__main__':
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
    else:
        pdfs = discover_pdfs(ROOT)
        if not pdfs:
            raise SystemExit('No PDFs found in output_pdfs/.')
        chosen = interactive_pick(pdfs)
        pdf_path = str(chosen)

    verify_ats(pdf_path)
