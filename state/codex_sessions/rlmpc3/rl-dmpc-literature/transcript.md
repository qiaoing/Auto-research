

## Turn RLDMPC-LIT-003 — 2026-05-21T09:35:56+00:00

### Hermes/User task

You are local Codex instance `rlmpc3` continuing conversation `rl-dmpc-literature` for repository `G:\AI_workspace\localserver`.

This is a multi-turn task. Use the prior transcript as durable conversation context, then answer/act on the new turn. Keep changes scoped to the new task, but preserve decisions, APIs, and assumptions already established in this conversation.


# New turn task

你是本地 Codex 文献调研代理。请围绕用户论文《面向无人水下航行器大机动轨迹跟踪的自适应学习增强可微模型预测控制》中的第三部分 Proposed LEAF-MPC for UUV Trajectory Tracking，第二小节 “Differentiable MPC with RL-Learned Parameters” 做专题文献调研。

论文设定：LEAF-MPC 使用增强 PPO + 可微 MPC 学习 MPC 中的 P、Q、R 参数矩阵/权重参数；RL 不直接输出控制输入，而是输出/调节 MPC 代价函数权重、终端权重、控制权重、约束惩罚/鲁棒补偿等参数。应用背景是 UUV 高速、大姿态、大机动轨迹跟踪，存在模型失配和非平稳扰动。

请完成：
1. 搜索并核验相关英文文献，优先给 DOI/arXiv/会议/期刊来源，不要编造。
2. 提取每篇文献与“RL 调 MPC 参数 / differentiable MPC / policy gradient through MPC / PPO + MPC / learning MPC cost weights / safe RL with MPC / robotics trajectory tracking”的关系。
3. 给出可用于论文小节的写作要点：问题动机、方法公式、学习变量、训练目标、约束处理、与端到端 RL 的区别。
4. 输出中文 Markdown 报告，包含：核心文献表、关键公式/思想、可引用句子、对本文 LEAF-MPC 的启发、参考文献列表。
5. 严格标注“强相关/中等相关/背景相关”，并说明不确定之处。

输出文件：reports/research/RLDMPC-LIT-003-safe-rl-mpc.md
不要修改代码；只写调研报告和必要的 progress.md 更新。

本任务特殊关注：聚焦 MPC-guided RL、safe RL with MPC、RL as high-level tuner / residual learning / constrained policy optimization。

### Local Codex output

2026-05-21T09:35:52+00:00 starting codex:rlmpc3 task RLDMPC-LIT-003
2026-05-21T09:35:52.425604Z  WARN codex_core_plugins::startup_remote_sync: startup remote plugin sync failed; will retry on next app-server start error=chatgpt authentication required to sync remote plugins; api key auth is not supported
2026-05-21T09:35:52.425675Z  WARN codex_core_plugins::remote::remote_installed_plugin_sync: remote installed plugin bundle sync failed error=chatgpt authentication required for remote plugin catalog; api key auth is not supported
2026-05-21T09:35:53.037857Z  WARN codex_core::shell_snapshot: Failed to create shell snapshot for powershell: Shell snapshot not supported yet for PowerShell
OpenAI Codex v0.131.0
--------
workdir: G:\AI_workspace\localserver
model: gpt-5.4
provider: OpenAI
approval: never
sandbox: read-only
reasoning effort: xhigh
reasoning summaries: none
session id: 019e49e4-342e-7e10-a655-7868e045468f
--------
user
You are local Codex instance `rlmpc3` continuing conversation `rl-dmpc-literature` for repository `G:\AI_workspace\localserver`.

This is a multi-turn task. Use the prior transcript as durable conversation context, then answer/act on the new turn. Keep changes scoped to the new task, but preserve decisions, APIs, and assumptions already established in this conversation.


# New turn task

你是本地 Codex 文献调研代理。请围绕用户论文《面向无人水下航行器大机动轨迹跟踪的自适应学习增强可微模型预测控制》中的第三部分 Proposed LEAF-MPC for UUV Trajectory Tracking，第二小节 “Differentiable MPC with RL-Learned Parameters” 做专题文献调研。

论文设定：LEAF-MPC 使用增强 PPO + 可微 MPC 学习 MPC 中的 P、Q、R 参数矩阵/权重参数；RL 不直接输出控制输入，而是输出/调节 MPC 代价函数权重、终端权重、控制权重、约束惩罚/鲁棒补偿等参数。应用背景是 UUV 高速、大姿态、大机动轨迹跟踪，存在模型失配和非平稳扰动。

请完成：
1. 搜索并核验相关英文文献，优先给 DOI/arXiv/会议/期刊来源，不要编造。
2. 提取每篇文献与“RL 调 MPC 参数 / differentiable MPC / policy gradient through MPC / PPO + MPC / learning MPC cost weights / safe RL with MPC / robotics trajectory tracking”的关系。
3. 给出可用于论文小节的写作要点：问题动机、方法公式、学习变量、训练目标、约束处理、与端到端 RL 的区别。
4. 输出中文 Markdown 报告，包含：核心文献表、关键公式/思想、可引用句子、对本文 LEAF-MPC 的启发、参考文献列表。
5. 严格标注“强相关/中等相关/背景相关”，并说明不确定之处。

输出文件：reports/research/RLDMPC-LIT-003-safe-rl-mpc.md
不要修改代码；只写调研报告和必要的 progress.md 更新。

本任务特殊关注：聚焦 MPC-guided RL、safe RL with MPC、RL as high-level tuner / residual learning / constrained policy optimization。

2026-05-21T09:35:53.827176Z  WARN codex_core_plugins::manifest: ignoring interface.defaultPrompt: prompt must be at most 128 characters path=C:\Users\26938\.codex\.tmp\plugins\plugins\build-ios-apps\.codex-plugin/plugin.json
2026-05-21T09:35:53.829420Z  WARN codex_core_plugins::manifest: ignoring interface.defaultPrompt: maximum of 3 prompts is supported path=C:\Users\26938\.codex\.tmp\plugins\plugins\plugin-eval\.codex-plugin/plugin.json
2026-05-21T09:35:53.846429Z  WARN codex_core_plugins::manifest: ignoring interface.defaultPrompt: maximum of 3 prompts is supported path=C:\Users\26938\.codex\.tmp\plugins\plugins\twilio-developer-kit\.codex-plugin/plugin.json
2026-05-21T09:35:53.846737Z  WARN codex_core_plugins::manifest: ignoring interface.defaultPrompt: maximum of 3 prompts is supported path=C:\Users\26938\.codex\.tmp\plugins\plugins\openai-developers\.codex-plugin/plugin.json
2026-05-21T09:35:53.939771Z  WARN codex_core_plugins::manager: failed to refresh curated plugin cache after sync: failed to refresh curated plugin cache for game-studio@openai-curated: failed to back up plugin cache entry: 拒绝访问。 (os error 5)
ERROR: Selected model is at capacity. Please try a different model.
ERROR: Selected model is at capacity. Please try a different model.
