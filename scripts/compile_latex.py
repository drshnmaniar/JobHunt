import argparse
import os
import re
import subprocess
import sys

def escape_latex(text):
    """Escapes LaTeX special characters in plain text."""
    # Must do backslash first
    text = text.replace('\\', '\\textbackslash{}')
    # Then others
    replacements = {
        '&': '\\&',
        '%': '\\%',
        '$': '\\$',
        '#': '\\#',
        '_': '\\_',
        '{': '\\{',
        '}': '\\}',
        '~': '\\textasciitilde{}',
        '^': '\\textasciicircum{}',
    }
    for char, rep in replacements.items():
        text = text.replace(char, rep)
    return text

def process_inline_markdown(text):
    """Handles **bold**, *italic*, and links after escaping."""
    # First escape the text
    text = escape_latex(text)
    
    # Replace **bold** with \textbf{bold}
    text = re.sub(r'\*\*(.*?)\*\*', r'\\textbf{\1}', text)
    # Replace *italic* with \textit{italic}
    text = re.sub(r'\*(.*?)\*', r'\\textit{\1}', text)
    
    # Handle [link](url)
    text = re.sub(r'\[(.*?)\]\((.*?)\)', r'\\href{\2}{\1}', text)
    
    return text

def is_bold_only_line(stripped):
    """True if the whole line is a single **bold** span (e.g. a name line)."""
    return bool(re.fullmatch(r'\*\*.+\*\*', stripped))

def convert_md_to_latex(md_content, doctype='auto'):
    """Dispatches to the resume or letter converter (auto-detects on the H1)."""
    if doctype == 'auto':
        m = re.search(r'^#\s+(.+)$', md_content, re.MULTILINE)
        doctype = 'letter' if (m and 'cover letter' in m.group(1).lower()) else 'resume'
    if doctype == 'letter':
        return convert_md_letter(md_content)
    return convert_md_resume(md_content)

def convert_md_letter(md_content):
    """Converts a cover-letter markdown file to block-letter LaTeX.

    Expected structure (see PROMPTS.md Option 5):
      # Cover Letter: ... (skipped, not rendered)
      **Name**            -> centered header
      contact line        -> centered contact + date below
      **Subject:** ...    -> bold subject paragraph
      Dear ...,           -> greeting
      body paragraphs     -> separated by real \\par breaks
      Best regards, Name  -> spaced closing block
    """
    lines = md_content.split('\n')
    latex_lines = []
    h1_skipped = False
    header_state = 'want_name'  # want_name -> want_contact -> body

    for line in lines:
        stripped = line.strip()

        # Skip the file-title H1 ("# Cover Letter: ...") — not part of the letter
        if stripped.startswith('# ') and not h1_skipped:
            h1_skipped = True
            continue
        if not h1_skipped:
            continue

        # Blank markdown lines become real paragraph breaks (no more wall of text)
        if not stripped:
            latex_lines.append('')
            continue

        # Name: first bold-only line -> centered large header
        # (bfseries, not scshape: Times has no true small-caps and the
        # fallback corrupts text extraction: "DARSHAN M ANIAR")
        if header_state == 'want_name' and is_bold_only_line(stripped):
            name = process_inline_markdown(stripped.strip('*').strip())
            latex_lines.append('\\begin{center}')
            latex_lines.append(f"{{\\Large \\bfseries {name}}} \\\\ \\vspace{{2pt}}")
            header_state = 'want_contact'
            continue

        # Contact: line right after the name -> centered contact + date
        if header_state == 'want_contact':
            latex_lines.append(f"{{\\small {process_inline_markdown(stripped)}}}")
            latex_lines.append('\\end{center}')
            latex_lines.append('\\begin{flushright}')
            latex_lines.append('{\\small \\today}')
            latex_lines.append('\\end{flushright}')
            latex_lines.append('')
            header_state = 'body'
            continue

        # Closing gets vertical breathing room before it, and the signature
        # name drops to its own line
        if stripped == 'Best regards,':
            latex_lines.append('')
            latex_lines.append('\\vspace{6pt}')
            latex_lines.append('{\\small Best regards,\\\\}')
            continue

        # Everything else (subject, greeting, body, signature name): own paragraph
        latex_lines.append(f"{{\\small {process_inline_markdown(stripped)}}}")
        latex_lines.append('')

    return '\n'.join(latex_lines)

