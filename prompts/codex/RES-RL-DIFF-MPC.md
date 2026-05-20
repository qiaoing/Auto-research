# 任务 RES-RL-DIFF-MPC：调研 RL 与可微 MPC / Differentiable MPC 融合方法

你是 Codex，本地代码/研究代理，正在当前 Git 仓库中工作。请完成一个**中文 Markdown 深度调研报告**，不要只写提纲。

## 调研主题

RL 可微 MPC（Reinforcement Learning + Differentiable MPC / differentiable optimization layers / learning MPC costs and dynamics）

## 输出文件

请创建或覆盖：`reports/research/RES-RL-DIFF-MPC.md`

## 具体要求

1. 报告使用中文，结构清晰，包含摘要、概念定义、方法分类、代表文献/方向、优缺点比较、与水下机器人 RL-MPC/学习控制器的结合建议。
2. 至少列出 8 条可核验参考线索（论文题名/作者/年份/期刊会议或 arXiv/DOI/URL 线索均可）。如果无法联网，基于已有知识写出“待核验”标记，不要编造 DOI。
3. 用表格比较主要方法：核心思想、假设条件、优点、局限、适用场景。
4. 给出 3-5 个适合后续研究的创新方向，尤其关注：水下强非线性、模型不准、扰动估计不准、约束控制、实物实验可落地性。
5. 保持学术严谨：明确哪些是已验证结论，哪些是推测/待核验。
6. 更新 `progress.md`，追加一条本任务完成记录。

## 调研重点

- 可微 MPC / differentiable MPC 的核心思想：把 MPC/QP/NLP 求解器作为可微层，端到端学习代价、约束松弛、动力学残差或策略参数
- RL 与 MPC 的结合方式：MPC 作为 policy、critic、actor 中的结构化先验；RL 学习 MPC 参数；安全约束与样本效率
- 近 5 年代表论文/工具/基准，优先机器人、UAV、水下机器人/非线性系统相关
- 适合用户水下机器人 RL-MPC/学习控制器研究的创新切入点

## 质量检查

本任务没有 pytest 检查；但你必须确保 `reports/research/RES-RL-DIFF-MPC.md` 文件存在且内容不是空文件。

## 规则

- 不要修改无关源代码。
- 不要执行硬件任务。
- 不要删除已有报告。
- 成功后让本地 runner 提交状态更新即可。
