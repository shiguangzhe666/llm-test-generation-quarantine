"""
Script to create normalized supplementary snapshot for Phase I revalidation.
Tracks:
- README.md
- data/benchmarks/
- data/sample_project/
- literature_audit/
Excludes:
- .git, __pycache__, .pytest_cache, *.pyc, temporary files
Generates:
- snapshots/snapshot_supplement_revalidated_20260921_011520/manifest.json
- copies of all tracked files
"""

import hashlib
import json
import os
import shutil
from datetime import datetime
from pathlib import Path

SNAPSHOT_ID = "snapshot_supplement_revalidated_20260921_011520"
PROJECT_ROOT = Path(r"F:\论文\llm-test-stability")
LIT_AUDIT = Path(r"F:\论文\literature_audit")
SNAPSHOT_DIR = PROJECT_ROOT / "snapshots" / SNAPSHOT_ID
SNAPSHOT_DIR.mkdir(parents=True, exist_ok=True)

targets = [
    (PROJECT_ROOT / "README.md", "README.md", "PROJECT_ROOT"),
    (PROJECT_ROOT / "data" / "benchmarks", "data/benchmarks", "PROJECT_ROOT"),
    (PROJECT_ROOT / "data" / "sample_project", "data/sample_project", "PROJECT_ROOT"),
    (LIT_AUDIT, "literature_audit", "LIT_ROOT"),
]

exclude_names = {".git", "__pycache__", ".pytest_cache"}
exclude_exts = {".pyc", ".log", ".tmp"}

files_manifest = []

for path, rel_base, root_alias in targets:
    if path.is_file():
        file_paths = [path]
    else:
        file_paths = []
        for p in sorted(path.rglob("*")):
            if p.is_file():
                parts = set(p.parts)
                if parts & exclude_names:
                    continue
                if p.suffix in exclude_exts:
                    continue
                file_paths.append(p)

    for fp in file_paths:
        raw_bytes = fp.read_bytes()
        sha256 = hashlib.sha256(raw_bytes).hexdigest()
        size = len(raw_bytes)
        
        if path.is_file():
            canon_rel = rel_base
        else:
            canon_rel = f"{rel_base}/{fp.relative_to(path).as_posix()}"

        dest_file = SNAPSHOT_DIR / canon_rel
        dest_file.parent.mkdir(parents=True, exist_ok=True)
        dest_file.write_bytes(raw_bytes)

        files_manifest.append({
            "canonical_relative_path": canon_rel,
            "root_alias": root_alias,
            "original_absolute_path": str(fp),
            "size_bytes": size,
            "sha256": sha256,
        })

manifest = {
    "snapshot_id": SNAPSHOT_ID,
    "created_at_utc": datetime.utcnow().isoformat(),
    "root_aliases": {
        "PROJECT_ROOT": str(PROJECT_ROOT),
        "LIT_ROOT": str(LIT_AUDIT),
    },
    "exclusion_rules": {
        "directories": sorted(list(exclude_names)),
        "extensions": sorted(list(exclude_exts)),
    },
    "total_files": len(files_manifest),
    "files": files_manifest,
    "verification_command": f"python scripts/_verify_snapshot.py {SNAPSHOT_ID}",
}

manifest_path = SNAPSHOT_DIR / "manifest.json"
with open(manifest_path, "w", encoding="utf-8") as f:
    json.dump(manifest, f, indent=2, ensure_ascii=False)

print(f"Snapshot {SNAPSHOT_ID} created successfully with {len(files_manifest)} files.")
for f in files_manifest:
    print(f"  {f['canonical_relative_path']:45s} {f['size_bytes']:6d}B  SHA256: {f['sha256']}")
