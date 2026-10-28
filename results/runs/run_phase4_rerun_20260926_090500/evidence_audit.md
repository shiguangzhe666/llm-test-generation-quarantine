# Evidence Audit: `run_phase4_rerun_20260926_090500`

This audit is conservative: unavailable fields are explicitly marked `UNAVAILABLE` or `NOT AUDITABLE`; no nodeid fallback is inferred.

## Run Semantics

- Valid instances: **13**
- Excluded instances: **4**
- Dynamic profiling repetitions: **N=20**
- N=20 applies to fixed-version dynamic shuffle profiling, not to physical strategy-pool repetition.
- Strategy-pool records: **135**

## Audit Checks

- `generated_count_equals_collected_count`: **PASS**
- `planned_observed_traceability_status_explicit`: **PASS**
- `defect_denominator_reproducible_from_final_run`: **PASS**
- `strategy_results_not_replaced_by_profiling_records`: **PASS**
- `final_tables_rebuild_source_declared`: **PASS**

## Defect Denominator

- Defect instances: **3**
- Defect-detecting tests: **14**
- Scope: current benchmark subset only; ceiling effect applies.

## Strategy-Pool Records

| Instance | Strategy | Pool | Codebase | Observed | Exit | Log |
|---|---|---|---|---:|---:|---|
| psf__requests-1921 | Discard-All-Flaky | main | buggy | 30 | 1 | logs\psf__requests-1921_06_Discard-All-Flaky_main_buggy.log |
| psf__requests-1921 | Discard-All-Flaky | main | fixed | 30 | 1 | logs\psf__requests-1921_06_Discard-All-Flaky_main_fixed.log |
| psf__requests-1921 | Keep-All | main | buggy | 30 | 1 | logs\psf__requests-1921_06_Keep-All_main_buggy.log |
| psf__requests-1921 | Keep-All | main | fixed | 30 | 1 | logs\psf__requests-1921_06_Keep-All_main_fixed.log |
| psf__requests-1921 | Random-Filtering | main | buggy | 27 | 1 | logs\psf__requests-1921_06_Random-Filtering_main_buggy.log |
| psf__requests-1921 | Random-Filtering | main | fixed | 27 | 1 | logs\psf__requests-1921_06_Random-Filtering_main_fixed.log |
| psf__requests-1921 | Risk-Aware-Triage | main | buggy | 27 | 1 | logs\psf__requests-1921_06_Risk-Aware-Triage_main_buggy.log |
| psf__requests-1921 | Risk-Aware-Triage | main | fixed | 27 | 1 | logs\psf__requests-1921_06_Risk-Aware-Triage_main_fixed.log |
| psf__requests-1921 | Risk-Aware-Triage | quar | buggy | 3 | 1 | logs\psf__requests-1921_06_Risk-Aware-Triage_quar_buggy.log |
| psf__requests-1921 | Static-Only | main | buggy | 27 | 1 | logs\psf__requests-1921_06_Static-Only_main_buggy.log |
| psf__requests-1921 | Static-Only | main | fixed | 27 | 1 | logs\psf__requests-1921_06_Static-Only_main_fixed.log |
| psf__requests-1724 | Discard-All-Flaky | main | buggy | 15 | 1 | logs\psf__requests-1724_06_Discard-All-Flaky_main_buggy.log |
| psf__requests-1724 | Discard-All-Flaky | main | fixed | 15 | 1 | logs\psf__requests-1724_06_Discard-All-Flaky_main_fixed.log |
| psf__requests-1724 | Keep-All | main | buggy | 15 | 1 | logs\psf__requests-1724_06_Keep-All_main_buggy.log |
| psf__requests-1724 | Keep-All | main | fixed | 15 | 1 | logs\psf__requests-1724_06_Keep-All_main_fixed.log |
| psf__requests-1724 | Random-Filtering | main | buggy | 2 | 1 | logs\psf__requests-1724_06_Random-Filtering_main_buggy.log |
| psf__requests-1724 | Random-Filtering | main | fixed | 2 | 1 | logs\psf__requests-1724_06_Random-Filtering_main_fixed.log |
| psf__requests-1724 | Risk-Aware-Triage | main | buggy | 2 | 1 | logs\psf__requests-1724_06_Risk-Aware-Triage_main_buggy.log |
| psf__requests-1724 | Risk-Aware-Triage | main | fixed | 2 | 1 | logs\psf__requests-1724_06_Risk-Aware-Triage_main_fixed.log |
| psf__requests-1724 | Risk-Aware-Triage | quar | buggy | 13 | 1 | logs\psf__requests-1724_06_Risk-Aware-Triage_quar_buggy.log |
| psf__requests-1724 | Static-Only | main | buggy | 2 | 1 | logs\psf__requests-1724_06_Static-Only_main_buggy.log |
| psf__requests-1724 | Static-Only | main | fixed | 2 | 1 | logs\psf__requests-1724_06_Static-Only_main_fixed.log |
| psf__requests-2317 | Discard-All-Flaky | main | buggy | 23 | 1 | logs\psf__requests-2317_06_Discard-All-Flaky_main_buggy.log |
| psf__requests-2317 | Discard-All-Flaky | main | fixed | 23 | 1 | logs\psf__requests-2317_06_Discard-All-Flaky_main_fixed.log |
| psf__requests-2317 | Keep-All | main | buggy | 23 | 1 | logs\psf__requests-2317_06_Keep-All_main_buggy.log |
| psf__requests-2317 | Keep-All | main | fixed | 23 | 1 | logs\psf__requests-2317_06_Keep-All_main_fixed.log |
| psf__requests-2317 | Random-Filtering | main | buggy | 1 | 0 | logs\psf__requests-2317_06_Random-Filtering_main_buggy.log |
| psf__requests-2317 | Random-Filtering | main | fixed | 1 | 0 | logs\psf__requests-2317_06_Random-Filtering_main_fixed.log |
| psf__requests-2317 | Risk-Aware-Triage | main | buggy | 1 | 1 | logs\psf__requests-2317_06_Risk-Aware-Triage_main_buggy.log |
| psf__requests-2317 | Risk-Aware-Triage | main | fixed | 1 | 1 | logs\psf__requests-2317_06_Risk-Aware-Triage_main_fixed.log |
| psf__requests-2317 | Risk-Aware-Triage | quar | buggy | 22 | 1 | logs\psf__requests-2317_06_Risk-Aware-Triage_quar_buggy.log |
| psf__requests-2317 | Static-Only | main | buggy | 1 | 1 | logs\psf__requests-2317_06_Static-Only_main_buggy.log |
| psf__requests-2317 | Static-Only | main | fixed | 1 | 1 | logs\psf__requests-2317_06_Static-Only_main_fixed.log |
| psf__requests-1766 | Discard-All-Flaky | main | buggy | 45 | 1 | logs\psf__requests-1766_06_Discard-All-Flaky_main_buggy.log |
| psf__requests-1766 | Discard-All-Flaky | main | fixed | 45 | 1 | logs\psf__requests-1766_06_Discard-All-Flaky_main_fixed.log |
| psf__requests-1766 | Keep-All | main | buggy | 45 | 1 | logs\psf__requests-1766_06_Keep-All_main_buggy.log |
| psf__requests-1766 | Keep-All | main | fixed | 45 | 1 | logs\psf__requests-1766_06_Keep-All_main_fixed.log |
| psf__requests-1766 | Random-Filtering | main | buggy | 14 | 1 | logs\psf__requests-1766_06_Random-Filtering_main_buggy.log |
| psf__requests-1766 | Random-Filtering | main | fixed | 14 | 1 | logs\psf__requests-1766_06_Random-Filtering_main_fixed.log |
| psf__requests-1766 | Risk-Aware-Triage | main | buggy | 14 | 1 | logs\psf__requests-1766_06_Risk-Aware-Triage_main_buggy.log |
| psf__requests-1766 | Risk-Aware-Triage | main | fixed | 14 | 1 | logs\psf__requests-1766_06_Risk-Aware-Triage_main_fixed.log |
| psf__requests-1766 | Risk-Aware-Triage | quar | buggy | 19 | 1 | logs\psf__requests-1766_06_Risk-Aware-Triage_quar_buggy.log |
| psf__requests-1766 | Static-Only | main | buggy | 14 | 1 | logs\psf__requests-1766_06_Static-Only_main_buggy.log |
| psf__requests-1766 | Static-Only | main | fixed | 14 | 1 | logs\psf__requests-1766_06_Static-Only_main_fixed.log |
| psf__requests-6028 | Discard-All-Flaky | main | buggy | 26 | 1 | logs\psf__requests-6028_06_Discard-All-Flaky_main_buggy.log |
| psf__requests-6028 | Discard-All-Flaky | main | fixed | 26 | 1 | logs\psf__requests-6028_06_Discard-All-Flaky_main_fixed.log |
| psf__requests-6028 | Keep-All | main | buggy | 26 | 1 | logs\psf__requests-6028_06_Keep-All_main_buggy.log |
| psf__requests-6028 | Keep-All | main | fixed | 26 | 1 | logs\psf__requests-6028_06_Keep-All_main_fixed.log |
| psf__requests-6028 | Random-Filtering | main | buggy | 18 | 1 | logs\psf__requests-6028_06_Random-Filtering_main_buggy.log |
| psf__requests-6028 | Random-Filtering | main | fixed | 18 | 1 | logs\psf__requests-6028_06_Random-Filtering_main_fixed.log |
| psf__requests-6028 | Risk-Aware-Triage | main | buggy | 18 | 1 | logs\psf__requests-6028_06_Risk-Aware-Triage_main_buggy.log |
| psf__requests-6028 | Risk-Aware-Triage | main | fixed | 18 | 1 | logs\psf__requests-6028_06_Risk-Aware-Triage_main_fixed.log |
| psf__requests-6028 | Risk-Aware-Triage | quar | buggy | 5 | 1 | logs\psf__requests-6028_06_Risk-Aware-Triage_quar_buggy.log |
| psf__requests-6028 | Static-Only | main | buggy | 18 | 1 | logs\psf__requests-6028_06_Static-Only_main_buggy.log |
| psf__requests-6028 | Static-Only | main | fixed | 18 | 1 | logs\psf__requests-6028_06_Static-Only_main_fixed.log |
| pallets__flask-5014 | Discard-All-Flaky | main | buggy | 37 | 1 | logs\pallets__flask-5014_06_Discard-All-Flaky_main_buggy.log |
| pallets__flask-5014 | Discard-All-Flaky | main | fixed | 37 | 1 | logs\pallets__flask-5014_06_Discard-All-Flaky_main_fixed.log |
| pallets__flask-5014 | Keep-All | main | buggy | 37 | 1 | logs\pallets__flask-5014_06_Keep-All_main_buggy.log |
| pallets__flask-5014 | Keep-All | main | fixed | 37 | 1 | logs\pallets__flask-5014_06_Keep-All_main_fixed.log |
| pallets__flask-5014 | Random-Filtering | main | buggy | 37 | 1 | logs\pallets__flask-5014_06_Random-Filtering_main_buggy.log |
| pallets__flask-5014 | Random-Filtering | main | fixed | 37 | 1 | logs\pallets__flask-5014_06_Random-Filtering_main_fixed.log |
| pallets__flask-5014 | Risk-Aware-Triage | main | buggy | 37 | 1 | logs\pallets__flask-5014_06_Risk-Aware-Triage_main_buggy.log |
| pallets__flask-5014 | Risk-Aware-Triage | main | fixed | 37 | 1 | logs\pallets__flask-5014_06_Risk-Aware-Triage_main_fixed.log |
| pallets__flask-5014 | Static-Only | main | buggy | 37 | 1 | logs\pallets__flask-5014_06_Static-Only_main_buggy.log |
| pallets__flask-5014 | Static-Only | main | fixed | 37 | 1 | logs\pallets__flask-5014_06_Static-Only_main_fixed.log |
| sympy__sympy-15809 | Discard-All-Flaky | main | buggy | 32 | 1 | logs\sympy__sympy-15809_06_Discard-All-Flaky_main_buggy.log |
| sympy__sympy-15809 | Discard-All-Flaky | main | fixed | 32 | 1 | logs\sympy__sympy-15809_06_Discard-All-Flaky_main_fixed.log |
| sympy__sympy-15809 | Keep-All | main | buggy | 32 | 1 | logs\sympy__sympy-15809_06_Keep-All_main_buggy.log |
| sympy__sympy-15809 | Keep-All | main | fixed | 32 | 1 | logs\sympy__sympy-15809_06_Keep-All_main_fixed.log |
| sympy__sympy-15809 | Random-Filtering | main | buggy | 32 | 1 | logs\sympy__sympy-15809_06_Random-Filtering_main_buggy.log |
| sympy__sympy-15809 | Random-Filtering | main | fixed | 32 | 1 | logs\sympy__sympy-15809_06_Random-Filtering_main_fixed.log |
| sympy__sympy-15809 | Risk-Aware-Triage | main | buggy | 32 | 1 | logs\sympy__sympy-15809_06_Risk-Aware-Triage_main_buggy.log |
| sympy__sympy-15809 | Risk-Aware-Triage | main | fixed | 32 | 1 | logs\sympy__sympy-15809_06_Risk-Aware-Triage_main_fixed.log |
| sympy__sympy-15809 | Static-Only | main | buggy | 32 | 1 | logs\sympy__sympy-15809_06_Static-Only_main_buggy.log |
| sympy__sympy-15809 | Static-Only | main | fixed | 32 | 1 | logs\sympy__sympy-15809_06_Static-Only_main_fixed.log |
| sympy__sympy-17630 | Discard-All-Flaky | main | buggy | 9 | 1 | logs\sympy__sympy-17630_06_Discard-All-Flaky_main_buggy.log |
| sympy__sympy-17630 | Discard-All-Flaky | main | fixed | 9 | 1 | logs\sympy__sympy-17630_06_Discard-All-Flaky_main_fixed.log |
| sympy__sympy-17630 | Keep-All | main | buggy | 9 | 1 | logs\sympy__sympy-17630_06_Keep-All_main_buggy.log |
| sympy__sympy-17630 | Keep-All | main | fixed | 9 | 1 | logs\sympy__sympy-17630_06_Keep-All_main_fixed.log |
| sympy__sympy-17630 | Random-Filtering | main | buggy | 9 | 1 | logs\sympy__sympy-17630_06_Random-Filtering_main_buggy.log |
| sympy__sympy-17630 | Random-Filtering | main | fixed | 9 | 1 | logs\sympy__sympy-17630_06_Random-Filtering_main_fixed.log |
| sympy__sympy-17630 | Risk-Aware-Triage | main | buggy | 9 | 1 | logs\sympy__sympy-17630_06_Risk-Aware-Triage_main_buggy.log |
| sympy__sympy-17630 | Risk-Aware-Triage | main | fixed | 9 | 1 | logs\sympy__sympy-17630_06_Risk-Aware-Triage_main_fixed.log |
| sympy__sympy-17630 | Static-Only | main | buggy | 9 | 1 | logs\sympy__sympy-17630_06_Static-Only_main_buggy.log |
| sympy__sympy-17630 | Static-Only | main | fixed | 9 | 1 | logs\sympy__sympy-17630_06_Static-Only_main_fixed.log |
| sympy__sympy-21930 | Discard-All-Flaky | main | buggy | 30 | 1 | logs\sympy__sympy-21930_06_Discard-All-Flaky_main_buggy.log |
| sympy__sympy-21930 | Discard-All-Flaky | main | fixed | 30 | 1 | logs\sympy__sympy-21930_06_Discard-All-Flaky_main_fixed.log |
| sympy__sympy-21930 | Keep-All | main | buggy | 30 | 1 | logs\sympy__sympy-21930_06_Keep-All_main_buggy.log |
| sympy__sympy-21930 | Keep-All | main | fixed | 30 | 1 | logs\sympy__sympy-21930_06_Keep-All_main_fixed.log |
| sympy__sympy-21930 | Random-Filtering | main | buggy | 30 | 1 | logs\sympy__sympy-21930_06_Random-Filtering_main_buggy.log |
| sympy__sympy-21930 | Random-Filtering | main | fixed | 30 | 1 | logs\sympy__sympy-21930_06_Random-Filtering_main_fixed.log |
| sympy__sympy-21930 | Risk-Aware-Triage | main | buggy | 30 | 1 | logs\sympy__sympy-21930_06_Risk-Aware-Triage_main_buggy.log |
| sympy__sympy-21930 | Risk-Aware-Triage | main | fixed | 30 | 1 | logs\sympy__sympy-21930_06_Risk-Aware-Triage_main_fixed.log |
| sympy__sympy-21930 | Static-Only | main | buggy | 30 | 1 | logs\sympy__sympy-21930_06_Static-Only_main_buggy.log |
| sympy__sympy-21930 | Static-Only | main | fixed | 30 | 1 | logs\sympy__sympy-21930_06_Static-Only_main_fixed.log |
| pydata__xarray-4075 | Discard-All-Flaky | main | buggy | 22 | 1 | logs\pydata__xarray-4075_06_Discard-All-Flaky_main_buggy.log |
| pydata__xarray-4075 | Discard-All-Flaky | main | fixed | 22 | 1 | logs\pydata__xarray-4075_06_Discard-All-Flaky_main_fixed.log |
| pydata__xarray-4075 | Keep-All | main | buggy | 22 | 1 | logs\pydata__xarray-4075_06_Keep-All_main_buggy.log |
| pydata__xarray-4075 | Keep-All | main | fixed | 22 | 1 | logs\pydata__xarray-4075_06_Keep-All_main_fixed.log |
| pydata__xarray-4075 | Random-Filtering | main | buggy | 22 | 1 | logs\pydata__xarray-4075_06_Random-Filtering_main_buggy.log |
| pydata__xarray-4075 | Random-Filtering | main | fixed | 22 | 1 | logs\pydata__xarray-4075_06_Random-Filtering_main_fixed.log |
| pydata__xarray-4075 | Risk-Aware-Triage | main | buggy | 22 | 1 | logs\pydata__xarray-4075_06_Risk-Aware-Triage_main_buggy.log |
| pydata__xarray-4075 | Risk-Aware-Triage | main | fixed | 22 | 1 | logs\pydata__xarray-4075_06_Risk-Aware-Triage_main_fixed.log |
| pydata__xarray-4075 | Static-Only | main | buggy | 22 | 1 | logs\pydata__xarray-4075_06_Static-Only_main_buggy.log |
| pydata__xarray-4075 | Static-Only | main | fixed | 22 | 1 | logs\pydata__xarray-4075_06_Static-Only_main_fixed.log |
| pydata__xarray-4356 | Discard-All-Flaky | main | buggy | 25 | 1 | logs\pydata__xarray-4356_06_Discard-All-Flaky_main_buggy.log |
| pydata__xarray-4356 | Discard-All-Flaky | main | fixed | 25 | 1 | logs\pydata__xarray-4356_06_Discard-All-Flaky_main_fixed.log |
| pydata__xarray-4356 | Keep-All | main | buggy | 25 | 1 | logs\pydata__xarray-4356_06_Keep-All_main_buggy.log |
| pydata__xarray-4356 | Keep-All | main | fixed | 25 | 1 | logs\pydata__xarray-4356_06_Keep-All_main_fixed.log |
| pydata__xarray-4356 | Random-Filtering | main | buggy | 25 | 1 | logs\pydata__xarray-4356_06_Random-Filtering_main_buggy.log |
| pydata__xarray-4356 | Random-Filtering | main | fixed | 25 | 1 | logs\pydata__xarray-4356_06_Random-Filtering_main_fixed.log |
| pydata__xarray-4356 | Risk-Aware-Triage | main | buggy | 25 | 1 | logs\pydata__xarray-4356_06_Risk-Aware-Triage_main_buggy.log |
| pydata__xarray-4356 | Risk-Aware-Triage | main | fixed | 25 | 1 | logs\pydata__xarray-4356_06_Risk-Aware-Triage_main_fixed.log |
| pydata__xarray-4356 | Static-Only | main | buggy | 25 | 1 | logs\pydata__xarray-4356_06_Static-Only_main_buggy.log |
| pydata__xarray-4356 | Static-Only | main | fixed | 25 | 1 | logs\pydata__xarray-4356_06_Static-Only_main_fixed.log |
| pydata__xarray-4966 | Discard-All-Flaky | main | buggy | 1 | 0 | logs\pydata__xarray-4966_06_Discard-All-Flaky_main_buggy.log |
| pydata__xarray-4966 | Discard-All-Flaky | main | fixed | 1 | 0 | logs\pydata__xarray-4966_06_Discard-All-Flaky_main_fixed.log |
| pydata__xarray-4966 | Keep-All | main | buggy | 1 | 0 | logs\pydata__xarray-4966_06_Keep-All_main_buggy.log |
| pydata__xarray-4966 | Keep-All | main | fixed | 1 | 0 | logs\pydata__xarray-4966_06_Keep-All_main_fixed.log |
| pydata__xarray-4966 | Random-Filtering | main | buggy | 1 | 0 | logs\pydata__xarray-4966_06_Random-Filtering_main_buggy.log |
| pydata__xarray-4966 | Random-Filtering | main | fixed | 1 | 0 | logs\pydata__xarray-4966_06_Random-Filtering_main_fixed.log |
| pydata__xarray-4966 | Risk-Aware-Triage | main | buggy | 1 | 0 | logs\pydata__xarray-4966_06_Risk-Aware-Triage_main_buggy.log |
| pydata__xarray-4966 | Risk-Aware-Triage | main | fixed | 1 | 0 | logs\pydata__xarray-4966_06_Risk-Aware-Triage_main_fixed.log |
| pydata__xarray-4966 | Static-Only | main | buggy | 1 | 0 | logs\pydata__xarray-4966_06_Static-Only_main_buggy.log |
| pydata__xarray-4966 | Static-Only | main | fixed | 1 | 0 | logs\pydata__xarray-4966_06_Static-Only_main_fixed.log |
| pydata__xarray-6744 | Discard-All-Flaky | main | buggy | 13 | 1 | logs\pydata__xarray-6744_06_Discard-All-Flaky_main_buggy.log |
| pydata__xarray-6744 | Discard-All-Flaky | main | fixed | 13 | 1 | logs\pydata__xarray-6744_06_Discard-All-Flaky_main_fixed.log |
| pydata__xarray-6744 | Keep-All | main | buggy | 13 | 1 | logs\pydata__xarray-6744_06_Keep-All_main_buggy.log |
| pydata__xarray-6744 | Keep-All | main | fixed | 13 | 1 | logs\pydata__xarray-6744_06_Keep-All_main_fixed.log |
| pydata__xarray-6744 | Random-Filtering | main | buggy | 13 | 1 | logs\pydata__xarray-6744_06_Random-Filtering_main_buggy.log |
| pydata__xarray-6744 | Random-Filtering | main | fixed | 13 | 1 | logs\pydata__xarray-6744_06_Random-Filtering_main_fixed.log |
| pydata__xarray-6744 | Risk-Aware-Triage | main | buggy | 13 | 1 | logs\pydata__xarray-6744_06_Risk-Aware-Triage_main_buggy.log |
| pydata__xarray-6744 | Risk-Aware-Triage | main | fixed | 13 | 1 | logs\pydata__xarray-6744_06_Risk-Aware-Triage_main_fixed.log |
| pydata__xarray-6744 | Static-Only | main | buggy | 13 | 1 | logs\pydata__xarray-6744_06_Static-Only_main_buggy.log |
| pydata__xarray-6744 | Static-Only | main | fixed | 13 | 1 | logs\pydata__xarray-6744_06_Static-Only_main_fixed.log |

## Explicit Limitations

- planned nodeids were not persisted in the frozen strategy-pool schema
- exact/canonical/fallback matching cannot be reconstructed
- independent stdout/stderr were not persisted in the frozen schema
- exception classes are reconstructed only from per-test outcome/error_type fields
