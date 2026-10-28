# LLM Test Stability Study

Quality-Preserving Stabilization of LLM-Generated Tests:
A Project-Level Empirical Study and Risk-Aware Triage Framework

## Project Structure

```
llm-test-stability/
├── src/                    # Source code
│   ├── generation/         # LLM test generation
│   ├── execution/          # Test execution & repeated runs
│   ├── detection/          # Flakiness detection & classification
│   ├── triage/             # Risk-aware test triage/filtering
│   ├── evaluation/         # Defect detection & mutation testing
│   └── utils/              # Shared utilities
├── configs/                # Experiment configurations
├── data/
│   ├── benchmarks/         # Dataset metadata & commit hashes
│   ├── generated_tests/    # Raw LLM-generated test outputs
│   └── execution_logs/     # Test execution logs
├── results/                # Experiment results & analysis
├── scripts/                # Automation scripts
├── prompts/                # LLM prompt templates
└── paper/                  # Paper drafts & figures
```

## Current Status & Evidence Tracking

- **Phase I (资产重盘点与保护)**: ✅ 已验收。建立三重快照（189+7 文件被 SHA-256 追踪，位于 `snapshots/`）。
- **Phase II (实验正确性修复与最小闭环重验)**: ✅ 已验收。
  - 端到端重审验证档案: `results/runs/run_phase2_reaudit_20260921_011520/` (包含 10 份结构化档案、7 份运行日志及 `commands.jsonl`)；
  - 自动化回归测试: 27/27 100% 通过 (`pytest tests/ -v`)；
  - 真实 SWE-bench 缺陷复现: `psf__requests-1921` 评估全部 6 个 `FAIL_TO_PASS` 用例（确认断言失败缺陷检出）及 107 个 `PASS_TO_PASS` 用例全量盘点；
  - 变异评估防护: 落实单字节 SHA-256 还原核对、强制 pycache 清理与模块导入源隔离检查；
  - 结构化执行器: 严谨标记 `MISSING_OBSERVATION`，杜绝退出码 0 静默通过；精细化统计 7 类用例状态；
  - 共享基准仓库保护: `data/repos/` 下 5 个基准仓库运行前后均 100% 保持 Clean: True，0 diff，0 untracked；
  - 第一作者批复正式通过。
- **Gate 1 (文献新颖性与相关工作审计)**: ✅ 已验收。
  - 详细报告: `literature_audit/gate1_novelty_audit_report.json` 与 `literature_audit/gate1_novelty_audit_report.md`；
  - 48 条文献记录全部核查完毕：33 篇已确证（具备正式 DOI 与官方索引），7 篇部分证实，8 篇未确证占位符（P01, P04, P05, P06, P07 等已正式剥离）；
  - 重点比对 6 篇最接近一线文献并完成审稿人抗辩分析；第一作者批复正式通过。
- **Phase III (数据探测与研究可行性校验)**: ✅ 已验收 (Gate 2 批复通过)。
  - 端到端试点与审计档案: `results/runs/run_phase3_pilot_20260921_081700/` (包含 13 份证据文件与 6 份全量日志，`manifest.json` 完整校验)；
  - 疑似 Flaky 测试病理确证: `psf__requests-2317` 两条测试（`test_session_request_with_utf8_encoding` / `test_request_with_non_ascii_path`）包含未 Mock 的真实网络请求与 IDN 域名解析；
  - 四阶段计数差异闭环: 确证生成 23 = 收集 23；执行 18/19 归因于旧执行器套件超时丢弃；分诊归因于未传字典与 0.4 缩放缺陷，已完成代码修复与回归测试验证；
  - 真实 Bug vs 测试条数厘清: `requests-1921` 为 1 真实 Bug / 1 检出测试；`sympy-15809` 为 1 真实 Bug / 6 检出测试；
  - 双实例实证与权衡确证: 在 Requests 与 SymPy 上实证验证“Discard-All-Flaky 造成缺陷丢失，风险感知分诊保全 100% 缺陷”的核心科学命题；第一作者对话明确批复 Gate 2 通过。
- **Phase IV (冻结协议后开展正式实验)**: ✅ 已完成。
  - 实验协议已正式冻结: `plan/experiment_protocol.md`（定义 RQ1-RQ3、多领域矩阵、聚类稳健标准误、Vargha-Delaney 效应量及熔断纪律）；
  - 全量规模扩展实证档案: `results/runs/run_phase4_expanded_20260922_120000/`（62 份文件被 SHA-256 清单追踪，17 实例 4 领域基准矩阵，13 有效实例生成并评估 308 条测试）；
  - 自动化回归测试: 36/36 100% 通过 (`pytest tests/ -v`)；
  - 核心实证确证: 保持 100.0% 真实缺陷（3/3）与缺陷测试（14/14），实现 18.0% ± 14.6% 隔离送检率与 100.0% 主干 CI 确定性，确证位列帕累托最优前沿；
  - 共享基准仓库保护: 运行前后 5 个共享仓库均 100% Clean (0 diff, 0 untracked)。
- **Phase V (论文撰写与成果交付)**: ✅ 已交付。
  - 顶级期刊标准手稿: `paper/manuscript.md`、`paper/manuscript_en.md`、`paper/emse_submission/main.tex`；
  - 论文就绪型 LaTeX 表格与矢量图表: `paper/tab_benchmark_matrix.tex`, `paper/tab_strategy_comparison.tex`, `paper/tab_hypothesis_tests.tex`, `paper/figures/fig_pareto_frontier.pdf` / `.png`, `paper/figures/fig_triage_breakdown.pdf` / `.png`；
  - 完整复现包指南: `paper/REPLICATION.md`；
  - 自动化生成脚本: `scripts/generate_paper_artifacts.py`。
