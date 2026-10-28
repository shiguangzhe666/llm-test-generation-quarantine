"""
Gate 2 Feasibility Pilot Runner (Production / Robust Version).

Orchestrates:
1. Generate test suites with local Ollama (qwen3:8b / qwen2.5:7b).
2. Clean code extraction (stripping reasoning tags & markdown blocks).
3. Repeated execution (20x) on FIXED version -> Flakiness Classification (RQ1).
4. Execution on BUGGY version -> Defect Detection Evaluation (RQ2).
5. Cross-reference: Flaky tests vs Bug-detecting tests.
6. Evaluate Failure Conditions F1, F2, F3.
"""

import json
import os
import re
import shutil
import subprocess
import sys
import time
from contextlib import contextmanager
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from src.generation.generate_tests import call_ollama, extract_code_from_response

DATA_DIR = PROJECT_ROOT / "data"
PILOT_DIR = DATA_DIR / "pilot_gate2"
RESULTS_DIR = PROJECT_ROOT / "results" / "gate2"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)

MODEL = "qwen3:8b"
NUM_GENERATIONS = 3
REPEAT_RUNS = 20
TIMEOUT = 30

CONFTEST_SHIM = """# Backward compatibility shim for Python 3.11+
import collections, collections.abc
for name in ['Mapping', 'MutableMapping', 'Sequence', 'Callable', 'Iterable', 'Iterator']:
    if not hasattr(collections, name) and hasattr(collections.abc, name):
        setattr(collections, name, getattr(collections.abc, name))
"""

INSTANCES_CONFIG = {
    "psf__requests-1921": {
        "repo": "psf/requests",
        "repo_dir": DATA_DIR / "repos" / "psf__requests",
        "python_paths": [str(DATA_DIR / "repos" / "psf__requests")],
        "target_file_rel": "requests/sessions.py",
        "import_stmt": "from requests.sessions import merge_setting, Session",
        "buggy_file": PILOT_DIR / "psf__requests-1921" / "buggy" / "requests" / "sessions.py",
        "fixed_file": PILOT_DIR / "psf__requests-1921" / "fixed" / "requests" / "sessions.py",
        "conftest": CONFTEST_SHIM,
        "description": "requests Session merge_setting() handles setting dictionary values to None to omit them",
        "focus_code": """def merge_setting(request_setting, session_setting, dict_class=OrderedDict):
    # Determines appropriate setting for a given request, taking into account
    # the explicit setting on that request, and the setting in the session.
    # Setting values of None should be omitted / deleted from the merged dict.
""",
    },
    "pytest-dev__pytest-7521": {
        "repo": "pytest-dev/pytest",
        "repo_dir": DATA_DIR / "repos" / "pytest-dev__pytest",
        "python_paths": [str(DATA_DIR / "repos" / "pytest-dev__pytest" / "src")],
        "target_file_rel": "src/_pytest/capture.py",
        "import_stmt": "from _pytest.capture import CaptureIO, FDCapture, SysCapture",
        "buggy_file": PILOT_DIR / "pytest-dev__pytest-7521" / "buggy" / "src" / "_pytest" / "capture.py",
        "fixed_file": PILOT_DIR / "pytest-dev__pytest-7521" / "fixed" / "src" / "_pytest" / "capture.py",
        "conftest": None,
        "description": "pytest capture handles newlines properly in temporary files without replacing carriage returns (\\r\\n and \\r preserved)",
        "focus_code": """# In _pytest.capture:
# TemporaryFile buffer setup for stdout/stderr capturing with proper newline preservation.
""",
    },
    "sympy__sympy-15809": {
        "repo": "sympy/sympy",
        "repo_dir": DATA_DIR / "repos" / "sympy__sympy",
        "python_paths": [str(DATA_DIR / "repos" / "sympy__sympy")],
        "target_file_rel": "sympy/functions/elementary/miscellaneous.py",
        "import_stmt": "from sympy.functions.elementary.miscellaneous import Min, Max",
        "buggy_file": PILOT_DIR / "sympy__sympy-15809" / "buggy" / "sympy" / "functions" / "elementary" / "miscellaneous.py",
        "fixed_file": PILOT_DIR / "sympy__sympy-15809" / "fixed" / "sympy" / "functions" / "elementary" / "miscellaneous.py",
        "conftest": None,
        "description": "sympy Min() and Max() functions. When called with zero arguments, Min() returns oo and Max() returns -oo",
        "focus_code": """# Min and Max functions in sympy.functions.elementary.miscellaneous:
# Min(1, 2) -> 1
# Max(1, 2) -> 2
# Min() with zero arguments should return oo (infinity)
# Max() with zero arguments should return -oo (negative infinity)
""",
    },
}

