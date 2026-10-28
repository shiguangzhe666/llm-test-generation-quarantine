"""
Comprehensive Typesetting, Layout, and Encoding Quality Audit
"""
import os
import re
import glob

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SUBMISSION_DIR = os.path.join(ROOT, "paper", "emse_submission")
PAPER_DIR = os.path.join(ROOT, "paper")

def audit_latex_crossrefs(main_tex_path):
    print("--- 1. Checking LaTeX Labels and Cross-References ---")
    with open(main_tex_path, "r", encoding="utf-8") as f:
        text = f.read()

    # Labels defined via \label{...} OR label={...} in lstlisting
    all_labels = set(re.findall(r"\\label\{([^}]+)\}", text))
    all_labels.update(re.findall(r"label\s*=\s*\{?([a-zA-Z0-9_\:\-]+)\}?", text))

    table_files = glob.glob(os.path.join(SUBMISSION_DIR, "tables", "*.tex"))
    for tf in table_files:
        with open(tf, "r", encoding="utf-8") as f:
            t_content = f.read()
            all_labels.update(re.findall(r"\\label\{([^}]+)\}", t_content))
            all_labels.update(re.findall(r"label\s*=\s*\{?([a-zA-Z0-9_\:\-]+)\}?", t_content))

    # References in main.tex
    refs = set(re.findall(r"\\ref\{([^}]+)\}", text))
    
    missing = refs - all_labels
    if missing:
        print(f"  [FAIL] Missing labels for references: {missing}")
    else:
        print(f"  [PASS] All {len(refs)} \\ref{{...}} references have corresponding labels defined!")

    return missing

def audit_latex_quotes(main_tex_path):
    print("\n--- 2. Checking LaTeX Quotation Marks ---")
    with open(main_tex_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    in_listing = False
    straight_quotes = []
    for idx, line in enumerate(lines, 1):
        stripped = re.sub(r"(?<!\\)%.*$", "", line)
        if "\\begin{lstlisting}" in stripped:
            in_listing = True
            continue
        if "\\end{lstlisting}" in stripped:
            in_listing = False
            continue
        if not in_listing:
            if '"' in stripped:
                straight_quotes.append((idx, line.strip()))

    if straight_quotes:
        print(f"  [NOTE] Found {len(straight_quotes)} line(s) with straight double quotes (\") in LaTeX prose:")
        for idx, l in straight_quotes:
            print(f"    Line {idx}: {l[:90]}")
    else:
        print("  [PASS] Zero straight double quotes in LaTeX text; proper `` ... '' used everywhere.")

    return straight_quotes

def audit_math_subscripts(main_tex_path):
    print("\n--- 3. Checking Math Subscripts Typesetting ---")
    with open(main_tex_path, "r", encoding="utf-8") as f:
        text = f.read()

    word_subs = re.findall(r"\_\{([a-zA-Z]{2,})\}(?!\s*\\mathrm)", text)
    # filter out words already wrapped in \mathrm
    bad_subs = set()
    for m in re.finditer(r"\_\{([a-zA-Z]{2,})\}", text):
        bad_subs.add(m.group(1))

    if bad_subs:
        print(f"  [NOTE] Word subscripts that can be upgraded to \\mathrm: {sorted(bad_subs)}")
    else:
        print("  [PASS] All multi-letter subscripts use \\mathrm styling.")

    return bad_subs

def audit_markdown_syntax(md_path):
    print(f"\n--- Checking Markdown Integrity: {os.path.basename(md_path)} ---")
    with open(md_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    issues = []
    in_code_block = False
    in_table = False
    table_cols = 0

    inline_math = False
    display_math = False

    for idx, line in enumerate(lines, 1):
        stripped = line.strip()

        # Code block tracking
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue
        if in_code_block:
            continue

        # Table check
        if stripped.startswith("|") and stripped.endswith("|"):
            cells = [c.strip() for c in stripped[1:-1].split("|")]
            if not in_table:
                in_table = True
                table_cols = len(cells)
            else:
                if all(re.match(r"^:?-+:?$", c) for c in cells):
                    if len(cells) != table_cols:
                        issues.append(f"Line {idx}: Table separator has {len(cells)} cols, expected {table_cols}")
                else:
                    if len(cells) != table_cols:
                        issues.append(f"Line {idx}: Table row has {len(cells)} cols, expected {table_cols}")
        else:
            in_table = False

        # Math delimiters check ($ outside code)
        # remove inline code `...`
        code_removed = re.sub(r"`[^`]+`", "", line)
        i = 0
        while i < len(code_removed):
            if code_removed[i] == "$" and (i == 0 or code_removed[i - 1] != "\\"):
                if i + 1 < len(code_removed) and code_removed[i + 1] == "$":
                    display_math = not display_math
                    i += 1
                else:
                    inline_math = not inline_math
            i += 1

    if inline_math:
        issues.append("Unclosed inline math delimiter '$'")
    if display_math:
        issues.append("Unclosed display math delimiter '$$'")

    if issues:
        print(f"  [ISSUES] {len(issues)} formatting issue(s) found:")
        for iss in issues[:10]:
            print(f"    - {iss}")
    else:
        print(f"  [PASS] 100% valid Markdown table and KaTeX math syntax!")

    return issues

def main():
    main_tex = os.path.join(SUBMISSION_DIR, "main.tex")
    audit_latex_crossrefs(main_tex)
    audit_latex_quotes(main_tex)
    audit_math_subscripts(main_tex)
    audit_markdown_syntax(os.path.join(PAPER_DIR, "manuscript_en.md"))
    audit_markdown_syntax(os.path.join(PAPER_DIR, "manuscript.md"))

if __name__ == "__main__":
    main()
