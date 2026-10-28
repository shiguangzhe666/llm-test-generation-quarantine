# 实验可复现性说明指南 (Replication Package Guide)

本说明文档指导审稿人与研究者完全端到端复现论文《面向缺陷发现能力保持的 LLM 生成测试稳定化：项目级实证研究与风险感知筛选框架》中的所有实验数据、统计指标、LaTeX 表格与矢量图表。

---

## 1. 环境依赖与快速准备

- **操作系统**: Windows 10/11 或 Linux (x86_64)
- **Python 版本**: Python 3.11.x (推荐 Python 3.11.9；若系统安装了多个 Python 版本，推荐使用 Windows 官方启动器 `py -3.11` 或 Linux `python3.11` 显式指定版本，避免默认调用到未安装依赖的高版本 Python，如 Python 3.14)
- **核心依赖**:
  ```bash
  # 使用目标 Python 3.11 环境安装依赖
  py -3.11 -m pip install pytest pytest-xdist datasets matplotlib numpy scipy
  ```
- **Git 环境**: Git 2.30+ (支持 `git worktree`)
- **本地 LLM (可选，重跑测试生成时使用)**: Ollama 运行 `qwen3:8b` (本复现包已完整附带生成好的测试套件，无需再次调用 LLM 即可重现实证全流程)。

---

## 2. 一键复现核心成果

### 2.1 重新生成论文图表与 LaTeX 统计表
基于已固化的全量正式实证实验结果（`results/runs/run_phase4_rerun_20260926_090500/`），运行以下命令可瞬间重新生成论文正文引用的全部表格与矢量图：
```powershell
# Windows (推荐使用 py -3.11 显式定位，亦可直接使用对应 python.exe)
py -3.11 scripts/generate_paper_artifacts.py --run-id run_phase4_rerun_20260926_090500
```
**产出成果清单**:
- `paper/emse_submission/tables/tab_benchmark_matrix.tex` (表 1: 17 实例 4 领域基准矩阵，含 Part A 13 个有效评估实例与 Part B 4 个协议排除实例)
- `paper/emse_submission/tables/tab_tool_taxonomy.tex` (工具分类学与适用性对比矩阵，对比 DeFlaker、FlakeFlagger、CoverUp 等)
- `paper/emse_submission/tables/tab_strategy_comparison.tex` (表 2: 5 策略聚合对比矩阵，含项目级聚类标准误)
- `paper/emse_submission/tables/tab_hypothesis_tests.tex` (表 3: Wilcoxon 符号秩检验与 Vargha-Delaney $\hat{A}_{12}$ 效应量)
- `paper/emse_submission/tables/tab_sensitivity_analysis.tex` (表 4: 缺陷检测潜力与风险阈值敏感性分析矩阵)
- `paper/emse_submission/tables/tab_hermetic_ci_benchmark.tex` (表 5: 密闭 CI 断网隔离基准实测对比表)
- `paper/emse_submission/tables/tab_cross_model_comparison.tex` (表 6: 四模型跨机构跨架构大矩阵对比表：Qwen3-8B, Qwen2.5-7B, DeepSeek-Coder-6.7B, CodeLlama-7B，共 923 条测试)
- `paper/emse_submission/figures/fig_triage_breakdown.pdf` / `.png` (图 1: 四级分诊自适应分布堆叠图)
- `paper/emse_submission/figures/fig_pareto_frontier.pdf` / `.png` (图 2: 帕累托最优与多目标权衡分析图)
- `paper/emse_submission/figures/fig_hermetic_ci_comparison.pdf` / `.png` (图 3: 密闭 CI 断网隔离与套件崩溃对比图)
- `paper/emse_submission/figures/fig_cross_model_comparison.pdf` / `.png` (图 4: 四模型跨厂商代码质量与分诊分布对比图)

