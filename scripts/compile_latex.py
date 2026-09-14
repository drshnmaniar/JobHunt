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

def convert_md_to_latex(md_content):
    """Converts a basic Markdown resume to LaTeX."""
    lines = md_content.split('\n')
    latex_lines = []
    in_list = False
    
    for line in lines:
        stripped = line.strip()
        
        # Empty lines
        if not stripped:
            if in_list:
                latex_lines.append('\\end{itemize}')
                in_list = False
            latex_lines.append('')
            continue
            
        # Headers
        if stripped.startswith('# '):
            if in_list: latex_lines.append('\\end{itemize}'); in_list = False
            latex_lines.append(f"\\section{{{process_inline_markdown(stripped[2:].strip())}}}")
            continue
        elif stripped.startswith('## '):
            if in_list: latex_lines.append('\\end{itemize}'); in_list = False
            latex_lines.append(f"\\subsection{{{process_inline_markdown(stripped[3:].strip())}}}")
            continue
        elif stripped.startswith('### '):
            if in_list: latex_lines.append('\\end{itemize}'); in_list = False
            latex_lines.append(f"\\subsubsection{{{process_inline_markdown(stripped[4:].strip())}}}")
            continue
            
        # Lists
        if stripped.startswith('- ') or stripped.startswith('* '):
            if not in_list:
                latex_lines.append('\\begin{itemize}')
                in_list = True
            latex_lines.append(f"\\item {process_inline_markdown(stripped[2:].strip())}")
            continue
            
        # Regular paragraph
        if in_list:
            # If it's a continuation of a list item
            latex_lines.append(process_inline_markdown(stripped))
        else:
            latex_lines.append(process_inline_markdown(stripped))
            
    if in_list:
        latex_lines.append('\\end{itemize}')
        
    return '\n'.join(latex_lines)

def main():
    parser = argparse.ArgumentParser(description="Compile Markdown to LaTeX PDF")
    parser.add_argument('--content', required=True, help="Path to markdown content file")
    parser.add_argument('--template', required=True, help="Path to LaTeX template")
    parser.add_argument('--output', required=True, help="Path to output PDF")
    args = parser.parse_args()
    
    # 1. Read Markdown
    try:
        with open(args.content, 'r', encoding='utf-8') as f:
            md_content = f.read()
    except FileNotFoundError:
        print(f"Error: Content file not found at {args.content}")
        sys.exit(1)
        
    # 2. Convert to LaTeX snippet
    latex_body = convert_md_to_latex(md_content)
    
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

if __name__ == "__main__":
    main()