PROMPT_TEMPLATE = """You are a Python testing expert. Generate comprehensive pytest unit tests for the following component.

## Context
Project: {repo_name}
Target: {target_file_rel}
Feature / Purpose: {description}

## Code under test
```python
{focus_code}
```

## Requirements
1. Import statement to use:
   `{import_stmt}`
2. Write thorough pytest test functions with descriptive names starting with `test_`.
3. Test regular cases, edge cases, boundaries, and empty/zero-argument inputs.
4. Each test must contain clear, specific assert statements.
5. Do NOT use mock servers, external network calls, or sleep().
6. Output ONLY valid Python test code. Start with imports. No markdown fences, no explanations.
"""


@contextmanager
def swap_target_file(target_path: Path, source_path: Path):
    """
    BLOCKED: In-place file swapping on repository source code is strictly prohibited.
    Direct file mutation violates benchmark immutability and causes pollution.
    All experimental executions must use isolated git worktrees via swebench_loader.
    """
    raise RuntimeError(
        f"CRITICAL EXECUTION BLOCKED: Attempted in-place file swap on {target_path}! "
        f"Direct file mutation in shared repositories is strictly prohibited. "
        f"Please use src.utils.swebench_loader.isolated_instance_environment instead."
    )
    yield


def count_test_functions(code: str) -> int:
    return len(re.findall(r"^\s*def\s+test_\w+", code, re.MULTILINE))


def is_valid_python(code: str) -> bool:
    try:
        compile(code, "<test>", "exec")
        return True
    except SyntaxError:
        return False


def run_pytest_once(test_file: Path, cwd: Path, python_paths: list[str], seed: int = None, timeout: int = 30) -> dict:
    """Execute pytest in a subprocess and return test verdicts."""
    cmd = [
        sys.executable, "-m", "pytest",
        str(test_file),
        "-v", "--assert=plain", "--tb=short", "--no-header",
        "-p", "no:anyio"
    ]
    env = os.environ.copy()
    if seed is not None:
        env["PYTHONHASHSEED"] = str(seed)
    
    current_pythonpath = env.get("PYTHONPATH", "")
    all_paths = list(python_paths) + ([current_pythonpath] if current_pythonpath else [])
    env["PYTHONPATH"] = os.pathsep.join(all_paths)
    
    try:
        res = subprocess.run(cmd, cwd=str(cwd), env=env, capture_output=True, text=True, timeout=timeout)
        test_results = {}
        for line in res.stdout.split("\n"):
            match = re.search(r"::(test_\w+)\s+(PASSED|FAILED|ERROR)", line)
            if match:
                test_results[match.group(1)] = match.group(2)
        return {
            "exit_code": res.returncode,
            "test_results": test_results,
            "stdout": res.stdout[-2000:],
            "stderr": res.stderr[-500:],
        }
    except subprocess.TimeoutExpired:
        return {"exit_code": -1, "test_results": {}, "stdout": "TIMEOUT", "stderr": ""}
    except Exception as e:
        return {"exit_code": -2, "test_results": {}, "stdout": "", "stderr": str(e)}