### 2.2 运行阈值敏感性与隔离用例深度分析
```powershell
py -3.11 scripts/run_sensitivity_analysis.py
py -3.11 scripts/analyze_quarantine_remediation.py
```
**预期输出**: 在当前生成候选样本中复核 $S_{defect} \in [0.4, 0.7]$ 的分流变化，以及 $\mathrm{Risk} \in [0.10, 0.40]$ 区间内观察到的分配稳定性。该结果仅描述当前样本，不单独证明阈值具有跨项目泛化性。

### 2.3 验证自动化回归测试套件 (48 项全量测试)
运行项目核心算法与隔离机制的回归测试套件（含断网隔离单元测试）：
```powershell
py -3.11 -m pytest tests/ -v
```
**预期输出**: 48 passed in ~20-25s (100% 通过率)。

### 2.4 验证共享基准仓库零污染证明
运行只读基线审计脚本，核验 5 个共享仓库的 HEAD 与物理洁净状态：
```powershell
py -3.11 -c "from scripts._audit_repos_state import audit_all_repos; import json; print(json.dumps(audit_all_repos(), indent=2))"
```
**预期输出**: `all_repos_clean: true`，全部 5 个仓库均为 0 diff, 0 untracked。

### 2.5 一键复现密闭 CI 断网基准测试 (Hermetic CI Benchmark)
```powershell
py -3.11 scripts/run_hermetic_ci_benchmark.py
```
**预期输出**: 评估 13 个实例在 socket 隔离条件下的网络诱发套件崩溃。权威 run 记录 Keep-All 有 24 次违规、2/13 次网络诱发崩溃；Risk-Aware-Triage 为 0 次违规、0/13 次此类崩溃。此结果不表示完整 CI 全绿：12/13 套件仍有普通非网络失败。该指标仅描述网络故障隔离。

### 2.6 一键复现选定模型的描述性比较 (Multi-Model Descriptive Study)
```powershell
py -3.11 scripts/run_multi_model_benchmark.py
```
**预期输出**: 对四模型共 923 个生成候选函数作静态分析，其中 775 个被收集。URL-token 数依次为 Qwen3 62、Qwen2.5 61、DeepSeek-Coder 59、CodeLlama 4；因此 59--62 的观察仅适用于前三者。Tier 2 比例的分母是全部生成候选函数，包含未收集候选，不代表可执行套件比例，也不构成跨模型缺陷保持证据。

---

## 3. 全量实证流水线重跑 (End-to-End Study Execution)

如需重跑研究，请注意：$N=20$ 仅指固定版本上的动态 shuffle profiling 轮数，并非策略池物理执行轮数；策略池记录通常是每策略一次执行。权威结果以 `run_phase4_rerun_20260926_090500` 为准。仅在证据审计发现关键结果不可复核时针对性重跑，不应将下列命令理解为此前每个分析均已按该流程产生：
```powershell
python scripts/run_phase4_rerun.py --num-runs 20 --max-mutants 3
```
- **执行时间**: 约 25-45 分钟（包含 13 个有效实例的 308 条用例多轮并发执行、独立测试池物理评估与变异体杀伤分析）；
- **产物位置**: `results/runs/run_phase4_rerun_<TIMESTAMP>/`；
- **增量防丢机制**: 实验进度由 `instance_results_incremental.json` 实时落盘，断点后无需从头执行。

---

## 4. 关键证据与数据映射索引 (Traceability Matrix)

