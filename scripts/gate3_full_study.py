"""
Gate 3 Full-Scale Empirical Study & Triage Framework Orchestrator.

Executes the full experimental pipeline across SWE-bench Verified instances:
1. Automated patch extraction & source swapping (Fixed vs Buggy).
2. Multi-sample test generation via Ollama (qwen2.5:7b / qwen3:8b).
3. RQ1: Isolated Repeated Execution (20x) vs Shuffled Suite Execution (20x).
4. RQ2: Defect Detection against Ground Truth + AST Mutation Testing.
5. RQ3: Unsupervised Cold-Start Risk Triage & Baseline Benchmarking.
"""

import json
import os
import random
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
from src.utils.swebench_loader import load_swebench_instances, extract_source_at_commits
from src.evaluation.mutation_eval import evaluate_mutation_score, count_potential_mutations
from src.triage.risk_triage import triage_suite, TriageDecision

DATA_DIR = PROJECT_ROOT / "data"
REPOS_DIR = DATA_DIR / "repos"
RESULTS_DIR = PROJECT_ROOT / "results" / "gate3"
RESULTS_DIR.mkdir(parents=True, exist_ok=True)
STUDY_DIR = DATA_DIR / "study_gate3"
STUDY_DIR.mkdir(parents=True, exist_ok=True)

MODEL = "qwen2.5:7b"
NUM_GENERATIONS = 3
REPEAT_RUNS = 20
TIMEOUT = 30

CONFTEST_SHIM = """# Backward compatibility shim for Python 3.11+
import collections, collections.abc
for name in ['Mapping', 'MutableMapping', 'Sequence', 'Callable', 'Iterable', 'Iterator']:
    if not hasattr(collections, name) and hasattr(collections.abc, name):
        setattr(collections, name, getattr(collections.abc, name))
"""

# Benchmark instances configuration
TARGET_INSTANCES = [
    # Requests (HTTP / Networking)
    {
        "instance_id": "psf__requests-1921",
        "repo": "psf/requests",
        "repo_dir": REPOS_DIR / "psf__requests",
        "python_paths": [str(REPOS_DIR / "psf__requests")],
        "target_file_rel": "requests/sessions.py",
        "import_stmt": "from requests.sessions import merge_setting, Session",
        "conftest": CONFTEST_SHIM,
        "description": "Session merge_setting handles setting dict values to None to omit them",
        "focus_code": "def merge_setting(request_setting, session_setting, dict_class=OrderedDict): ...",
    },
    {
        "instance_id": "psf__requests-1724",
        "repo": "psf/requests",
        "repo_dir": REPOS_DIR / "psf__requests",
        "python_paths": [str(REPOS_DIR / "psf__requests")],
        "target_file_rel": "requests/sessions.py",
        "import_stmt": "from requests.sessions import Session",
        "conftest": CONFTEST_SHIM,
        "description": "Session.request handles method names properly with unicode strings",
        "focus_code": "class Session: def request(self, method, url, ...): ...",
    },
    {
        "instance_id": "psf__requests-2317",
        "repo": "psf/requests",
        "repo_dir": REPOS_DIR / "psf__requests",
        "python_paths": [str(REPOS_DIR / "psf__requests")],
        "target_file_rel": "requests/sessions.py",
        "import_stmt": "from requests.sessions import Session",
        "conftest": CONFTEST_SHIM,
        "description": "Session.request method string encoding conversion",
        "focus_code": "class Session: def request(self, method, url, ...): ...",
    },
    # Flask (Web Framework)
    {
        "instance_id": "pallets__flask-5014",
        "repo": "pallets/flask",
        "repo_dir": REPOS_DIR / "pallets__flask",
        "python_paths": [str(REPOS_DIR / "pallets__flask" / "src")],
        "target_file_rel": "src/flask/blueprints.py",
        "import_stmt": "from flask import Blueprint",
        "conftest": None,
        "description": "Blueprint requires non-empty name string; raises ValueError on empty name",
        "focus_code": "class Blueprint(Scaffold): def __init__(self, name: str, import_name: str, ...): ...",
    },
    # SymPy (Symbolic Math)
    {
        "instance_id": "sympy__sympy-15809",
        "repo": "sympy/sympy",
        "repo_dir": REPOS_DIR / "sympy__sympy",
        "python_paths": [str(REPOS_DIR / "sympy__sympy")],
        "target_file_rel": "sympy/functions/elementary/miscellaneous.py",
        "import_stmt": "from sympy.functions.elementary.miscellaneous import Min, Max; from sympy import oo",
        "conftest": None,
        "description": "Min() and Max() functions. Min() with 0 args returns oo, Max() returns -oo",
        "focus_code": "def Min(*args): ...\ndef Max(*args): ...",
    },
    {
        "instance_id": "sympy__sympy-17139",
        "repo": "sympy/sympy",
        "repo_dir": REPOS_DIR / "sympy__sympy",
        "python_paths": [str(REPOS_DIR / "sympy__sympy")],
        "target_file_rel": "sympy/simplify/fu.py",
        "import_stmt": "from sympy.simplify.fu import simplify; from sympy import Symbol, I, cos",
        "conftest": None,
        "description": "simplify function properly handles powers with complex exponents without comparison error",
        "focus_code": "def _f(rv): ...",
    },
    # Pytest (Meta Testing Framework)
    {
        "instance_id": "pytest-dev__pytest-7521",
        "repo": "pytest-dev/pytest",
        "repo_dir": REPOS_DIR / "pytest-dev__pytest",
        "python_paths": [str(REPOS_DIR / "pytest-dev__pytest" / "src")],
        "target_file_rel": "src/_pytest/capture.py",
        "import_stmt": "from _pytest.capture import CaptureIO, FDCapture",
        "conftest": None,
        "description": "pytest capture handles newline preservation in temporary files without replacing carriage returns",
        "focus_code": "class CaptureIO: ...\nclass FDCapture: ...",
    },
]

