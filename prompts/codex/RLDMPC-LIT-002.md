你是本地 Codex 文献调研代理。请围绕用户论文《面向无人水下航行器大机动轨迹跟踪的自适应学习增强可微模型预测控制》中的第三部分 Proposed LEAF-MPC for UUV Trajectory Tracking，第二小节 “Differentiable MPC with RL-Learned Parameters” 做专题文献调研。

论文设定：LEAF-MPC 使用增强 PPO + 可微 MPC 学习 MPC 中的 P、Q、R 参数矩阵/权重参数；RL 不直接输出控制输入，而是输出/调节 MPC 代价函数权重、终端权重、控制权重、约束惩罚/鲁棒补偿等参数。应用背景是 UUV 高速、大姿态、大机动轨迹跟踪，存在模型失配和非平稳扰动。

请完成：
1. 搜索并核验相关英文文献，优先给 DOI/arXiv/会议/期刊来源，不要编造。
2. 提取每篇文献与“RL 调 MPC 参数 / differentiable MPC / policy gradient through MPC / PPO + MPC / learning MPC cost weights / safe RL with MPC / robotics trajectory tracking”的关系。
3. 给出可用于论文小节的写作要点：问题动机、方法公式、学习变量、训练目标、约束处理、与端到端 RL 的区别。
4. 输出中文 Markdown 报告，包含：核心文献表、关键公式/思想、可引用句子、对本文 LEAF-MPC 的启发、参考文献列表。
5. 严格标注“强相关/中等相关/背景相关”，并说明不确定之处。

输出文件：reports/research/RLDMPC-LIT-002-rl-learned-mpc-weights.md
不要修改代码；只写调研报告和必要的 progress.md 更新。

本任务特殊关注：聚焦 RL/PPO/SAC 等学习 MPC 代价权重、P/Q/R/终端权重、MPC 参数调节、Learning MPC。
