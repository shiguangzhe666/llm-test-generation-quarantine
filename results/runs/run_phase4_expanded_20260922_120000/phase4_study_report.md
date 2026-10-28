# Phase IV · 正式实证研究报告 (Full Empirical Study Report)

**运行标识 (Run ID)**: `run_phase4_expanded_20260922_120000`  
**执行日期**: 2026-09-22T04:31:04.918084  
**环境**: Python 3.11 | Git Worktree 隔离 | 5 共享仓库 100% Clean  
**完成实例数**: 13 / 17  

---

## 1. 策略对比总览 (Strategy Comparison Matrix)

| 策略 (Strategy) | 可执行保留率 (%) | 隔离送检率 (%) | 主干 CI 确定性 (%) | 真实 Bug 保持率 (%) | 缺陷测试保持率 (%) | 变异得分 (%) |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Keep-All** | 100.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 | 100.0 ± 0.0 | 100.0 ± 0.0 | 5.1 ± 4.2 |
| **Discard-All-Flaky** | 100.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 | 100.0 ± 0.0 | 100.0 ± 0.0 | 5.1 ± 4.2 |
| **Random-Filtering** | 79.6 ± 16.5 | 0.0 ± 0.0 | 100.0 ± 0.0 | 100.0 ± 0.0 | 100.0 ± 0.0 | 5.1 ± 4.2 |
| **Static-Only** | 77.9 ± 17.9 | 0.0 ± 0.0 | 100.0 ± 0.0 | 100.0 ± 0.0 | 100.0 ± 0.0 | 5.1 ± 4.2 |
| **Risk-Aware-Triage** | 79.9 ± 16.3 | 18.0 ± 14.6 | 100.0 ± 0.0 | 100.0 ± 0.0 | 100.0 ± 0.0 | 5.1 ± 4.2 |

---

## 2. 统计显著性与效应量 (Hypothesis Testing & Effect Sizes)

| 对比项 | Wilcoxon $W$ | $p$-value | Vargha-Delaney $\hat{A}_{12}$ | 效应量解释 (Magnitude) |
|:---|:---:|:---:|:---:|:---:|
| **Triage_vs_Discard-All-Flaky_Defect_Retention** | 0.0 | 1.0000 | 0.5 | NEGLIGIBLE |
| **Triage_vs_Random-Filtering_Defect_Retention** | 0.0 | 1.0000 | 0.5 | NEGLIGIBLE |
| **Triage_vs_Static-Only_Defect_Retention** | 0.0 | 1.0000 | 0.5 | NEGLIGIBLE |
| **Triage_vs_Keep-All_Defect_Retention** | 0.0 | 1.0000 | 0.5 | NEGLIGIBLE |
| **Triage_vs_Discard-All-Flaky_Quarantine_Rate** | 0 | 0.1003 | 0.6538 | MEDIUM |
| **Triage_vs_Static-Only_Executable_Retention** | 1.0 | 1.0000 | 0.5296 | NEGLIGIBLE |

---

## 3. 多目标权衡与天花板效应 (Multi-Objective Analysis & Ceiling Effect)

各策略在 (CI Flakiness, Defect Retention) 坐标系中的位置：

- **全部 5 种策略均重合在同一理想坐标点**: CI Flakiness = 0.0%, Defect Retention = 100.0%
- 实证表明：在当前 $N=5$ 轮执行下，所有缺陷检出测试均稳定通过（无抖动），策略间缺陷保持率呈现统计等价的天花板效应；各策略的核心操作权衡体现在主干可执行保留率与离线隔离缓冲率的取舍上。

---

## 4. 协议排除实例与真实技术根因 (Excluded Instances & Technical Root Causes)

| 实例 ID | 领域 | 排除原因与技术根因判定 |
|:---|:---|:---|
| `pytest-dev__pytest-7521` | Testing Tools | ModuleNotFoundError: No module named '_pytest._version' (legacy build metadata dependency missing) |
| `sympy__sympy-17139` | Symbolic Mathematics | ImportError: cannot import name 'simplify' from 'sympy.simplify.fu' (LLM import hallucination) |
| `sympy__sympy-22080` | Symbolic Mathematics | TypeError: print_ccode() takes 1 positional argument but 2 given (incorrect API argument call in generated test) |
| `pydata__xarray-6992` | Scientific Computing | AttributeError / ModuleNotFoundError in top-level code (LLM generation defect) |