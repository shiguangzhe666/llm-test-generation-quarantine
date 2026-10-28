# Replication Package — Risk-Aware-Triage / JSS submission

Manuscript: "Quarantining Environmentally Fragile LLM-Generated Tests:
A Project-Level Empirical Study on SWE-bench Verified"

## Contents
- `src/`            AST feature extraction, shuffle profiling, triage, socket guard
- `scripts/`        experiment drivers, cross-model benchmarks, plotting, audits
- `prompts/`        zero-leakage test-generation prompt templates
- `configs/`        experiment configuration
- `tests/`          unit and integration tests
- `results/`        formal run archive, including
                    `runs/run_phase4_rerun_20260926_090500/`
- `data/`           benchmark fixtures, generated tests, cross-model outputs
- `REPLICATION.md`  step-by-step reproduction instructions

## Formal run archive
`results/runs/run_phase4_rerun_20260926_090500/` contains the authoritative
formal run. Its `manifest.json` records SHA-256 digests for **363 files**
(`files_count = 363`). The directory as shipped contains **366 files**: the
363 hashed files plus `manifest.json` itself and `evidence_audit.json` /
`evidence_audit.md`, which were generated after hashing. This is expected.

Note: manifest paths are recorded with Windows-style backslashes because the
run was executed on Windows. On POSIX systems, normalise separators before
comparing digests.

## Base repositories (not bundled)
The cloned upstream repositories under `data/repos/` are excluded to keep the
package small; they are public and can be re-cloned at the exact commits:

- `psf__requests`: 091991be0da19de9108dbe5e3752917fea3d7fdc
- `pallets__flask`: 7ee9ceb71e868944a46e1ff00b506772a53a4f1d
- `pytest-dev__pytest`: 41d211c24a6781843b174379d6d6538f5c17adb9
- `sympy__sympy`: 1d3327b8e90a186df6972991963a5ae87053259d
- `pydata__xarray`: 8de862c29544c2fb1957ce20985745952bc81de7

## Environment
Python 3.11, pytest, and a local Ollama deployment of `qwen3:8b`
(temperature 0.7, num_predict 4096). Exact Ollama build and model digest are
recorded in the manuscript's method section / author records.

## License
Released under the MIT License (see `LICENSE`).