def convert_md_resume(md_content):
    """Converts a tailored resume markdown to compact 1-page ATS LaTeX."""
    # Strip internal traceability tags like [ACH-01] — never show in PDF
    md_content = re.sub(r'\s*\[ACH-[0-9A-Za-z-]+\]', '', md_content)
    lines = md_content.split('\n')
    latex_lines = []
    in_list = False
    first_h1_skipped = False
    seen_section = False
    in_contact_header = False
    contact_name_done = False
    last_was_para = False

    def close_list():
        nonlocal in_list, last_was_para
        if in_list:
            latex_lines.append('\\end{itemize}')
            in_list = False
        last_was_para = False

    def open_list():
        nonlocal in_list
        if not in_list:
            latex_lines.append('\\begin{itemize}[leftmargin=0.15in,topsep=2pt,itemsep=2pt,parsep=0pt]')
            in_list = True

    for line in lines:
        stripped = line.strip()

        # Skip horizontal rules
        if stripped in ('---', '***', '___'):
            close_list()
            in_contact_header = False
            continue
        # Skip the file-title H1 ("# Resume Content: ...") — not part of resume
        if stripped.startswith('# ') and not first_h1_skipped:
            first_h1_skipped = True
            last_was_para = False
            continue

        # Empty markdown lines become real paragraph breaks (prevents wall-of-text merging)
        if not stripped:
            close_list()
            latex_lines.append('')
            continue

        # ## Section headings -> ATS \section
        if stripped.startswith('## '):
            close_list()
            title = stripped[3:].strip()
            seen_section = True
            if title.lower() == 'contact header':
                in_contact_header = True
                contact_name_done = False
                continue
            in_contact_header = False
            latex_lines.append(f"\\section{{{process_inline_markdown(title)}}}")
            continue

        # Fallback: bold-only name line before any section (no ## Contact Header present)
        # -> centered header; the following line becomes the centered contact line
        if not seen_section and not in_contact_header and is_bold_only_line(stripped):
            close_list()
            name = process_inline_markdown(stripped.strip('*').strip())
            latex_lines.append('\\begin{center}')
            latex_lines.append(f"{{\\Large \\bfseries {name}}} \\\\ \\vspace{{2pt}}")
            in_contact_header = True
            contact_name_done = True
            continue

        # Contact header body: centered name + contact line
        if in_contact_header:
            close_list()
            if not contact_name_done and is_bold_only_line(stripped):
                name = process_inline_markdown(stripped.strip('*').strip())
                latex_lines.append('\\begin{center}')
                latex_lines.append(f"{{\\Large \\bfseries {name}}} \\\\ \\vspace{{2pt}}")
                contact_name_done = True
                continue
            if contact_name_done:
                latex_lines.append(f"{{\\small {process_inline_markdown(stripped)}}}")
                latex_lines.append('\\end{center}')
                in_contact_header = False
                continue
            latex_lines.append(f"{{\\small {process_inline_markdown(stripped)}}}")
            continue

        # ### Role / project headings -> compact bold line (saves vertical space)
        if stripped.startswith('### '):
            close_list()
            latex_lines.append(f"\\noindent\\textbf{{{process_inline_markdown(stripped[4:].strip())}}}\\\\")
            continue

        # Italic date lines like *Dec 2022 – Mar 2025 | ...* -> small italic
        if stripped.startswith('*') and stripped.endswith('*') and len(stripped) > 2:
            close_list()
            latex_lines.append(f"{{\\small\\textit{{{process_inline_markdown(stripped.strip('*').strip())}}}}}\\\\[-2pt]")
            continue

        # Headers (fallback)
        if stripped.startswith('# '):
            close_list()
            latex_lines.append(f"\\section{{{process_inline_markdown(stripped[2:].strip())}}}")
            continue

        # Lists -> compact small bullets
        if stripped.startswith('- ') or stripped.startswith('* '):
            open_list()
            last_was_para = False
            latex_lines.append(f"\\item\\small{{{process_inline_markdown(stripped[2:].strip())}}}")
            continue

        # Regular paragraph -> small text. Consecutive stacked lines (e.g. the
        # two Education entries) get an explicit line break instead of merging
        # into one run-together paragraph.
        if in_list:
            latex_lines[-1] = latex_lines[-1] + ' ' + process_inline_markdown(stripped)
        else:
            if last_was_para and latex_lines and not latex_lines[-1].endswith('\\\\'):
                latex_lines[-1] = latex_lines[-1] + '\\\\'
            latex_lines.append(f"{{\\small {process_inline_markdown(stripped)}}}")
            last_was_para = True

    close_list()
    return '\n'.join(latex_lines)

