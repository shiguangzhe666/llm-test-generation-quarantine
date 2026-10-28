# Phase IV · 正式实证研究报告 (Full Empirical Study Report)

**运行标识 (Run ID)**: `run_phase4_study_20260921_100000`  
**执行日期**: 2026-09-21T02:19:06.668319  
**环境**: Python 3.11 | Git Worktree 隔离 | 5 共享仓库 100% Clean  
**完成实例数**: 5 / 7  

---

## 1. 策略对比总览 (Strategy Comparison Matrix)

| 策略 (Strategy) | 可执行保留率 (%) | 隔离送检率 (%) | 主干 CI 确定性 (%) | 真实 Bug 保持率 (%) | 缺陷测试保持率 (%) | 变异得分 (%) |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|
| **Keep-All** | 100.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 | 100.0 ± 0.0 | 100.0 ± 0.0 | 13.3 ± 7.2 |
| **Discard-All-Flaky** | 100.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 | 100.0 ± 0.0 | 100.0 ± 0.0 | 13.3 ± 7.2 |
| **Random-Filtering** | 63.3 ± 10.6 | 0.0 ± 0.0 | 100.0 ± 0.0 | 100.0 ± 0.0 | 83.3 ± 16.7 | 13.3 ± 7.2 |
| **Static-Only** | 100.0 ± 0.0 | 0.0 ± 0.0 | 100.0 ± 0.0 | 100.0 ± 0.0 | 100.0 ± 0.0 | 13.3 ± 7.2 |
| **Risk-Aware-Triage** | 63.3 ± 10.6 | 0.0 ± 0.0 | 100.0 ± 0.0 | 66.7 ± 33.3 | 66.7 ± 33.3 | 13.3 ± 7.2 |

---

## 2. 统计显著性与效应量 (Hypothesis Testing & Effect Sizes)

| 对比项 | Wilcoxon $W$ | $p$-value | Vargha-Delaney $\hat{A}_{12}$ | 效应量解释 (Magnitude) |
|:---|:---:|:---:|:---:|:---:|
| **Triage_vs_Discard-All-Flaky_Defect_Retention** | 0 | 1.0000 | 0.4 | SMALL |
| **Triage_vs_Random-Filtering_Defect_Retention** | 0 | 1.0000 | 0.44 | NEGLIGIBLE |
| **Triage_vs_Static-Only_Defect_Retention** | 0 | 1.0000 | 0.4 | SMALL |
| **Triage_vs_Keep-All_Defect_Retention** | 0 | 1.0000 | 0.4 | SMALL |

---

## 3. 帕累托前沿分析 (Pareto Frontier)

帕累托最优策略集合（以 CI 抖动率为 $x$ 轴最小化，缺陷测试保持率为 $y$ 轴最大化）：

- **Keep-All**: CI Flakiness = 0.0%, Defect Retention = 100.0%
- **Discard-All-Flaky**: CI Flakiness = 0.0%, Defect Retention = 100.0%
- **Static-Only**: CI Flakiness = 0.0%, Defect Retention = 100.0%

---

## 4. 协议排除实例与环境审计 (Excluded Instances per Protocol)

根据 `plan/experiment_protocol.md` 第 3.2 节准入与排除准则（排除与 Python 3.11 存在底层 AST 运行时冲突的遗留组件）：

| 实例 ID | 领域 | 排除原因判定 |
|:---|:---|:---|
| `sympy__sympy-17139` | Symbolic Mathematics | EXCLUDED_RUNTIME_INCOMPATIBILITY: 0 tests collected under Python 3.11 environment (e.g. pytest 6.0 AST rewrite incompatibility) |
| `pytest-dev__pytest-7521` | Testing Tools | EXCLUDED_RUNTIME_INCOMPATIBILITY: 0 tests collected under Python 3.11 environment (e.g. pytest 6.0 AST rewrite incompatibility) |