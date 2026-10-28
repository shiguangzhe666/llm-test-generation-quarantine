"""Analyze SWE-bench Verified and select pilot instances."""
import os, json, sys
os.environ['NO_PROXY'] = '*'
os.environ['no_proxy'] = '*'
from collections import Counter
from datasets import load_dataset

ds = load_dataset('princeton-nlp/SWE-bench_Verified', split='test')
print("Total: {} instances".format(len(ds)))

repo_counts = Counter()
repo_instances = {}
for item in ds:
    repo = item['repo']
    repo_counts[repo] += 1
    if repo not in repo_instances:
        repo_instances[repo] = []
    
    f2p = json.loads(item['FAIL_TO_PASS']) if isinstance(item['FAIL_TO_PASS'], str) else item['FAIL_TO_PASS']
    p2p = json.loads(item['PASS_TO_PASS']) if isinstance(item['PASS_TO_PASS'], str) else item['PASS_TO_PASS']
    patch_lines = len(item.get('patch', '').split('\n'))
    
    repo_instances[repo].append({
        'instance_id': item['instance_id'],
        'base_commit': item.get('base_commit', '')[:12],
        'patch_lines': patch_lines,
        'f2p': len(f2p),
        'p2p': len(p2p),
        'difficulty': item.get('difficulty', ''),
        'version': item.get('version', ''),
    })

print("\n=== Instances per Repository ===")
for repo, count in repo_counts.most_common():
    print("  {:40s} {:4d}".format(repo, count))

# Select pilot instances
targets = ['psf/requests', 'pallets/flask', 'pytest-dev/pytest', 'sympy/sympy', 'pydata/xarray']
print("\n=== Pilot Selection ===")
pilot = {}
for repo in targets:
    if repo not in repo_instances:
        print("  {}: NOT FOUND".format(repo))
        continue
    insts = repo_instances[repo]
    scored = []
    for inst in insts:
        score = 0
        if 5 <= inst['patch_lines'] <= 50:
            score += 3
        elif inst['patch_lines'] < 100:
            score += 1
        score += min(inst['f2p'], 5)
        scored.append((score, inst))
    scored.sort(key=lambda x: x[0], reverse=True)
    selected = [s[1] for s in scored[:5]]
    pilot[repo] = selected
    print("\n  {} ({} total, selected {}):".format(repo, len(insts), len(selected)))
    for s in selected:
        iid = s['instance_id']
        pl = s['patch_lines']
        f = s['f2p']
        p = s['p2p']
        d = s['difficulty']
        print("    {}  patch:{}L  f2p:{}  p2p:{}  diff:{}".format(iid, pl, f, p, d))

# Save
output = {'repos': {}}
total_sel = 0
for repo, insts in pilot.items():
    output['repos'][repo] = {'count': len(insts), 'instances': insts}
    total_sel += len(insts)
output['total_selected'] = total_sel

with open('data/benchmarks/pilot_selection.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)
print("\nSaved {} instances to data/benchmarks/pilot_selection.json".format(total_sel))
