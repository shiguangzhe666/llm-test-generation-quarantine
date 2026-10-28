# 实验配置文件目录 (Configs Directory)

本目录预留用于存放自定义实验运行或模型推理的 YAML/JSON 配置文件。

> **说明**:
> 本研究所使用的 17 个 SWE-bench Verified 实例配置与执行参数已通过严格类型化的 Python 数据类直接编排于 [`../scripts/run_phase4_study.py`](file:///f:/%E8%AE%BA%E6%96%87/llm-test-stability/scripts/run_phase4_study.py) 中的 `INSTANCE_CONFIGS`，以实现跨平台无依赖的确定性加载与冻结协议校验。