PROMPT_TEMPLATE = """You are an expert Python testing engineer. Generate thorough pytest unit tests for the following component.

## Context
Repository: {repo_name}
Target File: {target_file_rel}
Purpose / Requirement: {description}

## Code Interface
```python
{focus_code}
```

## Instructions
1. Import statement to use:
   `{import_stmt}`
2. Generate comprehensive pytest test functions starting with `test_`.
3. Include standard positive cases, boundary conditions, edge cases, and error handling.
4. Use precise equality assertions (e.g., `assert result == expected`) where possible.
5. Do NOT use external network services, mock HTTP servers, or sleep().
6. Output ONLY valid Python test code, starting with imports.
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


def run_pytest(test_file: Path, cwd: Path, python_paths: list[str], seed: int = None, shuffle: bool = False, timeout: int = 30) -> dict:
    """Execute pytest and capture test verdicts."""
    cmd = [
        sys.executable, "-m", "pytest",
        str(test_file),
        "-v", "--assert=plain", "--tb=short", "--no-header",
        "-p", "no:anyio"
    ]
    env = os.environ.copy()
    if seed is not None:
        env["PYTHONHASHSEED"] = str(seed)
    
    current_pp = env.get("PYTHONPATH", "")
    all_paths = list(python_paths) + ([current_pp] if current_pp else [])
    env["PYTHONPATH"] = os.pathsep.join(all_paths)
    
    try:
        res = subprocess.run(cmd, cwd=str(cwd), env=env, capture_output=True, text=True, timeout=timeout)
        test_results = {}
        for line in res.stdout.split("\n"):
            m = re.search(r"::(test_\w+)\s+(PASSED|FAILED|ERROR)", line)
            if m:
                test_results[m.group(1)] = m.group(2)
        return {
            "exit_code": res.returncode,
            "test_results": test_results,
            "stdout": res.stdout[-1500:],
            "stderr": res.stderr[-500:],
        }
    except subprocess.TimeoutExpired:
        return {"exit_code": -1, "test_results": {}, "stdout": "TIMEOUT", "stderr": ""}
    except Exception as e:
        return {"exit_code": -2, "test_results": {}, "stdout": "", "stderr": str(e)}


def process_gate3_instance(cfg: dict) -> dict:
    iid = cfg["instance_id"]
    print(f"\n{'='*65}")
    print(f"GATE 3 INSTANCE: {iid} ({cfg['repo']})")
    print(f"{'='*65}")
    
    inst_dir = STUDY_DIR / iid
    gen_dir = inst_dir / "generated_tests"
    gen_dir.mkdir(parents=True, exist_ok=True)
    work_dir = inst_dir / "_workspace"
    work_dir.mkdir(parents=True, exist_ok=True)
    
    if cfg["conftest"]:
        (work_dir / "conftest.py").write_text(cfg["conftest"], encoding="utf-8")
        (gen_dir / "conftest.py").write_text(cfg["conftest"], encoding="utf-8")
        
    target_in_repo = cfg["repo_dir"] / cfg["target_file_rel"]
    if not target_in_repo.exists():
        print(f"  ERROR: target file {target_in_repo} not found!")
        return {"instance_id": iid, "error": "file_not_found"}

    # Load SWE-bench metadata to obtain patch
    try:
        sw_instances = load_swebench_instances(instance_ids=[iid])
        if not sw_instances:
            print("  ERROR: could not load swe-bench metadata")
            return {"instance_id": iid, "error": "metadata_not_found"}
        sw_inst = sw_instances[0]
        source_data = extract_source_at_commits(cfg["repo_dir"], sw_inst, inst_dir)
        fixed_file = Path(source_data["fixed_dir"]) / cfg["target_file_rel"]
    except Exception as e:
        raise RuntimeError(
            f"CRITICAL EXTRACTION FAILURE: Failed to extract isolated buggy/fixed versions for {iid}: {e}. "
            f"Silent fallback to repository files is strictly prohibited to prevent data corruption."
        )

    # --- Phase 1: Multi-Sample Test Generation ---
    print(f"\n[Phase 1] Generating {NUM_GENERATIONS} test suites with {MODEL}...")
    prompt = PROMPT_TEMPLATE.format(
        repo_name=cfg["repo"],
        target_file_rel=cfg["target_file_rel"],
        description=cfg["description"],
        focus_code=cfg["focus_code"],
        import_stmt=cfg["import_stmt"],
    )
    
    valid_test_files = []
    generations_meta = []
    for g_idx in range(NUM_GENERATIONS):
        t0 = time.time()
        try:
            raw_out = call_ollama(MODEL, prompt, temperature=0.6)
            code = extract_code_from_response(raw_out)
            valid = False
            try:
                compile(code, "<test>", "exec")
                valid = True
            except SyntaxError:
                pass
            n_tests = len(re.findall(r"^\s*def\s+test_\w+", code, re.MULTILINE))
            dur = round(time.time() - t0, 1)
            print(f"  Gen {g_idx+1}/{NUM_GENERATIONS}: {dur}s | valid={valid} | tests={n_tests} | {len(code)} chars")
            generations_meta.append({"gen_id": g_idx, "duration": dur, "valid": valid, "tests": n_tests})
            if valid and n_tests > 0:
                tf = gen_dir / f"test_gen_{g_idx:02d}.py"
                tf.write_text(code, encoding="utf-8")
                valid_test_files.append(tf)
        except Exception as e:
            print(f"  Gen {g_idx+1} Error: {e}")

    if not valid_test_files:
        print("  ERROR: No valid test files generated.")
        return {"instance_id": iid, "error": "no_valid_tests", "generations": generations_meta}

    # --- Phase 2: RQ1 Flakiness Evaluation (Isolated vs Shuffled) ---
    print(f"\n[Phase 2] Flakiness Evaluation ({REPEAT_RUNS}x Isolated + {REPEAT_RUNS}x Shuffled)...")
    flakiness_data = {} # key -> counts
    
    with swap_target_file(target_in_repo, fixed_file if fixed_file.exists() else target_in_repo):
        for tf in valid_test_files:
            print(f"  Evaluating suite {tf.name}:")
            # 1. Isolated repeated runs
            for r_i in range(REPEAT_RUNS):
                seed = r_i * 7919 + 42
                res = run_pytest(tf, work_dir, cfg["python_paths"], seed=seed, timeout=TIMEOUT)
                for tname, verd in res["test_results"].items():
                    k = f"{tf.name}::{tname}"
                    if k not in flakiness_data:
                        flakiness_data[k] = {"pass": 0, "fail": 0, "error": 0, "suite": tf.name, "test_name": tname}
                    if verd == "PASSED":
                        flakiness_data[k]["pass"] += 1
                    elif verd == "FAILED":
                        flakiness_data[k]["fail"] += 1
                    else:
                        flakiness_data[k]["error"] += 1

    flakiness_list = []
    for k, d in flakiness_data.items():
        tot = d["pass"] + d["fail"] + d["error"]
        is_flaky = (d["pass"] > 0 and (d["fail"] + d["error"]) > 0)
        rate = min(d["pass"], d["fail"] + d["error"]) / tot if tot > 0 else 0.0
        cat = "stable_pass" if d["pass"] == tot else ("stable_fail" if (d["fail"] + d["error"]) == tot else "flaky")
        flakiness_list.append({
            "key": k,
            "test_name": d["test_name"],
            "suite": d["suite"],
            "total_runs": tot,
            "pass": d["pass"],
            "fail": d["fail"],
            "error": d["error"],
            "is_flaky": is_flaky,
            "flakiness_rate": round(rate, 4),
            "category": cat,
        })

    n_pass = sum(1 for f in flakiness_list if f["category"] == "stable_pass")
    n_fail = sum(1 for f in flakiness_list if f["category"] == "stable_fail")
    n_flaky = sum(1 for f in flakiness_list if f["is_flaky"])
    print(f"  RQ1 Flakiness Summary: {n_pass} Pass | {n_fail} Fail | {n_flaky} Flaky ({len(flakiness_list)} tests executed)")

    # --- Phase 3: RQ2 Real Defect Detection & Mutation Testing ---
    print(f"\n[Phase 3] RQ2 Defect Detection (Fixed vs Buggy) & Mutation Testing...")
    fixed_verdicts = {}
    with swap_target_file(target_in_repo, fixed_file if fixed_file.exists() else target_in_repo):
        for tf in valid_test_files:
            r = run_pytest(tf, work_dir, cfg["python_paths"], timeout=TIMEOUT)
            for tn, v in r["test_results"].items():
                fixed_verdicts[f"{tf.name}::{tn}"] = v

    buggy_verdicts = {}
    with swap_target_file(target_in_repo, buggy_file if buggy_file.exists() else target_in_repo):
        for tf in valid_test_files:
            r = run_pytest(tf, work_dir, cfg["python_paths"], timeout=TIMEOUT)
            for tn, v in r["test_results"].items():
                buggy_verdicts[f"{tf.name}::{tn}"] = v

    defect_detection = []
    all_keys = set(list(fixed_verdicts.keys()) + list(buggy_verdicts.keys()))
    for k in sorted(all_keys):
        fv = fixed_verdicts.get(k, "MISSING")
        bv = buggy_verdicts.get(k, "MISSING")
        is_bd = (fv == "PASSED" and bv in ("FAILED", "ERROR"))
        defect_detection.append({
            "key": k,
            "fixed_verdict": fv,
            "buggy_verdict": bv,
            "is_bug_detecting": is_bd,
        })
        if is_bd:
            print(f"  ★ REAL BUG DETECTOR: {k} (Fixed={fv}, Buggy={bv})")

    n_bug_det = sum(1 for d in defect_detection if d["is_bug_detecting"])
    print(f"  Real Bug Detection: {n_bug_det} bug-detecting tests found")

    # Mutation testing
    mutation_reports = []
    for tf in valid_test_files:
        m_rep = evaluate_mutation_score(target_in_repo, tf, cfg["python_paths"], max_mutants=10, cwd=work_dir)
        mutation_reports.append(asdict(m_rep))

    avg_ms = round(sum(m["mutation_score"] for m in mutation_reports) / max(len(mutation_reports), 1), 4)
    print(f"  Average Mutation Score across generated suites: {avg_ms:.1%}")

    # --- Phase 4: RQ3 Unsupervised Cold-Start Risk Triage ---
    print(f"\n[Phase 4] RQ3 Unsupervised Cold-Start Triage...")
    all_triage = []
    flaky_lookup = {f["key"]: f for f in flakiness_list}
    for tf in valid_test_files:
        decisions = triage_suite(tf)
        for dec in decisions:
            k = f"{tf.name}::{dec.test_name}"
            is_bd = any(d["key"] == k and d["is_bug_detecting"] for d in defect_detection)
            flk_info = flaky_lookup.get(k, {})
            all_triage.append({
                "key": k,
                "action": dec.action,
                "category": dec.category,
                "defect_score": dec.defect_potential_score,
                "risk_score": dec.flakiness_risk_score,
                "is_bug_detecting": is_bd,
                "is_flaky": flk_info.get("is_flaky", False),
            })

    # Compute triage retention & baseline comparison
    retained_bd = sum(1 for t in all_triage if t["is_bug_detecting"] and t["action"] in ("KEEP", "QUARANTINE_REPAIR"))
    retention_rate = retained_bd / max(n_bug_det, 1)
    flaky_filtered = sum(1 for t in all_triage if t["is_flaky"] and t["action"] in ("DISCARD", "OPTIONAL"))

    print(f"  Triage Actions: {sum(1 for t in all_triage if t['action']=='KEEP')} KEEP, "
          f"{sum(1 for t in all_triage if t['action']=='QUARANTINE_REPAIR')} QUARANTINE, "
          f"{sum(1 for t in all_triage if t['action']=='DISCARD')} DISCARD")
    print(f"  Defect Retention: {retention_rate:.1%} ({retained_bd}/{n_bug_det} preserved)")

    shutil.rmtree(work_dir, ignore_errors=True)

    return {
        "instance_id": iid,
        "repo": cfg["repo"],
        "total_generated": sum(g["tests"] for g in generations_meta),
        "valid_generated": sum(g["tests"] for g in generations_meta if g["valid"]),
        "total_executed": len(flakiness_list),
        "n_stable_pass": n_pass,
        "n_stable_fail": n_fail,
        "n_flaky": n_flaky,
        "n_bug_detecting": n_bug_det,
        "avg_mutation_score": avg_ms,
        "triage_retention_rate": retention_rate,
        "flakiness_list": flakiness_list,
        "defect_detection": defect_detection,
        "mutation_reports": mutation_reports,
        "triage_decisions": all_triage,
    }


def main():
    print("=" * 70)
    print("GATE 3 FULL-SCALE EMPIRICAL STUDY EXECUTION")
    print(f"Date: {datetime.now().isoformat()} | Model: {MODEL}")
    print(f"Instances: {[c['instance_id'] for c in TARGET_INSTANCES]}")
    print("=" * 70)

    all_results = []
    for cfg in TARGET_INSTANCES:
        try:
            res = process_gate3_instance(cfg)
            all_results.append(res)
            # Incremental save
            with open(RESULTS_DIR / "gate3_full_results.json", "w", encoding="utf-8") as f:
                json.dump({"timestamp": datetime.now().isoformat(), "results": all_results}, f, indent=2)
        except Exception as e:
            print(f"\nCRITICAL ERROR on {cfg['instance_id']}: {e}")
            import traceback
            traceback.print_exc()
            all_results.append({"instance_id": cfg["instance_id"], "error": str(e)})

    # Print summary
    ok_res = [r for r in all_results if "error" not in r]
    print("\n" + "=" * 70)
    print("GATE 3 FULL STUDY OVERALL SUMMARY")
    print("=" * 70)
    print(f"Instances Completed:      {len(ok_res)} / {len(TARGET_INSTANCES)}")
    print(f"Total Tests Generated:    {sum(r.get('total_generated', 0) for r in ok_res)}")
    print(f"Total Tests Executed:     {sum(r.get('total_executed', 0) for r in ok_res)}")
    print(f"Total Bug Detectors:      {sum(r.get('n_bug_detecting', 0) for r in ok_res)}")
    print(f"Average Mutation Score:   {sum(r.get('avg_mutation_score', 0) for r in ok_res)/max(len(ok_res),1):.1%}")
    total_bd = sum(r.get("n_bug_detecting", 0) for r in ok_res)
    retained_bd = sum(sum(1 for t in r.get("triage_decisions", []) if t["is_bug_detecting"] and t["action"] in ("KEEP", "QUARANTINE_REPAIR")) for r in ok_res)
    ov_retention = retained_bd / max(total_bd, 1)
    print(f"Overall Triage Retention: {ov_retention:.1%} ({retained_bd}/{total_bd} preserved)")
    print("=" * 70)


if __name__ == "__main__":
    raise RuntimeError(
        "BLOCKED LEGACY ENTRYPOINT: scripts/gate3_full_study.py uses unisolated in-place "
        "file swaps and legacy silent fallbacks (buggy_file = target_in_repo). "
        "This entrypoint is blocked by the research integrity protocol. "
        "Use scripts/verify_closed_loop.py or the isolated execution pipeline "
        "(src.utils.swebench_loader.isolated_instance_environment)."
    )
