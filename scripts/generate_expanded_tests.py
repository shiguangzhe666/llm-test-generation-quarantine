"""
Batch test generation for Path B expansion instances.
Generates 3 independent test suites per instance using Ollama qwen3:8b.
Strict information isolation: only feeds base_commit source code, NO patch/test_patch leakage.
"""
import sys
import json
import hashlib
import time
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(r"F:\论文\llm-test-stability")
sys.path.insert(0, str(PROJECT_ROOT))

from src.utils.swebench_loader import load_swebench_instances, isolated_instance_environment
from src.generation.generate_tests import generate_tests, extract_code_from_response

NUM_RUNS = 3
MODEL = "qwen3:8b"
TEMPERATURE = 0.7

# 10 new instances to generate tests for
NEW_INSTANCES = [
    {
        "instance_id": "psf__requests-1766",
        "repo_dir_name": "psf__requests",
        "target_file_rel": "requests/auth.py",
    },
    {
        "instance_id": "psf__requests-6028",
        "repo_dir_name": "psf__requests",
        "target_file_rel": "requests/utils.py",
    },
    {
        "instance_id": "sympy__sympy-17630",
        "repo_dir_name": "sympy__sympy",
        "target_file_rel": "sympy/matrices/expressions/matexpr.py",
    },
    {
        "instance_id": "sympy__sympy-21930",
        "repo_dir_name": "sympy__sympy",
        "target_file_rel": "sympy/physics/secondquant.py",
    },
    {
        "instance_id": "sympy__sympy-22080",
        "repo_dir_name": "sympy__sympy",
        "target_file_rel": "sympy/printing/codeprinter.py",
    },
    {
        "instance_id": "pydata__xarray-4075",
        "repo_dir_name": "pydata__xarray",
        "target_file_rel": "xarray/core/weighted.py",
    },
    {
        "instance_id": "pydata__xarray-4356",
        "repo_dir_name": "pydata__xarray",
        "target_file_rel": "xarray/core/nanops.py",
    },
    {
        "instance_id": "pydata__xarray-4966",
        "repo_dir_name": "pydata__xarray",
        "target_file_rel": "xarray/coding/variables.py",
    },
    {
        "instance_id": "pydata__xarray-6744",
        "repo_dir_name": "pydata__xarray",
        "target_file_rel": "xarray/core/rolling.py",
    },
    {
        "instance_id": "pydata__xarray-6992",
        "repo_dir_name": "pydata__xarray",
        "target_file_rel": "xarray/core/dataset.py",
    },
]

CONFTEST_REQUESTS = """# Backward compatibility shim for Python 3.11+
import collections, collections.abc
for name in ['Mapping', 'MutableMapping', 'Sequence', 'Callable', 'Iterable', 'Iterator']:
    if not hasattr(collections, name) and hasattr(collections.abc, name):
        setattr(collections, name, getattr(collections.abc, name))
"""

CONFTEST_XARRAY = """# NumPy 2.0 compatibility shim for old xarray versions
import numpy as np
if not hasattr(np, 'unicode_'):
    np.unicode_ = np.str_
if not hasattr(np, 'bool'):
    pass  # np.bool was removed in NumPy 1.24+
import collections, collections.abc
for name in ['Mapping', 'MutableMapping', 'Sequence', 'Callable', 'Iterable', 'Iterator']:
    if not hasattr(collections, name) and hasattr(collections.abc, name):
        setattr(collections, name, getattr(collections.abc, name))
"""


def get_conftest(instance_id):
    if instance_id.startswith("psf__requests"):
        return CONFTEST_REQUESTS
    elif instance_id.startswith("pydata__xarray"):
        return CONFTEST_XARRAY
    return None


def sha256_file(path):
    h = hashlib.sha256()
    h.update(path.read_bytes())
    return h.hexdigest()


