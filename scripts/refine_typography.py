"""
Refine LaTeX typography in main.tex:
1. Standardize straight quotes inside code snippets to single quotes.
2. Upgrade multi-letter math subscripts to Roman \mathrm formatting for academic publication.
"""
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAIN_TEX = os.path.join(ROOT, "paper", "emse_submission", "main.tex")

with open(MAIN_TEX, "r", encoding="utf-8") as f:
    text = f.read()

# 1. Straight quotes to single quotes in \texttt
text = text.replace(r'\texttt{requests.get("http://example.com")}', r"\texttt{requests.get('http://example.com')}")
text = text.replace(r'(\texttt{"http://"} or \texttt{"https://"})', r"(\texttt{'http://'} or \texttt{'https://'})")

# 2. Subscripts
sub_map = {
    r"_{bug}": r"_{\mathrm{bug}}",
    r"_{defect}": r"_{\mathrm{defect}}",
    r"_{exec}": r"_{\mathrm{exec}}",
    r"_{fail}": r"_{\mathrm{fail}}",
    r"_{fixed}": r"_{\mathrm{fixed}}",
    r"_{main}": r"_{\mathrm{main}}",
    r"_{pass}": r"_{\mathrm{pass}}",
    r"_{quar}": r"_{\mathrm{quar}}",
    r"_{rate}": r"_{\mathrm{rate}}",
    r"_{spec}": r"_{\mathrm{spec}}",
    r"_{valid}": r"_{\mathrm{valid}}",
}

for old, new in sub_map.items():
    text = text.replace(old, new)

with open(MAIN_TEX, "w", encoding="utf-8") as f:
    f.write(text)

print(f"Refined typography in {MAIN_TEX} successfully.")
