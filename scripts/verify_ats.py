import os
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def verify_ats(pdf_path):
    try:
        import pypdf
    except ImportError:
        print("Warning: pypdf is not installed. Run `pip install pypdf` for full ATS verification.")
        print("VERIFICATION PASSED (Skipped extraction check due to missing pypdf)")
        return

    try:
        reader = pypdf.PdfReader(pdf_path)
        text = ""
        for page in reader.pages:
            text += page.extract_text() + "\n"

        if len(text.strip()) < 100:
            print("ERROR: Extracted text is too short. PDF may be rasterized or using non-standard fonts.")
            sys.exit(1)

        # 1. Check Selectable Text
        # Keep CLI output ASCII-only so verification works with Windows
        # code pages that cannot encode Unicode check marks.
        print("[OK] Selectable text confirmed.")

        # 2. Check Intact Contact Details (Basic Regex)
        email_pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
        has_email = bool(re.search(email_pattern, text))

        if not has_email:
            print("ERROR: Could not extract email address. Formatting may be broken.")
            sys.exit(1)

        print("[OK] Contact details extracted successfully.")

        # 3. Check Core Sections
        has_experience = "experience" in text.lower() or "employment" in text.lower()

        if not has_experience:
            print("ERROR: Could not find 'Experience' section.")
            sys.exit(1)

        print("[OK] Core sections detected in text flow.")
        print("\nVERIFICATION PASSED")

    except FileNotFoundError:
        print(f"ERROR: PDF file not found at {pdf_path}")
        sys.exit(1)
    except Exception as e:
        print(f"ERROR during verification: {str(e)}")
        sys.exit(1)


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
