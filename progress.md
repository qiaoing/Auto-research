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
