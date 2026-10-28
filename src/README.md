# 核心算法与框架源码导航 (Source Code Directory)

本目录包含本研究提出的 **Risk-Aware-Triage** 框架、密闭断网守卫、多轮洗牌执行引擎与统计分析包的完整实现源码。

---

## 模块结构与职责划分

```
src/
├── triage/             # 【四级分诊决策中枢】
│   ├── ast_features.py       # 静态 AST 语义特征提取（断言特异性 S_defect、外部 URL、异常捕获分析）
│   ├── triage_engine.py      # 四级分诊分配器（Tier 1 主干、Tier 2 隔离、Tier 3 夜间、Tier 4 丢弃）
│   └── sensitivity.py        # 阈值敏感性网格扫描与结构性双峰分析模块
│
├── execution/          # 【沙箱隔离与多轮测试执行引擎】
│   ├── isolated_worktree.py  # 基于 Git Worktree 的临时隔离工作区管理器（杜绝污染底层共享仓库）
│   ├── repeated_executor.py  # 多轮测试执行器（支持顺序、独立与多轮随机洗牌 Suite-Random 模式）
│   └── pytest_structured_plugin.py # 自定义 pytest 插件（包含 HERMETIC_CI=1 物理断网守卫与结构化 JSON 报告）
│
├── detection/          # 【脆弱性与非确定性探测器】
│   └── flakiness_detector.py # 基于多轮执行日志计算抖动率与非确定性根因归类
│
├── evaluation/         # 【双真值评测管道】
│   ├── real_defect_eval.py   # 真实缺陷评估器（基于 SWE-bench Buggy/Fixed 状态计算缺陷保持率）
│   └── mutation_eval.py      # 变异测试评估器（集成基线多轮预检与单字节还原校验）
│
├── analysis/           # 【统计学检验与多目标权衡】
│   └── pareto_analysis.py   # Vargha-Delaney A12 效应量、成对 Wilcoxon、聚类稳健标准误与帕累托前沿计算
│
├── generation/         # 【LLM 测试生成管道】
│   ├── prompt_builder.py     # 严格单向信息隔离 Prompt 装配器（仅输入 base_commit 源码）
│   └── code_extractor.py     # 模型输出解析与 Python 测试函数规范化提取器
│
└── utils/              # 【基础工具与规范化支持】
    ├── nodeid_utils.py       # 规范化 pytest nodeid 拆分、匹配与歧义检测器
    └── log_utils.py          # 结构化日志记录与 JSONL 流水线日志工具
```
