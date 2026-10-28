"""
Test pilot generation for DeepSeek-Coder and CodeLlama.
"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.generation.generate_tests import generate_tests
from src.utils.swebench_loader import load_swebench_instances, isolated_instance_environment

all_swebench = load_swebench_instances()
inst = next(i for i in all_swebench if i.instance_id == "psf__requests-1724")
repo_dir = Path("data/repos/psf__requests")

with isolated_instance_environment(repo_dir, inst, version="buggy") as wt:
    source_file = wt / "requests/sessions.py"
    source_code = source_file.read_text(encoding="utf-8", errors="ignore")
    if len(source_code.splitlines()) > 1000:
        source_code = "\n".join(source_code.splitlines()[:800])

for model_name in ["deepseek-coder:6.7b", "codellama:7b"]:
    print(f"\n--- Testing {model_name} on {inst.instance_id} ---")
    res = generate_tests(
        source_code=source_code,
        filepath="requests/sessions.py",
        model=model_name,
        template="basic",
        temperature=0.7,
    )
    code = res["test_code"]
    lines = code.splitlines()
    print(f"Generated {len(lines)} lines.")
    print("Preview:\n" + "\n".join(lines[:10]))
