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
      ## Contact Header   (skipped, not rendered)
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
    in_closing = False

    for line in lines:
        stripped = line.strip()

        # Skip the file-title H1 ("# Cover Letter: ...") — not part of the letter
        if stripped.startswith('# ') and not h1_skipped:
            h1_skipped = True
            continue
        if not h1_skipped:
            continue

        # Skip any ## section headings (e.g. "## Contact Header") — metadata only
        if stripped.startswith('## '):
            continue

        # Blank markdown lines become real paragraph breaks (no more wall of text)
        if not stripped:
            if not in_closing:
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

        # Closing gets vertical breathing room before it; name follows immediately
        if stripped == 'Best regards,':
            latex_lines.append('')
            latex_lines.append('\\vspace{6pt}')
            latex_lines.append('{\\small Best regards,}\\\\')
            in_closing = True
            continue

        # Signature name: attach directly to "Best regards," with no gap
        if in_closing:
            name = process_inline_markdown(stripped)
            latex_lines.append(f"{{\\small {name}}}")
            in_closing = False
            continue

        # Everything else (subject, greeting, body): own paragraph
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
    blocks_in_section = 0  # counts ### headings per section

    def close_list():
        nonlocal in_list, last_was_para
        if in_list:
            latex_lines.append('\\end{itemize}')
            in_list = False
        last_was_para = False

    def open_list():
        nonlocal in_list
        if not in_list:
            while latex_lines and latex_lines[-1] == '':
                latex_lines.pop()
            if latex_lines and latex_lines[-1].endswith('\\\\'):
                latex_lines[-1] = latex_lines[-1][:-2]
            latex_lines.append('\\begin{itemize}[leftmargin=0.15in,topsep=0pt,itemsep=4pt,parsep=0pt]')
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
            blocks_in_section = 0  # reset block counter for each new section
            if title.lower() == 'contact header':
                in_contact_header = True
                contact_name_done = False
                continue
            in_contact_header = False
            # Keep section heading + at least 5 lines of content together
            latex_lines.append('\\needspace{5\\baselineskip}')
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

        # ### Role / project headings -> compact bold line with inter-block spacing
        if stripped.startswith('### '):
            close_list()
            # Strip trailing blank lines so vspace sits flush
            while latex_lines and latex_lines[-1] == '':
                latex_lines.pop()
            if blocks_in_section > 0:
                latex_lines.append('\\vspace{8pt}')
            # Keep block heading + at least 4 lines of content together
            latex_lines.append('\\needspace{4\\baselineskip}')
            blocks_in_section += 1
            latex_lines.append(f"\\noindent\\textbf{{{process_inline_markdown(stripped[4:].strip())}}}\\\\")
            continue

        # Italic date lines like *Dec 2022 – Mar 2025 | ...* -> small italic
        if stripped.startswith('*') and stripped.endswith('*') and len(stripped) > 2:
            close_list()
            latex_lines.append(f"{{\\small\\textit{{{process_inline_markdown(stripped.strip('*').strip())}}}}}\\\\")
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

def discover_content_files(root: str):
    """Return sorted list of .md files under resume_contents/."""
    content_dir = os.path.join(root, 'resume_contents')
    if not os.path.isdir(content_dir):
        return []
    files = sorted(
        f for f in os.listdir(content_dir)
        if f.endswith('.md') and not f.startswith('.')
    )
    return [os.path.join(content_dir, f) for f in files]


def auto_resolve(content_path: str, root: str):
    """Derive template, output path and doctype from the content filename."""
    basename = os.path.basename(content_path)
    name_no_ext = os.path.splitext(basename)[0]

    is_letter = 'cover_letter' in name_no_ext
    doctype   = 'letter' if is_letter else 'resume'

    template_name = 'cover_letter.tex' if is_letter else 'modern_ats_resume.tex'
    template      = os.path.join(root, 'templates', template_name)

    # Output PDF keeps the same stem as the content file
    output = os.path.join(root, 'output_pdfs', name_no_ext + '.pdf')
    return template, output, doctype


def interactive_pick(files):
    """Print a numbered menu and return the chosen file path."""
    print('\nAvailable content files:')
    for i, f in enumerate(files, 1):
        print(f'  {i:2}. {os.path.basename(f)}')
    print()
    while True:
        raw = input('Pick a number (or q to quit): ').strip()
        if raw.lower() == 'q':
            raise SystemExit('Aborted.')
        if raw.isdigit() and 1 <= int(raw) <= len(files):
            return files[int(raw) - 1]
        print(f'  Please enter a number between 1 and {len(files)}.')