| 论文元素 | 对应数据文件路径 | 关键校验字段 / 验证指标 |
|:---|:---|:---|
| **表 1 (基准矩阵)** | `results/runs/run_phase4_rerun_20260926_090500/phase4_full_study_results.json` | 13 个有效实例，4 个协议排除实例（共 308 条测试，3 个真实 Bug） |
| **表 2 (策略对比)** | 同上 | Triage: 77.5% ± 18.2% 保留率，**19.5% ± 15.8% 隔离缓冲**，100.0% 缺陷保持率，100.0% 确定性；Keep-All: 100.0% ± 0.0% 确定性 |
| **表 3 (假设检验)** | 同上 | Triage 隔离率 $W=0.0, p=0.0591, \hat{A}_{12}=0.69$ (Medium 效应量)；14/14 条缺陷检测测试均保留仅表示当前子集未观察到损失，$p=1.0000$ 不证明策略等价。缺陷样本为 $n=3$ 个实例，存在 ceiling effect。 |
| **表 4 (敏感性分析)** | `paper/emse_submission/tables/tab_sensitivity_analysis.tex` | $S_{defect} \in [0.4, 0.7]$ 平滑过渡，$\mathrm{Risk} \in [0.1, 0.4]$ 结构性双峰绝对恒定 |
| **表 5 (密闭 CI 实测)** | `results/runs/run_phase4_rerun_20260926_090500/` | Keep-All: 24 violations, 2/13 network-induced crashes; Triage: 0 violations, 0/13 such crashes. 12/13 suites still had ordinary non-network failures. |
| **表 6 (跨模型静态分析)** | `results/cross_model_study_results.json` | 923 generated candidates, 775 collected; URL tokens: Qwen3 62, Qwen2.5 61, DeepSeek-Coder 59, CodeLlama 4. Tier percentages use generated candidates, not executable suites. |
| **图 1 (分诊堆叠)** | `paper/figures/fig_triage_breakdown.pdf` | 四级分诊在各实例上的自适应分布 |
| **图 2 (帕累托图)** | `paper/figures/fig_pareto_frontier.pdf` | 零人工抖动，展示诚实权衡前沿与 19.5% 隔离缓冲 |
| **图 3 (密闭 CI 对比)** | `paper/figures/fig_hermetic_ci_comparison.pdf` | 密闭网络违规拦截数与干净套件可行率对比 |
| **图 4 (跨模型对比)** | `paper/figures/fig_cross_model_comparison.pdf` | 四模型跨厂商代码质量与四级分诊比例对比 |
| **策略物理测试池报告** | `results/runs/run_phase4_rerun_20260926_090500/strategy_pools/<instance>/` | 5 策略在 Fixed 与 Buggy 上的真实独立测试报告 JSON |
| **真实缺陷记录** | `results/runs/run_phase4_rerun_20260926_090500/commands.jsonl` | `*_buggy_defect_eval.log` |
| **排除实例跟踪** | `results/runs/run_phase4_rerun_20260926_090500/logs/` | `*_exclusion_traceback.log` (4 份真实原始异常日志) |
| **完整哈希清单** | `results/runs/run_phase4_rerun_20260926_090500/manifest.json` | 363 份文件的 SHA-256 签名 |

## 5. 最终结果的审计边界

权威结果为 `run_phase4_rerun_20260926_090500`。该 run 可支持文中已报告的实例级与测试级统计，但当前归档未保留足以逐条复核的 planned nodeids，也没有保存独立 stdout/stderr 和所有匹配决策的完整记录。因此 exact、canonical 与 fallback 匹配数量均标记为不可审计，不推断其匹配模式。跨模型 Tier 分布来自 generated candidates；逐候选的收集映射未保留，故 executable-only Tier 比例不可审计。

如需补强这些审计字段，应针对受影响实例与策略池进行定向重跑，并保存 planned/observed nodeids、匹配模式、完整测试报告、退出码、stdout/stderr、异常分类及生成脚本版本；不默认重跑全部 13 个实例。历史 run 仅作为开发记录，不用于主结论。

---

## 5. 质量与学术诚信承诺

本项目所有代码与实验结果恪守软件工程学术规范：
1. **真实无伪造**: 严禁编造数据，所有结论均直接基于代码执行与日志；
2. **零信息泄漏**: 测试生成阶段未引入任何补丁或参考测试；
3. **真实排除记录**: 4 个不可执行的实例未被掩盖，全部在论文《效度威胁》与复现包中显式标明原因与异常栈。
4. **共享仓库持续零污染**: 依托 Git Worktree 隔离机制，共享仓库始终保持 0 diff, 0 untracked。