def main():
    print(f"=== Batch Test Generation for Path B Expansion ===")
    print(f"Model: {MODEL}, Runs: {NUM_RUNS}, Temperature: {TEMPERATURE}")
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()

    instances = load_swebench_instances()
    inst_map = {i.instance_id: i for i in instances}

    all_meta = {}
    total_start = time.time()

    for cfg in NEW_INSTANCES:
        inst_id = cfg["instance_id"]
        inst = inst_map.get(inst_id)
        if not inst:
            print(f"[SKIP] {inst_id}: NOT FOUND in SWE-bench Verified")
            continue

        repo_dir = PROJECT_ROOT / "data" / "repos" / cfg["repo_dir_name"]
        out_dir = PROJECT_ROOT / "data" / "study_gate3" / inst_id / "generated_tests"
        out_dir.mkdir(parents=True, exist_ok=True)

        print(f"\n--- {inst_id} ---")

        # Read source from buggy worktree (base_commit, NO patch applied)
        with isolated_instance_environment(repo_dir, inst, version="buggy") as wt:
            source_file = wt / cfg["target_file_rel"]
            if not source_file.exists():
                print(f"  [ERROR] Target file not found: {cfg['target_file_rel']}")
                continue
            source_code = source_file.read_text(encoding="utf-8", errors="ignore")
            source_lines = len(source_code.splitlines())
            print(f"  Source: {cfg['target_file_rel']} ({source_lines} lines)")

            # For very large files (>1000 lines), truncate to first 800 lines
            # to stay within LLM context window
            if source_lines > 1000:
                truncated_lines = source_code.splitlines()[:800]
                source_code = "\n".join(truncated_lines)
                print(f"  [TRUNCATED] to 800/{source_lines} lines for LLM context")

        # Generate N runs
        inst_meta = []
        for run_idx in range(NUM_RUNS):
            print(f"  Run {run_idx}/{NUM_RUNS-1}...")
            try:
                result = generate_tests(
                    source_code=source_code,
                    filepath=cfg["target_file_rel"],
                    model=MODEL,
                    template="basic",
                    temperature=TEMPERATURE,
                )

                test_code = result["test_code"]
                out_file = out_dir / f"test_gen_{run_idx:02d}.py"
                out_file.write_text(test_code, encoding="utf-8")

                file_hash = sha256_file(out_file)
                print(f"    Saved: {out_file.name} ({len(test_code)} chars, SHA256={file_hash[:16]}...)")

                inst_meta.append({
                    "run_index": run_idx,
                    "file": out_file.name,
                    "sha256": file_hash,
                    "model": MODEL,
                    "template": "basic",
                    "temperature": TEMPERATURE,
                    "generation_time_seconds": result["generation_time_seconds"],
                    "test_code_length": result["test_code_length"],
                    "raw_response_length": result["raw_response_length"],
                    "timestamp": result["timestamp"],
                })
            except Exception as e:
                print(f"    [ERROR] Run {run_idx} failed: {e}")
                inst_meta.append({"run_index": run_idx, "error": str(e)})

        # Write conftest if needed
        conftest_content = get_conftest(inst_id)
        if conftest_content:
            conftest_path = out_dir / "conftest.py"
            conftest_path.write_text(conftest_content, encoding="utf-8")
            print(f"  Written conftest.py shim")

        # Save per-instance metadata
        meta_path = out_dir / "generation_meta.json"
        meta_path.write_text(json.dumps(inst_meta, indent=2, ensure_ascii=False), encoding="utf-8")
        all_meta[inst_id] = inst_meta

    total_dur = time.time() - total_start
    print(f"\n=== Batch Generation Complete ===")
    print(f"Total time: {total_dur:.1f}s")
    print(f"Instances processed: {len(all_meta)}")

    # Save aggregate metadata
    agg_path = PROJECT_ROOT / "data" / "study_gate3" / "batch_generation_meta.json"
    agg_path.write_text(json.dumps({
        "timestamp": datetime.now().isoformat(),
        "model": MODEL,
        "num_runs": NUM_RUNS,
        "temperature": TEMPERATURE,
        "total_duration_seconds": round(total_dur, 2),
        "instances": all_meta,
    }, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Aggregate metadata: {agg_path}")


if __name__ == "__main__":
    main()