def compile_file(content, template, output, doctype):
    """Core compile logic shared between CLI and interactive modes."""
    # 1. Read Markdown
    try:
        with open(content, 'r', encoding='utf-8') as f:
            md_content = f.read()
    except FileNotFoundError:
        print(f'Error: Content file not found at {content}')
        sys.exit(1)

    # 2. Convert to LaTeX snippet
    latex_body = convert_md_to_latex(md_content, doctype=doctype)

    # 3. Read Template
    try:
        with open(template, 'r', encoding='utf-8') as f:
            template_content = f.read()
    except FileNotFoundError:
        print(f'Error: Template file not found at {template}')
        sys.exit(1)

    # 4. Inject Body
    if '{{CONTENT}}' in template_content:
        final_tex = template_content.replace('{{CONTENT}}', latex_body)
    elif '% CONTENT_GOES_HERE' in template_content:
        final_tex = template_content.replace('% CONTENT_GOES_HERE', latex_body)
    else:
        final_tex = template_content.replace('\\end{document}', latex_body + '\n\\end{document}')

    # 5. Write to .tex file
    output_dir = os.path.dirname(output)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    tex_file = output.replace('.pdf', '.tex')
    with open(tex_file, 'w', encoding='utf-8') as f:
        f.write(final_tex)

    # 6. Compile PDF
    print(f'Compiling {tex_file} ...')
    try:
        subprocess.run(
            ['pdflatex', '-halt-on-error', '-disable-installer',
             f'-output-directory={output_dir}', tex_file],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        print(f'Done  ->  {output}')
    except subprocess.CalledProcessError as e:
        print('Error during pdflatex compilation:')
        print(e.stdout)
        print(e.stderr)
        sys.exit(1)
    except FileNotFoundError:
        print('Error: pdflatex not found. Ensure MiKTeX or TeX Live is installed and in PATH.')
        sys.exit(1)

    # 7. Clean up sidecar files
    cleanup_extensions = ('.aux', '.log', '.out', '.toc', '.synctex.gz', '.fls', '.fdb_latexmk')
    tex_basename = os.path.splitext(tex_file)[0]
    for ext in cleanup_extensions:
        sidecar = tex_basename + ext
        try:
            if os.path.isfile(sidecar):
                os.remove(sidecar)
        except OSError as e:
            print(f'Warning: could not remove {sidecar}: {e}')


def main():
    ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    parser = argparse.ArgumentParser(
        description='Compile Markdown resume/cover-letter to PDF.\n'
                    'Run with no arguments for interactive file picker.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument('--content',  help='Path to markdown content file')
    parser.add_argument('--template', help='Path to LaTeX template (auto-detected if omitted)')
    parser.add_argument('--output',   help='Path to output PDF (auto-detected if omitted)')
    parser.add_argument('--doctype',  default='auto', choices=('auto', 'resume', 'letter'),
                        help='Document type (default: auto-detect from filename/H1)')
    parser.add_argument('--all', action='store_true',
                        help='Compile every file in resume_contents/ non-interactively')
    args = parser.parse_args()

    # --- compile everything ---
    if args.all:
        files = discover_content_files(ROOT)
        if not files:
            raise SystemExit('No .md files found in resume_contents/.')
        for f in files:
            tmpl, out, dt = auto_resolve(f, ROOT)
            print(f'\n=== {os.path.basename(f)} ===')
            compile_file(f, tmpl, out, dt)
        return

    # --- explicit CLI args provided ---
    if args.content:
        template = args.template
        output   = args.output
        doctype  = args.doctype
        if not template or not output:
            tmpl_auto, out_auto, dt_auto = auto_resolve(args.content, ROOT)
            template = template or tmpl_auto
            output   = output   or out_auto
            if doctype == 'auto':
                doctype = dt_auto
        compile_file(args.content, template, output, doctype)
        return

    # --- interactive picker ---
    files = discover_content_files(ROOT)
    if not files:
        raise SystemExit('No .md files found in resume_contents/.')
    chosen = interactive_pick(files)
    template, output, doctype = auto_resolve(chosen, ROOT)
    if args.doctype != 'auto':
        doctype = args.doctype
    print(f'  Content : {chosen}')
    print(f'  Template: {template}')
    print(f'  Output  : {output}')
    print(f'  Doctype : {doctype}')
    compile_file(chosen, template, output, doctype)


if __name__ == '__main__':
    main()
