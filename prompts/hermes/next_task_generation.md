# Hermes 下一任务生成模板

请基于当前仓库状态、已完成任务和研究目标，生成下一批本地任务。

## 生成要求

- 优先补齐当前研究主线最关键的缺口
- 任务粒度适中，尽量能被单个本地代理独立完成
- 每个任务都要明确：
  - `id`
  - `title`
  - `type`
  - `assigned_to`
  - `priority`
  - `status`
  - `prompt_file`
  - `expected_outputs`
  - `quality_checks`
  - `requires_human_approval`

## 输出目标

- 给出建议加入 `tasks/task_queue.json` 的任务列表
- 给出这些任务之间的优先顺序和依赖关系
- 如果涉及硬件，必须明确标注人工确认要求
