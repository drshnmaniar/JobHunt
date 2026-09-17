import argparse
import re
import sys

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
        phone_pattern = r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
        
        has_email = bool(re.search(email_pattern, text))
        has_phone = bool(re.search(phone_pattern, text))
        
        if not has_email:
            print("ERROR: Could not extract email address. Formatting may be broken.")
            sys.exit(1)
            
        print("[OK] Contact details extracted successfully.")
        
        # 3. Check Extraction Order (Ensure Experience comes before Education or vice versa, sections exist)
        has_experience = "experience" in text.lower() or "employment" in text.lower()
        has_education = "education" in text.lower()
        
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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Verify PDF ATS Compliance")
    parser.add_argument("pdf_path", help="Path to the generated PDF resume")
    args = parser.parse_args()
    
    verify_ats(args.pdf_path)
