# Research Autopilot 进度日志

## 仓库约定

- 本仓库使用 `tasks/task_queue.json` 作为本地任务队列。
- `Codex` 主要用于仿真代码、动力学建模和复杂实现任务。
- `OpenCode` 主要用于绘图脚本、整理工作和论文基础设施任务。
- 任何真实硬件实验都必须经过人工确认。

---

## 初始化阶段

- 仓库已初始化完成。
- 项目目录结构已创建。
- 等待 `Hermes` 继续生成或更新研究任务。

## 初始化状态

- 文档骨架已创建。
- 任务队列与提示词模板已创建。
- 研究、实验、图表和论文占位文件已创建。

## 2026-05-19

- `SIM-001` 已完成：实现了耦合型 3-DOF 平面水下机器人动力学模型，文件位于 `src/dynamics/underwater_vehicle.py`。
- 已为 `SIM-001` 补充测试，覆盖输出维度、零速度平衡、固定输入确定性和偏航角积分行为，文件位于 `tests/test_underwater_vehicle.py`。
- 已验证 `python -m pytest -q` 通过。
- [2026-05-19 23:01:22] 本地调度器已将 `SIM-001` 标记为完成。

## 2026-05-20

- 新增本地 Runner API 服务：支持 `/health`、`/status`、`/tasks`、`/run-once`、`/logs/{task_id}` 和 `/webhook/github`。
- 本地任务状态机扩展为 `pending`、`claimed`、`running`、`review`、`done`、`failed`、`blocked`、`cancelled`。
- 新增 Windows/Linux 启动脚本、systemd 用户服务安装脚本、部署文档和架构文档。
- 安全限制：API 不接收任意命令或 prompt；webhook 使用 GitHub HMAC；硬件和人工审批任务会转为 `blocked`；质量检查仅允许 `pytest` 形式。

- 2026-05-20T07:24:34+00:00 Task RUN-ONCE-SMOKE claimed by local-runner.

- 2026-05-20T07:24:34+00:00 Task RUN-ONCE-SMOKE started.

- 2026-05-20T07:24:35+00:00 Task RUN-ONCE-SMOKE moved to review.

- 2026-05-20T08:52:39+00:00 Task SIM-002 claimed by local-runner.

- 2026-05-20T08:52:39+00:00 Task SIM-002 started.

- 2026-05-20T08:52:40+00:00 Task SIM-002 failed quality checks: could not start quality check.

- 2026-05-20T09:20:00+00:00 Task SIM-002 reset to pending for real execution path validation.

- 2026-05-20T09:57:44+00:00 Task FIG-001 claimed by local-runner.

- 2026-05-20T09:57:44+00:00 Task FIG-001 started.

- 2026-05-20T09:57:45+00:00 Task FIG-001 failed: quality check command is not allowed: .

- 2026-05-20T10:01:16+00:00 Task SIM-002 claimed by local-runner.

- 2026-05-20T10:01:16+00:00 Task SIM-002 started.

- 2026-05-20T10:04:44+00:00 Task SIM-002 failed: orchestrator exception: 'gbk' codec can't decode byte 0x80 in position 9783: illegal multibyte sequence.

- 2026-05-20T12:19:42+00:00 No pending task found for local runner.

- 2026-05-20T12:59:00+00:00 Task SIM-002 claimed by local-runner.

- 2026-05-20T12:59:00+00:00 Task SIM-002 started.

- 2026-05-20T13:00:57+00:00 Task SIM-002 failed: orchestrator exception: 'gbk' codec can't decode byte 0x80 in position 9783: illegal multibyte sequence.

- 2026-05-20T13:01:09+00:00 No pending task found for local runner.

- 2026-05-20T14:00:57+00:00 No pending task found for local runner.

- 2026-05-20T14:55:28+00:00 Task RES-RL-DIFF-MPC claimed by local-runner.

- 2026-05-20T14:55:28+00:00 Task RES-RL-DIFF-MPC started.

- 2026-05-20T15:12:59+00:00 Task RES-RL-DIFF-MPC failed: orchestrator exception: 'gbk' codec can't decode byte 0x94 in position 906: illegal multibyte sequence.

- 2026-05-20T15:13:09+00:00 Task RES-FXTA-ESO claimed by local-runner.

- 2026-05-20T15:13:09+00:00 Task RES-FXTA-ESO started.

- 2026-05-20T15:20:37+00:00 Task RES-FXTA-ESO failed: orchestrator exception: 'gbk' codec can't decode byte 0x80 in position 929: illegal multibyte sequence.

