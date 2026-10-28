"""
Script to independently verify a snapshot manifest against the snapshot directory
and against current live files.
"""

import hashlib
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(r"F:\论文\llm-test-stability")


def verify_snapshot(snapshot_id: str):
    snapshot_dir = PROJECT_ROOT / "snapshots" / snapshot_id
    manifest_path = snapshot_dir / "manifest.json"
    if not manifest_path.exists():
        print(f"ERROR: Manifest not found: {manifest_path}")
        return False

    with open(manifest_path, "r", encoding="utf-8") as f:
        manifest = json.load(f)

    print(f"Verifying snapshot: {snapshot_id}")
    print(f"Total files in manifest: {manifest.get('total_files', len(manifest.get('files', [])))}")

    all_matched = True
    for item in manifest.get("files", []):
        rel_path = item.get("canonical_relative_path") or item.get("relative_path")
        expected_sha = item.get("sha256")
        expected_size = item.get("size_bytes")
        
        # 1. Verify snapshot copy
        snap_copy = snapshot_dir / rel_path
        if not snap_copy.exists():
            print(f"  [MISSING IN SNAPSHOT] {rel_path}")
            all_matched = False
            continue
        snap_bytes = snap_copy.read_bytes()
        snap_sha = hashlib.sha256(snap_bytes).hexdigest()
        if snap_sha != expected_sha:
            print(f"  [HASH MISMATCH SNAPSHOT] {rel_path}: expected {expected_sha[:12]}, got {snap_sha[:12]}")
            all_matched = False
            continue

        # 2. Check original live file
        orig_path = Path(item.get("original_absolute_path", ""))
        live_status = "NOT_CHECKED"
        if orig_path.exists():
            orig_bytes = orig_path.read_bytes()
            orig_sha = hashlib.sha256(orig_bytes).hexdigest()
            if orig_sha == expected_sha:
                live_status = "MATCHED_LIVE"
            else:
                live_status = f"LIVE_MODIFIED (live_sha: {orig_sha[:12]})"
        else:
            live_status = "ORIGINAL_MOVED_OR_DELETED"

        print(f"  [OK] {rel_path:45s} size={len(snap_bytes)}B snap_sha={snap_sha[:12]} live={live_status}")

    print(f"\nSnapshot verification completed: All snapshot copies matched manifest: {all_matched}")
    return all_matched


if __name__ == "__main__":
    sid = sys.argv[1] if len(sys.argv) > 1 else "snapshot_supplement_revalidated_20260921_011520"
    ok = verify_snapshot(sid)
    sys.exit(0 if ok else 1)
