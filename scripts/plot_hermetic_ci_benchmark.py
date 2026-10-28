"""
Plot publication-quality Hermetic CI Benchmark figure for EMSE submission.
Outputs:
- paper/emse_submission/figures/fig_hermetic_ci_comparison.pdf
- paper/emse_submission/figures/fig_hermetic_ci_comparison.png
"""

import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_FILE = PROJECT_ROOT / "results" / "hermetic_ci_benchmark_results.json"
FIG_DIR = PROJECT_ROOT / "paper" / "emse_submission" / "figures"
FIG_DIR.mkdir(parents=True, exist_ok=True)

with open(DATA_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

summary = data["summary"]
instances = data["instances"]

plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4.8), dpi=300)

# ----------------------------------------------------
# Panel A: Strategy-Level Hermetic Feasibility vs Spurious Break Rate
# ----------------------------------------------------
strats = ["Keep-All", "Discard-All-Flaky", "Random-Filtering", "Static-Only", "Risk-Aware-Triage"]
strat_labels = ["Keep-All", "Discard\nAll Flaky", "Random\nFiltering", "Static\nOnly", "Risk-Aware\nTriage (Ours)"]
feas_rates = [summary[s]["hermetic_build_feasibility_rate_pct"] for s in strats]
break_rates = [summary[s]["spurious_network_break_rate_pct"] for s in strats]
viol_counts = [summary[s]["network_violations"] for s in strats]

x = np.arange(len(strats))
width = 0.45

colors = ["#dc2626", "#ea580c", "#d97706", "#2563eb", "#16a34a"]

bars = ax1.bar(x, feas_rates, width, color=colors, edgecolor="#1e293b", linewidth=1.2, alpha=0.9)

# Annotate bars
for i, bar in enumerate(bars):
    h = bar.get_height()
    viol = viol_counts[i]
    if viol > 0:
        ax1.text(bar.get_x() + bar.get_width()/2., h - 14, f"{h:.1f}%\n({viol} Socket Errs)",
                 ha="center", va="center", color="white", fontweight="bold", fontsize=9)
    else:
        ax1.text(bar.get_x() + bar.get_width()/2., h - 10, f"{h:.1f}%\n(0 Errs)",
                 ha="center", va="center", color="white", fontweight="bold", fontsize=9)

ax1.set_ylabel("Mainline Hermetic CI Feasibility (%)", fontsize=11, fontweight="bold")
ax1.set_title("(a) Mainline CI Feasibility Under Air-Gapped Network Sandbox", fontsize=11.5, fontweight="bold", pad=10)
ax1.set_xticks(x)
ax1.set_xticklabels(strat_labels, fontsize=9.5)
ax1.set_ylim(0, 115)
ax1.axhline(100.0, color="#16a34a", linestyle="--", alpha=0.5, label="100% Hermetic Resilience")
ax1.legend(loc="lower left", frameon=True, framealpha=0.9, fontsize=9)

# ----------------------------------------------------
# Panel B: Instance-Level Network Violations (Keep-All vs Triage)
# ----------------------------------------------------
req_instances = [iid for iid, info in instances.items() if "requests" in iid]
clean_names = [iid.replace("psf__", "") for iid in req_instances]

keep_viols = [instances[iid]["strategies"]["Keep-All"]["network_violations"] for iid in req_instances]
tri_viols = [instances[iid]["strategies"]["Risk-Aware-Triage"]["network_violations"] for iid in req_instances]

x_b = np.arange(len(req_instances))
w_b = 0.35

ax2.bar(x_b - w_b/2, keep_viols, w_b, label="Keep-All (Unconstrained)", color="#dc2626", edgecolor="#1e293b", linewidth=1.1, alpha=0.9)
ax2.bar(x_b + w_b/2, tri_viols, w_b, label="Risk-Aware-Triage Mainline", color="#16a34a", edgecolor="#1e293b", linewidth=1.1, alpha=0.9)

for i in range(len(req_instances)):
    if keep_viols[i] > 0:
        ax2.text(x_b[i] - w_b/2, keep_viols[i] + 0.4, str(keep_viols[i]), ha="center", va="bottom", fontweight="bold", fontsize=9.5, color="#dc2626")
    ax2.text(x_b[i] + w_b/2, tri_viols[i] + 0.4, str(tri_viols[i]), ha="center", va="bottom", fontweight="bold", fontsize=9.5, color="#16a34a")

ax2.set_ylabel("Spurious Socket Connection Failures", fontsize=11, fontweight="bold")
ax2.set_title("(b) Unmocked Socket Crashes in Networking Repositories", fontsize=11.5, fontweight="bold", pad=10)
ax2.set_xticks(x_b)
ax2.set_xticklabels(clean_names, rotation=25, ha="right", fontsize=9.5)
ax2.set_ylim(0, max(keep_viols) + 3)
ax2.legend(loc="upper right", frameon=True, framealpha=0.9, fontsize=9.5)

plt.tight_layout()
fig.savefig(FIG_DIR / "fig_hermetic_ci_comparison.pdf", dpi=300)
fig.savefig(FIG_DIR / "fig_hermetic_ci_comparison.png", dpi=300)
plt.close(fig)

print(f"[+] Successfully generated figure at: {FIG_DIR / 'fig_hermetic_ci_comparison.pdf'}")