- **Phase VI (深度审计与实证口径校正)**: ✅ 已验收。修正聚类标准误过滤逻辑，彻底废除人工抖动，全面校准学术表述与天花板效应。
- **Phase VII (正式实验重跑与全链证据闭环)**: ✅ 已验收。遵照 10 条重跑协议执行全量实证重跑（`run_phase4_rerun_20260923_211103`，106 份文件 SHA-256 清单）。
- **Phase VIII (深度复现审计加固与最终全量正式重跑)**: ✅ 已验收。
  - 修复物理策略池报告持久化、缺失观测保留 None 语义与统计检验成对过滤；
  - 正式运行: `results/runs/run_phase4_rerun_20260924_001649/`（363 份文件 SHA-256 清单，Keep-All 抖动率 0.3% ± 0.3%，Triage 隔离率 19.2% ± 15.5%，100.0% 缺陷保持率，100.0% 主干确定性）；
  - 自动化回归测试: 40/40 100% 通过 (`pytest tests/ -v`)。
- **Phase IX (审稿缺陷全面修复与顶刊提交就绪)**: ✅ 已验收。
  - 摘要与表 1 数值 100% 绝对对齐；统一 363 份文件 SHA-256 清单引用；补充 Section 3.4 Tier 2 隔离池生命周期与 Section 6.2.3 单模型泛化性论证。
- **Phase X (全量实证重跑、46项测试加固与论文数据终审对齐)**: ✅ 已验收。
  - 最新正式重跑: `results/runs/run_phase4_rerun_20260926_090500/`（363 份文件 SHA-256 清单，耗时 39 分钟，5 仓库 100% Clean）；
  - 全量数据同步锁定: 准入保留率 77.5% ± 18.2%，隔离送检率 19.5% ± 15.8%，缺陷保持率 100.0%（14/14），主干 CI 确定性 100.0%；
  - 自动化回归测试扩充至 46/46 100% 通过。
- **Phase XI (顶刊文献体系扩充至50篇与全套手稿深度对齐)**: ✅ 已验收。
  - 文献库扩充至 50 篇权威文献（`references.bib` 与 `main.tex` 100% 双向命中，覆盖经典选择、Flaky 生态、SBST 基线与 SE 统计规范）；
  - 中英文完整手稿与 LaTeX 深度统一图表编号（图 1: 分诊堆叠图，图 2: 帕累托最优与多目标权衡图）。
- **Phase XII (与SOTA顶刊论文全方位对齐与论文硬核补强)**: ✅ 已验收。
  - 对标 11 篇顶刊顶会（TestGen-LLM, CoverUp, ChatUniTest, DeFlaker 等），补齐表 1 工具分类学与适用性矩阵；
  - 增补 5.4 节隔离用例案例剖析（确证 100% 具备深层断言价值且 100% 可通过 `requests_mock` 自动打桩修复）；
  - 增补 5.5 节阈值敏感性分析（表 4，确证代码脆弱性天然呈现结构性双峰，参数极其稳健）；
  - 补齐构建可用率 (76.47%) 与运行开销指标（静态扫描仅需 2.4ms/函数）。
- **Phase XIII (面向顶刊录用标准的科学实证双支柱加固)**: ✅ 已验收。
  - **密闭 CI 物理断网压力实测**: 注入 `HERMETIC_CI=1` 物理断网守卫，实测确证 Keep-All 触发 24 次网络违规并导致 15.4% 套件整体崩溃，Triage 实现 0 违规与 100.0% 可行（表 5, 图 3）；
  - **跨模型代际对比实测**: 本地部署 Qwen2.5-7B 合成 282 条测试对比主数据集 Qwen3-8B（308 条），实证揭示未打桩网络脆弱性呈现代际恒定（61 vs. 62 个 Token），Triage 隔离缓冲极其稳健（18.1% vs. 20.1%）（表 6, 图 4）；
  - 自动化测试扩充至 48/48 项全过。
- **Phase XIV (审稿要点靶向封堵、口径精准校准与投稿包终结打包)**: ✅ 已验收。
  - 建立与 Static-Only 的核心分水岭：表 5 扩充资产保全列，明确 Static-Only 永久破坏 77 条测试（25.0%），而 Triage 完整留存 62 条高价值用例（20.1%）并可 100% 自动打桩修复；
  - 严格界定缺陷天花板（n=3 Bug，14 缺陷测试，$p=1.0000$）与跨模型泛化性定位，杜绝大样本伪显著性过度宣称；
  - 抗辩指南新增 Question 10 专打“为何不用纯静态过滤”；
  - 重新固化 `paper/emse_submission_package.zip`（999 KB，纯 ASCII LaTeX 标准，50 篇文献，20 份完整提交文件）。

## Directory Conventions & Path Mappings

- `data/repos/`: 只读基准仓库镜像，严格流程约束，禁止就地 `git checkout` 或修改源码，统一通过 `git worktree` 临时隔离运行。
- `data/sample_project/`: 合成对照用例与轻量组件（`config_parser.py`, `cache_manager.py`），提供已知可杀/存活/基线失败等对照用例。
- `literature_audit/` (`F:\论文\literature_audit`): 48 条文献记录全面核查台账与 Gate 1 审计报告。
- `results/runs/<run_id>/`: 所有新实验的独立落盘目录，严格独立存储，绝不覆盖历史运行记录。

## Environment Requirements

- Python 3.11.x (推荐使用 Windows `py -3.11` 或 Linux `python3.11` 显式定位，确保 pytest, scipy, matplotlib 等科学计算依赖完备；若系统已安装 Python 3.14 等高版本，避免直接使用无版本号的 `python` 命令)
- Git 2.x+ (支持 `git worktree`)
- pytest, pluggy, datasets, matplotlib, numpy, scipy (SWE-bench Verified)
