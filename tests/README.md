# 自动化回归测试套件导航 (Tests Directory)

本目录包含保障本实证研究系统正确性、统计计算严密性与沙箱隔离性的 48 项单元与集成回归测试。

---

## 测试文件清单与验证重点

| 测试模块 | 测试数 | 核心验证重点与质量红线 |
| :--- | :---: | :--- |
| **`test_control_cases.py`** | 6 | 验证对照用例：已知可杀与存活变异体识别、基线失败用例杜绝虚假击杀、运行时异常 vs 断言失败区分、单字节 SHA-256 还原核对。 |
| **`test_execution_modes.py`** | 4 | 验证三种测试执行模式（顺序、单用例独立、多轮随机洗牌）；验证跳过与未执行状态的精准区分。 |
| **`test_hermetic_ci.py`** | 2 | 验证 `HERMETIC_CI=1` 物理网络断网守卫：有效拦截非本地出站 TCP/UDP 请求，且安全放行本地 IPC 与 Mock 调用。 |
| **`test_loader_isolation.py`** | 4 | 验证 `IsolatedWorktree` 临时工作树环境：保证底层 5 大共享仓库零写入与 100% 干净删除，补丁错误显式报错拒绝静默回退。 |
| **`test_mutation_eval_baseline.py`** | 3 | 验证变异测试基线多轮预检（Baseline Pre-check）、零分母容错处理与共享仓库物理改写熔断拦截。 |
| **`test_nodeid_matching.py`** | 6 | 验证 pytest nodeid 精准拆分、跨作用域防碰撞、参数化用例后缀匹配及歧义检测。 |
| **`test_pareto_analysis.py`** | 7 | 验证统计学计算核心：Vargha-Delaney $\hat{A}_{12}$ 效应量、成对 Wilcoxon 检验、聚类稳健标准误、Wilson 95% 置信区间及帕累托前沿计算。 |
| **`test_rerun_evidence_chain.py`** | 4 | 验证重跑证据链：未完成观测不默认补零、真实缺陷检出严苛校验（要求 Buggy 失败且 Fixed 稳定通过）。 |
| **`test_risk_triage_metrics.py`** | 7 | 验证四级分诊决策逻辑：冷启动报告、未打桩外部 URL 检测、异常处理块评分及分诊路由防歧义碰撞。 |
| **`test_structured_reporting.py`** | 5 | 验证 pytest 结构化 JSON 报告：收集错误与导入异常捕获、套件中断与未执行区分、同名函数与类隔离。 |

---

## 运行回归测试命令

```bash
# 执行全部 48 项自动化测试
pytest tests/ -v
```
