# 实验与工具脚本功能分类导航 (Scripts Directory)

本目录包含本研究项目全流程自动化实验、深度分析、图表生成与质量保障脚本。

---

## 脚本分类清单

### 1. 主实验与正式重跑流水线 (Formal Experiments)
- **`run_phase4_rerun.py`**: **【核心正式重跑脚本】** 执行 $N=20$ 轮动态洗牌、变异击杀、真实缺陷检出评估、物理策略池持久化与全套 SHA-256 签名生成。
- **`run_phase4_study.py`**: Phase IV 实验基础配置与流水线编排模块。
- **`generate_expanded_tests.py`**: 17 个 SWE-bench Verified 实例的测试用例生成与提示词装配。

### 2. 专项深度实证脚本 (Specialized Empirical Benchmarks)
- **`run_hermetic_ci_benchmark.py`**: 密闭 CI 物理断网压力实测主脚本（注入 `HERMETIC_CI=1` 守卫，全量 13 实例实测）。
- **`plot_hermetic_ci_benchmark.py`**: 自动生成密闭 CI 网络违规数与构建可行率对比图（Figure 3）。
- **`run_cross_model_study.py`**: 跨模型代际对比实测脚本（加载 Qwen2.5-7B 生成测试，提取 AST 画像与四级分诊分布）。
- **`run_sensitivity_analysis.py`**: 参数阈值敏感性网格扫描与结构性双峰分析（生成 Table 4）。
- **`analyze_quarantine_remediation.py`**: 隔离用例自动化打桩修复可行性分析（生成 100% 自动修复统计）。
- **`analyze_deep_diagnostics.py`**: 测试失败与环境脆弱性深层诊断。

### 3. 论文成果自动化导出 (Artifact Generation)
- **`generate_paper_artifacts.py`**: 从指定运行结果 JSON（如 `run_phase4_rerun_20260926_090500`）动态提取数据并生成 LaTeX 表格（Table 1–3）与矢量图表（Figure 1–2）。
- **`align_references.py`**: 核验 `main.tex` 与 `references.bib` 的 50 篇文献双向引用与排版对齐。

### 4. 质量红线与数据一致性审计 (Auditing & Quality Assurance)
- **`verify_sync.py`**: **【全链数据一致性门禁】** 严格核验所有手稿、Markdown、LaTeX 表格与最新正式实验运行数据是否 100% 绝对一致。
- **`_audit_repos_state.py`**: **【共享仓库零污染审计】** 自动化执行 5 大共享基准仓库 `git status --porcelain` 校验，输出 `data/repos_state_audit.json`。
- **`verify_phase3_pilot.py`**: 校验 Phase III 试点运行证据链。
- **`verify_closed_loop.py`**: 校验 Phase II 闭环重验数据。
- **`_verify_snapshot.py`**: 校验 Phase I 快照清单与文件哈希。

---

## 常用命令速查

```bash
# 1. 运行全套数据同步检验
python scripts/verify_sync.py

# 2. 运行底层代码库干净度审计
python scripts/_audit_repos_state.py

# 3. 基于最新正式实验结果重新导出论文表格与图表
python scripts/generate_paper_artifacts.py --run-id run_phase4_rerun_20260926_090500

# 4. 运行密闭 CI 断网压力基准测试
python scripts/run_hermetic_ci_benchmark.py

# 5. 运行跨模型对比实验分析
python scripts/run_cross_model_study.py
```
