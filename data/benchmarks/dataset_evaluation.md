# Dataset Evaluation for Feasibility Study

## Decision: SWE-bench Verified as Primary Benchmark

### Rationale
| Criterion | BugsInPy | SWE-bench Verified |
|-----------|----------|-------------------|
| Reproducibility | <50% functional | **100% (pre-built Docker)** |
| Maintenance | Dormant since 2021 | **Active (OpenAI/Princeton)** |
| Project Diversity | 17 repos (but 8 broken) | **12 repos across 5 domains** |
| Test Flakiness in Base | High | **Vetted by human auditors** |
| Docker Support | Partial/broken | **Pre-built images on Docker Hub** |

### Selected Pilot Projects (from SWE-bench Verified)

1. **requests** (psf/requests) — HTTP library, networking
2. **flask** (pallets/flask) — Web framework
3. **pytest** (pytest-dev/pytest) — Testing tool, meta-relevant
4. **sympy** (sympy/sympy) — Symbolic math, pure Python
5. **xarray** (pydata/xarray) — Data processing

### Backup: BugsInPy Stable Subset (for quick local testing)
- cookiecutter (4 bugs)
- httpie (5 bugs)  
- thefuck (32 bugs)
- fastapi (16 bugs)
- sanic (5 bugs)
- Total: ~62 bugs, pure Python, pytest-based

### Workflow for Each Bug Instance
1. Extract buggy code at `base_commit`
2. Generate LLM tests for target component
3. Run tests N times for flakiness detection (RQ1)
4. Run tests on buggy vs fixed versions for bug detection (RQ2)
5. Apply triage framework and re-evaluate (RQ3)

### Access
- Dataset: `princeton-nlp/SWE-bench_Verified` on Hugging Face
- Docker images: `swebench/sweb.eval.x86_64.<instance_id>`
- Install: `pip install swebench`