def main():
    parser = argparse.ArgumentParser(description="Compile Markdown to LaTeX PDF")
    parser.add_argument('--content', required=True, help="Path to markdown content file")
    parser.add_argument('--template', required=True, help="Path to LaTeX template")
    parser.add_argument('--output', required=True, help="Path to output PDF")
    parser.add_argument('--doctype', default='auto', choices=('auto', 'resume', 'letter'),
                        help="Document type: auto-detects letter vs resume from the H1")
    args = parser.parse_args()
    
    # 1. Read Markdown
    try:
        with open(args.content, 'r', encoding='utf-8') as f:
            md_content = f.read()
    except FileNotFoundError:
        print(f"Error: Content file not found at {args.content}")
        sys.exit(1)
        
    # 2. Convert to LaTeX snippet
    latex_body = convert_md_to_latex(md_content, doctype=args.doctype)
    
    # 3. Read Template
    try:
        with open(args.template, 'r', encoding='utf-8') as f:
            template_content = f.read()
    except FileNotFoundError:
        print(f"Error: Template file not found at {args.template}")
        sys.exit(1)
        
    # 4. Inject Body
    # Try different common placeholders
    if '{{CONTENT}}' in template_content:
        final_tex = template_content.replace('{{CONTENT}}', latex_body)
    elif '% CONTENT_GOES_HERE' in template_content:
        final_tex = template_content.replace('% CONTENT_GOES_HERE', latex_body)
    else:
        # Fallback: Just insert before \end{document}
        final_tex = template_content.replace('\\end{document}', latex_body + '\n\\end{document}')
        
    # 5. Write to .tex file
    output_dir = os.path.dirname(args.output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
        
    tex_file = args.output.replace('.pdf', '.tex')
    with open(tex_file, 'w', encoding='utf-8') as f:
        f.write(final_tex)
        
    # 6. Compile PDF
    print(f"Compiling {tex_file} to PDF...")
    try:
        result = subprocess.run(
            ['pdflatex', '-halt-on-error', '-disable-installer', f'-output-directory={output_dir}', tex_file],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print("Compilation successful.")
    except subprocess.CalledProcessError as e:
        print("Error during pdflatex compilation:")
        print(e.stdout)
        print(e.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print("Error: pdflatex command not found. Ensure MiKTeX or TeX Live is installed and in PATH.")
        sys.exit(1)

    # 7. Clean up LaTeX sidecar files (keep only .tex + .pdf)
    cleanup_extensions = ('.aux', '.log', '.out', '.toc', '.synctex.gz', '.fls', '.fdb_latexmk')
    tex_basename = os.path.splitext(tex_file)[0]
    for ext in cleanup_extensions:
        sidecar = tex_basename + ext
        try:
            if os.path.isfile(sidecar):
                os.remove(sidecar)
                print(f"Removed {sidecar}")
        except OSError as e:
            print(f"Warning: could not remove {sidecar}: {e}")

if __name__ == "__main__":
    main()
