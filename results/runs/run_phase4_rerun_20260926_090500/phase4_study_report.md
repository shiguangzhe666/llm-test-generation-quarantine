# Phase IV Formal Study Rerun Report (run_phase4_rerun_20260926_090500)

**Date (UTC)**: 2026-09-26 01:44:10  
**Settings**: N=20 repetitions, Max Mutants=3  
**Valid Instances**: 13 / 17 evaluated  

## Overall Strategy Comparison (Mean ± Clustered SE)

| Strategy | Exec. Ret. (%) | Quarantine (%) | CI Determ. (%) | Bug Ret. (%) | Defect Tests Ret. (%) | Mut. Score (%) | Mainline DT Ret. (%) | Quar. DT Ret. (%) |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **Keep-All** | 100.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 | 100.0 ± 0.0 | 100.0 ± 0.0 | 7.7 ± 3.2 | 100.0 ± 0.0 | 0.0 ± 0.0 |
| **Discard-All-Flaky** | 100.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 | 100.0 ± 0.0 | 100.0 ± 0.0 | 7.7 ± 3.2 | 100.0 ± 0.0 | 0.0 ± 0.0 |
| **Random-Filtering** | 77.5 ± 18.2 | 0.0 ± 0.0 | 100.0 ± 0.0 | 100.0 ± 0.0 | 100.0 ± 0.0 | 7.7 ± 3.2 | 100.0 ± 0.0 | 0.0 ± 0.0 |
| **Static-Only** | 77.5 ± 18.2 | 0.0 ± 0.0 | 100.0 ± 0.0 | 100.0 ± 0.0 | 100.0 ± 0.0 | 7.7 ± 3.2 | 100.0 ± 0.0 | 0.0 ± 0.0 |
| **Risk-Aware-Triage** | 77.5 ± 18.2 | 19.5 ± 15.8 | 100.0 ± 0.0 | 100.0 ± 0.0 | 100.0 ± 0.0 | 7.7 ± 3.2 | 100.0 ± 0.0 | 0.0 ± 0.0 |

## Hypothesis Testing (Triage vs Baselines)

| Comparison | n_pairs | Non-zero | Wilcoxon W | p-value (raw) | p-value (Holm) | Paired A12 | Magnitude |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| Triage_vs_Discard-All-Flaky_Defect_Retention | 3 | 0 | 0.0 | 1.0000 | 1.0000 | 0.5000 | negligible |
| Triage_vs_Random-Filtering_Defect_Retention | 3 | 0 | 0.0 | 1.0000 | 1.0000 | 0.5000 | negligible |
| Triage_vs_Static-Only_Defect_Retention | 3 | 0 | 0.0 | 1.0000 | 1.0000 | 0.5000 | negligible |
| Triage_vs_Keep-All_Defect_Retention | 3 | 0 | 0.0 | 1.0000 | 1.0000 | 0.5000 | negligible |
| Triage_vs_Discard-All-Flaky_Quarantine_Rate | 13 | 5 | 0 | 0.0591 | 0.3543 | 0.6923 | medium |
| Triage_vs_Static-Only_Executable_Retention | 13 | 0 | 0.0 | 1.0000 | 1.0000 | 0.5000 | negligible |