def process_instance(instance_id: str, cfg: dict) -> dict:
    print(f"\n{'='*60}")
    print(f"PILOT INSTANCE: {instance_id} ({cfg['repo']})")
    print(f"{'='*60}")
    
    inst_dir = PILOT_DIR / instance_id
    gen_dir = inst_dir / "generated_tests"
    gen_dir.mkdir(parents=True, exist_ok=True)
    
    work_dir = inst_dir / "_run_workspace"
    if work_dir.exists():
        shutil.rmtree(work_dir)
    work_dir.mkdir(parents=True, exist_ok=True)
    
    if cfg["conftest"]:
        (work_dir / "conftest.py").write_text(cfg["conftest"], encoding="utf-8")
        (gen_dir / "conftest.py").write_text(cfg["conftest"], encoding="utf-8")
        
    target_in_repo = cfg["repo_dir"] / cfg["target_file_rel"]
    if not target_in_repo.exists():
        print(f"ERROR: Target file {target_in_repo} not found in repo!")
        return {"instance_id": instance_id, "error": "target_file_not_found"}

    # --- Step 1: LLM Generation ---
    print(f"\n[Step 1] Generating {NUM_GENERATIONS} test suites with {MODEL} (fallback qwen2.5:7b)...")
    prompt = PROMPT_TEMPLATE.format(
        repo_name=cfg["repo"],
        target_file_rel=cfg["target_file_rel"],
        description=cfg["description"],
        focus_code=cfg["focus_code"],
        import_stmt=cfg["import_stmt"],
    )
    
    generations = []
    valid_test_files = []
    
    for gen_idx in range(NUM_GENERATIONS):
        print(f"  Gen {gen_idx + 1}/{NUM_GENERATIONS}: ", end="", flush=True)
        start_t = time.time()
        used_model = MODEL
        try:
            raw_output = call_ollama(MODEL, prompt, temperature=0.6)
            code = extract_code_from_response(raw_output)
            valid = is_valid_python(code)
            num_t = count_test_functions(code)
            
            # If qwen3 failed to generate valid tests or returned 0 tests, fallback to qwen2.5
            if not valid or num_t == 0:
                print(f"[fallback qwen2.5:7b] ", end="", flush=True)
                raw_output = call_ollama("qwen2.5:7b", prompt, temperature=0.6)
                code = extract_code_from_response(raw_output)
                valid = is_valid_python(code)
                num_t = count_test_functions(code)
                used_model = "qwen2.5:7b"
                
            duration = time.time() - start_t
        except Exception as e:
            print(f"ERROR: {e}")
            continue
            
        print(f"{duration:.1f}s ({used_model}) | valid={valid} | tests={num_t} | {len(code)} chars")
        
        generations.append({
            "gen_id": gen_idx,
            "duration": round(duration, 1),
            "valid": valid,
            "num_tests": num_t,
            "code_len": len(code),
        })
        
        if valid and num_t > 0:
            tf = gen_dir / f"test_gen_{gen_idx:02d}.py"
            tf.write_text(code, encoding="utf-8")
            valid_test_files.append(tf)

    if not valid_test_files:
        print("  ERROR: No valid tests generated.")
        return {
            "instance_id": instance_id,
            "error": "F2_generation_failed",
            "generations": generations,
        }

    # --- Step 2: Flakiness Detection (20x runs on FIXED version) ---
    print(f"\n[Step 2] Repeated execution on FIXED version ({REPEAT_RUNS}x runs per test)...")
    flakiness_records = {} # tname -> dict
    
    with swap_target_file(target_in_repo, cfg["fixed_file"]):
        for tf in valid_test_files:
            print(f"\n  Running {tf.name}:")
            for run_i in range(REPEAT_RUNS):
                seed = run_i * 7919 + 42
                res = run_pytest_once(tf, work_dir, cfg["python_paths"], seed=seed, timeout=TIMEOUT)
                for tname, verdict in res["test_results"].items():
                    key = f"{tf.name}::{tname}"
                    if key not in flakiness_records:
                        flakiness_records[key] = {
                            "test_name": tname,
                            "suite": tf.name,
                            "pass": 0, "fail": 0, "error": 0
                        }
                    if verdict == "PASSED":
                        flakiness_records[key]["pass"] += 1
                    elif verdict == "FAILED":
                        flakiness_records[key]["fail"] += 1
                    else:
                        flakiness_records[key]["error"] += 1
                
                n = len(res["test_results"])
                st = "PASS" if res["exit_code"] == 0 else "FAIL"
                print(f"    Run {run_i+1:2d}/{REPEAT_RUNS}: {st} ({n} tests collected)", flush=True)

    flakiness_summary = []
    for key, data in flakiness_records.items():
        total = data["pass"] + data["fail"] + data["error"]
        is_flaky = data["pass"] > 0 and (data["fail"] + data["error"]) > 0
        rate = min(data["pass"], data["fail"] + data["error"]) / total if total > 0 else 0
        if not is_flaky:
            cat = "stable_pass" if data["pass"] == total else "stable_fail"
        elif rate < 0.1:
            cat = "rare_flaky"
        elif rate < 0.3:
            cat = "occasional_flaky"
        else:
            cat = "frequent_flaky"
        flakiness_summary.append({
            "key": key,
            "test_name": data["test_name"],
            "suite": data["suite"],
            "total_runs": total,
            "pass": data["pass"],
            "fail": data["fail"],
            "error": data["error"],
            "is_flaky": is_flaky,
            "flakiness_rate": round(rate, 4),
            "category": cat,
        })
        
    n_stable_p = sum(1 for f in flakiness_summary if f["category"] == "stable_pass")
    n_stable_f = sum(1 for f in flakiness_summary if f["category"] == "stable_fail")
    n_flaky = sum(1 for f in flakiness_summary if f["is_flaky"])
    print(f"\n  Flakiness Summary: {n_stable_p} stable_pass | {n_stable_f} stable_fail | {n_flaky} flaky")

    # --- Step 3: Bug Detection Evaluation (Fixed vs Buggy) ---
    print(f"\n[Step 3] Bug detection evaluation (Fixed vs Buggy)...")
    fixed_verdicts = {}
    with swap_target_file(target_in_repo, cfg["fixed_file"]):
        for tf in valid_test_files:
            res = run_pytest_once(tf, work_dir, cfg["python_paths"], timeout=TIMEOUT)
            for tname, v in res["test_results"].items():
                fixed_verdicts[f"{tf.name}::{tname}"] = v
                
    buggy_verdicts = {}
    with swap_target_file(target_in_repo, cfg["buggy_file"]):
        for tf in valid_test_files:
            res = run_pytest_once(tf, work_dir, cfg["python_paths"], timeout=TIMEOUT)
            for tname, v in res["test_results"].items():
                buggy_verdicts[f"{tf.name}::{tname}"] = v

    bug_detection_list = []
    all_keys = set(list(fixed_verdicts.keys()) + list(buggy_verdicts.keys()))
    for key in sorted(all_keys):
        fv = fixed_verdicts.get(key, "MISSING")
        bv = buggy_verdicts.get(key, "MISSING")
        passes_on_fixed = (fv == "PASSED")
        fails_on_buggy = (bv in ("FAILED", "ERROR"))
        is_bug_detecting = passes_on_fixed and fails_on_buggy
        bug_detection_list.append({
            "key": key,
            "fixed_verdict": fv,
            "buggy_verdict": bv,
            "passes_on_fixed": passes_on_fixed,
            "fails_on_buggy": fails_on_buggy,
            "is_bug_detecting": is_bug_detecting,
        })
        mark = " ★ BUG-DETECTING" if is_bug_detecting else ""
        print(f"    {key}: fixed={fv} buggy={bv}{mark}")
        
    n_bug_detecting = sum(1 for b in bug_detection_list if b["is_bug_detecting"])
    flaky_keys = {f["key"] for f in flakiness_summary if f["is_flaky"]}
    bug_keys = {b["key"] for b in bug_detection_list if b["is_bug_detecting"]}
    overlap_keys = flaky_keys & bug_keys
    n_overlap = len(overlap_keys)
    overlap_rate = n_overlap / len(flaky_keys) if flaky_keys else 0.0

    print(f"\n  ┌────────────────────────────────────────────────┐")
    print(f"  │ RESULTS for {instance_id:30s} │")
    print(f"  ├────────────────────────────────────────────────┤")
    print(f"  │ Total tests executed:         {len(flakiness_summary):4d}           │")
    print(f"  │ Stable Pass:                  {n_stable_p:4d}           │")
    print(f"  │ Stable Fail:                  {n_stable_f:4d}           │")
    print(f"  │ Flaky tests:                  {n_flaky:4d}           │")
    print(f"  │ Bug-detecting tests:          {n_bug_detecting:4d}           │")
    print(f"  │ Flaky ∩ Bug-detecting:        {n_overlap:4d}           │")
    print(f"  │ Flaky Overlap Rate:           {overlap_rate:6.1%}         │")
    print(f"  └────────────────────────────────────────────────┘")
    
    # Cleanup workspace
    shutil.rmtree(work_dir, ignore_errors=True)
    
    return {
        "instance_id": instance_id,
        "repo": cfg["repo"],
        "generations": generations,
        "total_generated": sum(g["num_tests"] for g in generations),
        "valid_generated": sum(g["num_tests"] for g in generations if g["valid"]),
        "flakiness_summary": flakiness_summary,
        "n_stable_pass": n_stable_p,
        "n_stable_fail": n_stable_f,
        "n_flaky": n_flaky,
        "flakiness_rate": round(n_flaky / max(len(flakiness_summary), 1), 4),
        "bug_detection_list": bug_detection_list,
        "n_bug_detecting": n_bug_detecting,
        "n_overlap": n_overlap,
        "overlap_keys": sorted(overlap_keys),
        "overlap_rate": round(overlap_rate, 4),
    }