- 2026-05-20T15:20:48+00:00 Task RES-FORGETTING-FACTOR claimed by local-runner.

- 2026-05-20T15:20:48+00:00 Task RES-FORGETTING-FACTOR started.

- 2026-05-20T15:29:31+00:00 Task RES-FORGETTING-FACTOR failed: orchestrator exception: 'gbk' codec can't decode byte 0xaa in position 9895: illegal multibyte sequence.

- 2026-05-20T15:29:42+00:00 No pending task found for local runner.

- 2026-05-21T03:19:34+00:00 No pending task found for local runner.

- 2026-05-21T03:58:59+00:00 No pending task found for local runner.

- 2026-05-21T04:03:21+00:00 Task MT-SMOKE-001 claimed by local-runner.

- 2026-05-21T04:03:21+00:00 Task MT-SMOKE-001 started.

- 2026-05-21T04:03:53+00:00 Task MT-SMOKE-001 moved to review.

- 2026-05-21T04:04:03+00:00 Task MT-SMOKE-002 claimed by local-runner.

- 2026-05-21T04:04:03+00:00 Task MT-SMOKE-002 started.

- 2026-05-21T04:04:03+00:00 Task MT-SMOKE-002 failed: ������̫����.

- 2026-05-21T04:04:13+00:00 No pending task found for local runner.

- 2026-05-21T04:25:06+00:00 Task MT-SMOKE-RERUN-001 claimed by local-runner.

- 2026-05-21T04:25:06+00:00 Task MT-SMOKE-RERUN-001 started.

- 2026-05-21T04:26:27+00:00 Task MT-SMOKE-RERUN-001 moved to review.

- 2026-05-21T04:26:37+00:00 Task MT-SMOKE-RERUN-002 claimed by local-runner.

- 2026-05-21T04:26:37+00:00 Task MT-SMOKE-RERUN-002 started.

- 2026-05-21T04:26:38+00:00 Task MT-SMOKE-RERUN-002 failed: ������̫����.

- 2026-05-21T04:26:47+00:00 No pending task found for local runner.

- 2026-05-21T05:03:12+00:00 Task MT-STDIN-001 claimed by local-runner.

- 2026-05-21T05:03:12+00:00 Task MT-STDIN-001 started.

- 2026-05-21T05:03:37+00:00 Task MT-STDIN-001 moved to review.

- 2026-05-21T05:03:47+00:00 Task MT-STDIN-002 claimed by local-runner.

- 2026-05-21T05:03:47+00:00 Task MT-STDIN-002 started.

- 2026-05-21T05:04:17+00:00 Task MT-STDIN-002 moved to review.

- 2026-05-21T05:04:28+00:00 No pending task found for local runner.

- 2026-05-21T08:45:24+00:00 Task RLDMPC-LIT-001 claimed by local-runner.

- 2026-05-21T08:45:24+00:00 Task RLDMPC-LIT-001 started.

- 2026-05-21T09:22:45+00:00 Task RLDMPC-LIT-001 failed: missing expected outputs: reports/research/RLDMPC-LIT-001-differentiable-mpc.md.

- 2026-05-21T09:22:56+00:00 Task RLDMPC-LIT-002 claimed by local-runner.

- 2026-05-21T09:22:56+00:00 Task RLDMPC-LIT-002 started.
- 2026-05-21 已完成 `RLDMPC-LIT-002` 文献调研报告，输出文件为 `reports/research/RLDMPC-LIT-002-rl-learned-mpc-weights.md`。
- `RLDMPC-LIT-002` 聚焦 `RL/PPO/DDPG` 学习 `MPC` 代价权重、终端权重、控制权重、软约束惩罚与相关元参数，报告中已按“强相关/中等相关/背景相关”标注文献相关度并说明不确定项。
- 已对输出文件进行回读检查，确认报告已写入目标路径。

- 2026-05-21T09:35:41+00:00 Task RLDMPC-LIT-002 moved to review.

- 2026-05-21T09:35:51+00:00 Task RLDMPC-LIT-003 claimed by local-runner.

- 2026-05-21T09:35:51+00:00 Task RLDMPC-LIT-003 started.

- 2026-05-21T09:35:56+00:00 Task RLDMPC-LIT-003 failed: 2026-05-21T09:35:52.425604Z  WARN codex_core_plugins::startup_remote_sync: startup remote plugin sync failed; will retry on next app-server start error=chatgpt authentication required to sync remote plugins; api key auth is not supported
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
ERROR: Selected model is at capacity. Please try a different model..
