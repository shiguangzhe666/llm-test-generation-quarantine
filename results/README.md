# 实证实验数据与结果归档导航 (Results Directory)

本目录集中存储本研究从 Phase II 闭环重验到 Phase XIV 终审全量实证实验的原始输出、JSON 结构化记录、运行日志及分析数据。

---

## 核心结果文件与正式基线

### 1. 当前论文官方基准运行 (Official Publication Baseline)
- **运行 ID**: `run_phase4_rerun_20260926_090500`
- **路径**: [`runs/run_phase4_rerun_20260926_090500/`](file:///f:/%E8%AE%BA%E6%96%87/llm-test-stability/results/runs/run_phase4_rerun_20260926_090500/)
- **说明**: 论文正文（表 1–3、图 1–2、摘要及正文所有统计数值）的唯一正式数据来源。包含：
  - `phase4_full_study_results.json`: 全量聚合统计与假设检验数据；
  - `manifest.json`: 363 份实验数据与日志文件的 SHA-256 签名清单；
  - `strategy_pools/`: 5 大策略在每个实例 Fixed 与 Buggy 状态下的真实独立 pytest 运行报告；
  - `logs/`: 每个实例的测试发现、多轮洗牌、变异评估与缺陷检出原始日志。

### 2. 专项深度实证数据 (Specialized Empirical Benchmarks)
- **密闭 CI 物理断网压力实测**:
  - 文件: [`hermetic_ci_benchmark_results.json`](file:///f:/%E8%AE%BA%E6%96%87/llm-test-stability/results/hermetic_ci_benchmark_results.json)
  - 支撑: 论文 5.7 节、表 5 与图 3。确证未经治理套件触发 24 次网络违规并导致 15.4% 套件整体崩溃，Risk-Aware-Triage 实现 100% 密闭可行。
- **跨模型代际对比实证**:
  - 文件: [`cross_model_study_results.json`](file:///f:/%E8%AE%BA%E6%96%87/llm-test-stability/results/cross_model_study_results.json)
  - 支撑: 论文 5.8 节、表 6 与图 4。横向对比 Qwen3-8B（308 条）与 Qwen2.5-7B（282 条），确证网络脆弱性代际恒定（61 vs. 62 个 Token）与分诊稳健性（18.1% vs. 20.1%）。

---

## 历史阶段性实证档案 (Historical Audit Runs)

| 运行目录 | 对应阶段 | 核心验证目的与成果 |
| :--- | :---: | :--- |
| `run_phase4_rerun_20260924_001649/` | Phase VIII–IX | 早期正式全量重跑记录（363 份文件 SHA-256 签名归档）。 |
| `run_phase4_rerun_20260923_211103/` | Phase VII | 协议冻结后的首次全量正式重跑记录。 |
| `run_phase4_expanded_20260922_120000/` | Phase IV | 路径 B 扩展至 17 实例 4 领域的首轮全量评估。 |
| `run_phase4_refined_20260921_193000/` | Phase IV 细化 | 多轮洗牌调度细化测试记录。 |
| `run_phase4_study_20260921_100000/` | Phase IV 初测 | 17 实例初步执行冒烟验证。 |
| `run_phase3_pilot_20260921_081700/` | Phase III | 双实例试点实测，确证未打桩网络请求为 Flaky 核心诱因。 |
| `run_phase2_reaudit_20260921_011520/` | Phase II | 最小闭环重验，确证共享仓库零污染隔离与变异单字节还原。 |
| `run_phase2_closure_20260920/` | Phase II | 早期闭环尝试归档。 |