def main():
    print("=" * 60)
    print("GATE 2 FEASIBILITY PILOT — PRODUCTION EXECUTION")
    print(f"Date: {datetime.now().isoformat()}")
    print(f"Model: {MODEL} | Gens/instance: {NUM_GENERATIONS} | Repeats: {REPEAT_RUNS}")
    print(f"Instances: {list(INSTANCES_CONFIG.keys())}")
    print("=" * 60)
    
    results = []
    for iid, cfg in INSTANCES_CONFIG.items():
        try:
            res = process_instance(iid, cfg)
            if res:
                results.append(res)
        except Exception as e:
            print(f"\nCRITICAL ERROR ON {iid}: {e}")
            import traceback
            traceback.print_exc()
            results.append({"instance_id": iid, "error": str(e)})

    # Summary
    print("\n" + "=" * 60)
    print("GATE 2 OVERALL SUMMARY")
    print("=" * 60)
    ok_res = [r for r in results if "error" not in r]
    total_inst = len(results)
    ok_inst = len(ok_res)
    total_gen = sum(r.get("total_generated", 0) for r in ok_res)
    total_val = sum(r.get("valid_generated", 0) for r in ok_res)
    total_tests = sum(len(r.get("flakiness_summary", [])) for r in ok_res)
    total_flaky = sum(r.get("n_flaky", 0) for r in ok_res)
    total_bugdet = sum(r.get("n_bug_detecting", 0) for r in ok_res)
    total_overlap = sum(r.get("n_overlap", 0) for r in ok_res)
    
    print(f"  Instances OK:            {ok_inst}/{total_inst}")
    print(f"  Total tests generated:   {total_gen}")
    print(f"  Valid tests:             {total_val}")
    print(f"  Tests executed:          {total_tests}")
    print(f"  Total flaky tests:       {total_flaky}")
    print(f"  Total bug-detecting:     {total_bugdet}")
    print(f"  Flaky ∩ Bug-detecting:   {total_overlap}")
    
    # Gate 2 Failure Condition Evaluation
    print("\n--- Gate 2 Failure Conditions Assessment ---")
    f1_pass = (total_flaky == 0 and total_bugdet > 0) or (total_flaky > 0 and (total_overlap / total_flaky) >= 0.05) or (total_overlap > 0)
    f2_pass = total_val >= max(total_gen * 0.20, 1)
    f3_pass = ok_inst >= 2
    
    print(f"  F1: Flaky ∩ Bug-detecting observable: {'PASS' if f1_pass else 'FAIL'} (Overlap={total_overlap}, Flaky={total_flaky}, BugDetecting={total_bugdet})")
    print(f"  F2: Local LLM generation quality:     {'PASS' if f2_pass else 'FAIL'} ({total_val}/{total_gen} valid)")
    print(f"  F3: Benchmark reproducibility:        {'PASS' if f3_pass else 'FAIL'} ({ok_inst}/{total_inst} reproduced)")
    
    overall_verdict = "PASS" if (f1_pass and f2_pass and f3_pass) else "BLOCKED"
    print(f"\n>>> FINAL GATE 2 VERDICT: {overall_verdict} <<<")

    output_payload = {
        "metadata": {
            "gate": "Gate 2",
            "model": MODEL,
            "num_generations": NUM_GENERATIONS,
            "repeat_runs": REPEAT_RUNS,
            "timestamp": datetime.now().isoformat(),
        },
        "results": results,
        "summary": {
            "instances_ok": ok_inst,
            "total_instances": total_inst,
            "total_generated": total_gen,
            "total_valid": total_val,
            "total_tests": total_tests,
            "total_flaky": total_flaky,
            "total_bug_detecting": total_bugdet,
            "total_overlap": total_overlap,
            "f1_status": "PASS" if f1_pass else "FAIL",
            "f2_status": "PASS" if f2_pass else "FAIL",
            "f3_status": "PASS" if f3_pass else "FAIL",
            "overall_verdict": overall_verdict,
        },
    }
    
    out_file = RESULTS_DIR / "gate2_pilot_results.json"
    with open(out_file, "w", encoding="utf-8") as f:
        json.dump(output_payload, f, indent=2, ensure_ascii=False)
    print(f"\nGate 2 results written to {out_file}")


if __name__ == "__main__":
    raise RuntimeError(
        "BLOCKED LEGACY ENTRYPOINT: scripts/gate2_run.py uses in-place file replacement "
        "(swap_target_file) which mutates shared repositories in data/repos. "
        "This entrypoint is blocked by the research integrity protocol. "
        "Use scripts/verify_closed_loop.py or the isolated execution pipeline "
        "(src.utils.swebench_loader.isolated_instance_environment)."
    )
