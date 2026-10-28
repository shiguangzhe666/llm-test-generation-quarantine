"""Fix the pytest instance extraction — apply patch manually."""
from pathlib import Path

src = Path(r"F:\论文\llm-test-stability\data\repos\pytest-dev__pytest\src\_pytest\capture.py")
content = src.read_text(encoding="utf-8")
buggy_content = content

# The patch adds: newline="", after errors="replace",
old_str = 'errors="replace",\n                write_through=True,'
new_str = 'errors="replace",\n                newline="",\n                write_through=True,'
fixed_content = content.replace(old_str, new_str)
print(f"Changed: {fixed_content != buggy_content}")

output_dir = Path(r"F:\论文\llm-test-stability\data\pilot_gate2\pytest-dev__pytest-7521")

# Save buggy
buggy_dir = output_dir / "buggy" / "src" / "_pytest"
buggy_dir.mkdir(parents=True, exist_ok=True)
(buggy_dir / "capture.py").write_text(buggy_content, encoding="utf-8")

# Save fixed
fixed_dir = output_dir / "fixed" / "src" / "_pytest"
fixed_dir.mkdir(parents=True, exist_ok=True)
(fixed_dir / "capture.py").write_text(fixed_content, encoding="utf-8")

print("Both versions saved")
print(f"Buggy size: {len(buggy_content)}")
print(f"Fixed size: {len(fixed_content)}")
