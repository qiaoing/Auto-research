# 多 Codex 多轮任务协议

本仓库的 runner 现在支持把云端 Hermes 发布的一组离散任务，映射为本地多个 Codex 实例的“连续多轮会话”。这不是让云端直接打开本地交互式 Codex，而是在 Git 任务队列中显式保存会话身份，并由本地 runner 在每一轮执行时自动注入历史 transcript。

## 核心字段

在 `tasks/task_queue.json` 的任务中使用以下字段：

```json
{
  "id": "CTRL-002",
  "title": "继续完善鲁棒控制器测试",
  "assigned_to": "codex:controller",
  "conversation_id": "learning-mpc-controller",
  "status": "pending",
  "prompt_file": "prompts/codex/CTRL-002.md",
  "expected_outputs": ["src/controllers/robust_mpc.py", "tests/test_robust_mpc.py"],
  "quality_checks": ["pytest tests/test_robust_mpc.py -q"]
}
```

字段含义：

- `assigned_to: "codex:<instance>"`：选择本地 Codex 实例名，例如 `codex:controller`、`codex:sim`、`codex:paper`。
- `conversation_id`：同一实例内的连续对话 ID。相同 `(instance, conversation_id)` 的任务共享历史上下文。
- `multi_turn: true`：可选简写。如果没有 `conversation_id`，会使用 Codex 实例名作为会话 ID。
- 普通 `assigned_to: "codex"` 且没有 `conversation_id` 的任务仍按单轮任务执行。

## runner 行为

1. runner 仍按优先级从 `pending` 中取一个任务。
2. 如果任务是多轮 Codex 任务，runner 会读取：
   `state/codex_sessions/<instance>/<conversation_id>/transcript.md`
3. runner 将历史 transcript 与当前 `prompt_file` 合成为本轮 Codex prompt。
4. 本轮完成后，runner 将当前 prompt 与 Codex 输出追加到同一个 transcript。
5. transcript 文件会作为 `changed_files` 的一部分提交，云端 Hermes 和后续 Codex 轮次都能看到。

## 多个本地 Codex 的用法

可以同时维护多个逻辑 Codex 实例：

```json
[
  {
    "id": "SIM-010",
    "assigned_to": "codex:sim",
    "conversation_id": "auv-dynamics",
    "status": "pending"
  },
  {
    "id": "CTRL-010",
    "assigned_to": "codex:controller",
    "conversation_id": "rl-mpc-controller",
    "status": "pending"
  },
  {
    "id": "PAPER-010",
    "assigned_to": "codex:paper",
    "conversation_id": "tro-paper-draft",
    "status": "pending"
  }
]
```

默认 runner 仍是单进程单任务执行，避免多个 Codex 同时改同一工作区造成冲突；“多个 Codex”在协议上体现为多个独立会话/角色。如果之后需要真正并行执行，应给不同实例配置独立 git worktree 后再放开并发。

## 配置 Codex 命令

默认命令形态为：

```bash
codex exec --cd <repo_root> "<merged_prompt>"
```

可通过环境变量调整 Codex 参数：

```bash
export LOCAL_RUNNER_CODEX_ARGS="exec --full-auto"
```

如果设置了 `LOCAL_RUNNER_CODEX_COMMAND`，runner 会完全使用该模板，适合自定义包装脚本；模板变量仍包括 `{task_id}`、`{prompt_file}`、`{repo_root}`、`{log_file}`。注意：完全自定义模板不会自动注入 transcript，除非包装脚本自行读取 `state/codex_sessions/...`。

## 编码稳定性

runner 对 Codex、质量检查和 Git 子进程输出均使用 `encoding="utf-8", errors="replace"`，并设置 `PYTHONUTF8=1`、`PYTHONIOENCODING=utf-8`，以降低 Windows/中文输出导致的 GBK 解码失败概率。
