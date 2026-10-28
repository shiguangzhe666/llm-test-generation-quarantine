"""Debug the buggy module string replacement."""
import sys
sys.path.insert(0, '.')

# Read and exec the pilot_test module constants
with open('scripts/pilot_test.py', encoding='utf-8') as f:
    content = f.read()

# Execute only the constant definitions (up to the run_pilot function)
code_block = content.split('def run_pilot')[0]
exec(code_block)

print("=== FIXED MODULE (relevant section) ===")
for i, line in enumerate(SAMPLE_MODULE_FIXED.split('\n')):
    if 'query_string' in line or 'fragment' in line.lower() or '#' in line:
        print(f"  Line {i}: {line}")

print("\n=== BUGGY MODULE (relevant section) ===")
for i, line in enumerate(SAMPLE_MODULE_BUGGY.split('\n')):
    if 'query_string' in line or 'fragment' in line.lower() or '#' in line or 'BUG' in line:
        print(f"  Line {i}: {line}")

# Check if the bug actually works
has_fragment_strip_fixed = "query_string.split('#')[0]" in SAMPLE_MODULE_FIXED
has_fragment_strip_buggy = "query_string.split('#')[0]" in SAMPLE_MODULE_BUGGY

print(f"\nFixed has fragment strip: {has_fragment_strip_fixed}")
print(f"Buggy has fragment strip: {has_fragment_strip_buggy}")
print(f"Difference exists: {SAMPLE_MODULE_FIXED != SAMPLE_MODULE_BUGGY}")
