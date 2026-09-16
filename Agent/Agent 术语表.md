# Agent 术语表

> 标签：#概念/Agent #术语 #glossary

| 术语 | 英文 | 含义 |
|------|------|------|
| 智能体 / 代理 | Agent | 以 LLM 为大脑、能自主规划调用工具完成目标的系统 |
| 代理系统 | Agentic systems | 涵盖 Workflow 与 Agent 的所有相关应用总称 |
| 增强型 LLM | Augmented LLM | 集成了检索/工具/记忆能力的 LLM，是所有模式基石 |
| 工作流 | Workflow | 用预定义代码路径编排 LLM 与工具（可预测、一致） |
| 规划 | Planning | 把复杂任务拆解为子步骤并动态调整 |
| 任务分解 | Task Decomposition | 拆任务的方法：CoT / ToT / LLM+P 等 |
| 思维链 | CoT | Chain of Thought，让模型一步步思考 |
| 思维树 | ToT | Tree of Thoughts，树状多路径搜索 |
| 记忆 | Memory | 短期（上下文）+ 长期（外部向量存储） |
| 短期记忆 | STM | 上下文窗口内的 in-context 信息 |
| 长期记忆 | LTM | 外部向量库，近似无限容量 |
| 最大内积搜索 | MIPS | 向量检索的核心计算，常用 ANN 加速 |
| 工具使用 | Tool Use | 调用外部 API / 代码 / 函数 |
| 函数调用 | Function Calling | 模型输出结构化调用指令由宿主执行 |
| ReAct | ReAct | Thought→Action→Observation 的推理-行动耦合循环 |
| Reflexion | Reflexion | 带动态记忆与自我反思的闭环框架 |
| 反思 | Reflection | Agent 执行后评估并沉淀经验以改进 |
| 评估者-优化者 | Evaluator-Optimizer | 生成者+评估者循环互促 |
| 提示链 | Prompt chaining | 顺序步骤、可加 gate 检查 |
| 路由 | Routing | 输入分类导向不同处理分支 |
| 并行化 | Parallelization | 分段 / 投票式并行处理 |
| 编排者-工作者 | Orchestrator-workers | 中央动态分解任务并汇总 |
| 多智能体 | Multi-Agent | 多个 Agent 角色分工协作 |
| 交接 | Handoff | 一个 Agent 把任务转交更合适的 Agent |
| 护栏 | Guardrails | 权限/校验/预算等安全约束 |
| 检索增强生成 | RAG | 检索外部知识拼入上下文再生成 |
| 智能体-计算机接口 | ACI | Agent 与工具/环境交互的接口设计 |
| 防错设计 | Poka-yoke | 通过接口设计防止误用（如强制绝对路径） |
| 追踪 | Tracing | 记录 Agent 每步 thought/action/observation 以便调试 |

## 相关
- 总入口：[[AI Agent 智能体 概述]]
- 框架：[[主流框架对比]]
- 工程：[[构建最佳实践]]
