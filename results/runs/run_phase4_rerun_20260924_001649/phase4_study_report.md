# Phase IV Formal Study Rerun Report (run_phase4_rerun_20260924_001649)

**Date (UTC)**: 2026-09-23 17:06:42  
**Settings**: N=20 repetitions, Max Mutants=3  
**Valid Instances**: 13 / 17 evaluated  

## Overall Strategy Comparison (Mean ± Clustered SE)

| Strategy | Exec. Ret. (%) | Quarantine (%) | CI Determ. (%) | Bug Ret. (%) | Defect Tests Ret. (%) | Mut. Score (%) | Mainline DT Ret. (%) | Quar. DT Ret. (%) |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Keep-All** | 100.0 ± 0.0 | 0.0 ± 0.0 | 99.7 ± 0.3 | 100.0 ± 0.0 | 100.0 ± 0.0 | 7.7 ± 3.2 | 100.0 ± 0.0 | 0.0 ± 0.0 |
| **Discard-All-Flaky** | 99.7 ± 0.3 | 0.0 ± 0.0 | 100.0 ± 0.0 | 100.0 ± 0.0 | 100.0 ± 0.0 | 7.7 ± 3.2 | 100.0 ± 0.0 | 0.0 ± 0.0 |
| **Random-Filtering** | 77.9 ± 17.9 | 0.0 ± 0.0 | 100.0 ± 0.0 | 100.0 ± 0.0 | 100.0 ± 0.0 | 7.7 ± 3.2 | 100.0 ± 0.0 | 0.0 ± 0.0 |
| **Static-Only** | 77.9 ± 17.9 | 0.0 ± 0.0 | 100.0 ± 0.0 | 100.0 ± 0.0 | 100.0 ± 0.0 | 7.7 ± 3.2 | 100.0 ± 0.0 | 0.0 ± 0.0 |
| **Risk-Aware-Triage** | 77.9 ± 17.9 | 19.2 ± 15.5 | 100.0 ± 0.0 | 100.0 ± 0.0 | 100.0 ± 0.0 | 7.7 ± 3.2 | 100.0 ± 0.0 | 0.0 ± 0.0 |

## Hypothesis Testing (Triage vs Baselines)

| Comparison | Wilcoxon W | p-value | Vargha-Delaney A12 | Magnitude |
|:---|:---:|:---:|:---:|:---:|
| Triage_vs_Discard-All-Flaky_Defect_Retention | 0.0 | 1.0000 | 0.5000 | negligible |
| Triage_vs_Random-Filtering_Defect_Retention | 0.0 | 1.0000 | 0.5000 | negligible |
| Triage_vs_Static-Only_Defect_Retention | 0.0 | 1.0000 | 0.5000 | negligible |
| Triage_vs_Keep-All_Defect_Retention | 0.0 | 1.0000 | 0.5000 | negligible |
| Triage_vs_Discard-All-Flaky_Quarantine_Rate | 0 | 0.0591 | 0.6923 | medium |
| Triage_vs_Static-Only_Executable_Retention | 0.0 | 1.0000 | 0.5000 | negligible |