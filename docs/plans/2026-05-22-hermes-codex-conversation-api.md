# Hermes ↔ Local Codex 会话式重构实施计划

> **For Hermes:** Use subagent-driven-development skill to implement this plan task-by-task.

**Goal:** 将当前“云端 Hermes → GitHub 任务队列 → 本地 runner → Codex”的单轮任务制，重构为“云端 Hermes ↔ 本地 Codex worker”的可连续追问、可持续上下文的会话式协作架构。

**Architecture:** 云端 Hermes 负责发起与审查 turn，本地只保留一个常驻 worker 进程，按 `conversation_id` 管理多个逻辑会话。交互层优先使用 HTTP/RPC 风格接口，Git 仅作为转录、产物和审计持久化层；这样可以保留可追溯性，同时让 Hermes 和 Codex 像“对话”一样反复迭代，而不是依赖任务队列轮询。

**Tech Stack:** Python、FastAPI、Pydantic、SQLite/JSON 文件持久化、Git、Cloudflare Tunnel、Hermes Agent 现有工具链。

---

## 设计原则

1. **对话优先，任务从属**：系统核心单位是 `conversation` 与 `turn`，不是单次 task。
2. **单 worker，多会话**：默认先实现一个本地 worker 进程，内部管理多个逻辑会话；以后再扩展多 worker。
3. **Git 只做持久化**：Git 记录 transcript、metadata、artifacts，不承担实时调度职责。
4. **可审查、可回放、可回滚**：每轮输入输出都落盘，所有状态更新都可复盘。
5. **向后兼容**：保留现有 task queue 作为兼容层，逐步迁移，而不是一次性推翻。

---

## Task 1: 定义会话式数据模型

**Objective:** 设计 `conversation`、`turn`、`artifact` 的持久化结构，为后续 API 和 worker 提供统一语义。

**Files:**
- Create: `docs/multi_turn_codex_v2.md`
- Modify: `src/local_runner/codex_sessions.py`
- Modify: `src/local_runner/task_store.py`
- Modify: `tasks/task_queue.json`（增加兼容字段示例，不破坏旧格式）

**Step 1: 写出数据结构草案**

定义最少字段：
- `conversation_id`
- `worker_id`
- `status`
- `turns[]`
- `artifacts[]`
- `last_turn_at`
- `last_error`

**Step 2: 明确 turn 结构**

每轮 turn 至少包含：
- `turn_id`
- `user_prompt`
- `merged_prompt`
- `model_output`
- `changed_files`
- `created_at`
- `status`

**Step 3: 明确兼容策略**

旧 task queue 仍可映射为：
- `task_id` → `turn_id`
- `prompt_file` → 当前 turn 输入
- `codex:<instance>` → 会话 worker 路由键

---

## Task 2: 设计本地 worker API

**Objective:** 让云端 Hermes 能直接向本地 worker 追加 turn，而不是写入一次性任务队列。

**Files:**
- Create: `src/local_runner/session_api.py`
- Modify: `src/local_runner/orchestrator.py`
- Modify: `src/local_runner/main.py` 或 FastAPI 启动入口
- Modify: `docs/cloudflare_tunnel.md`

**API 建议：**
- `POST /sessions`：创建会话
- `POST /sessions/{conversation_id}/turns`：追加新一轮问题
- `GET /sessions/{conversation_id}`：查看会话状态
- `GET /sessions/{conversation_id}/transcript`：读取完整转录
- `GET /sessions/{conversation_id}/artifacts`：列出产物
- `POST /sessions/{conversation_id}/resume`：继续某会话
- `POST /sessions/{conversation_id}/stop`：停止会话 worker

**Step 1: 约束接口输入**

只允许固定字段，不接受任意 shell 命令。

**Step 2: 约束接口输出**

返回：
- `conversation_id`
- `turn_id`
- `status`
- `transcript_path`
- `artifact_paths`

**Step 3: 保留安全边界**

所有写入操作仍要经过固定工作目录和白名单路径校验。

---

## Task 3: 改造本地 Codex 执行路径

**Objective:** 让 worker 不再依赖单轮 task 执行，而是按 conversation 读取历史并追加 turn。

**Files:**
- Modify: `src/local_runner/orchestrator.py`
- Modify: `src/local_runner/codex_sessions.py`
- Modify: `src/local_runner/logging_utils.py`
- Modify: `tests/test_local_orchestrator.py`
- Add: `tests/test_session_api.py`

**Step 1: 抽出会话加载逻辑**

worker 启动时读取某个 `conversation_id` 的历史 transcript，构造上下文。

**Step 2: 抽出 turn 处理逻辑**

每个 turn 执行后，统一写入：
- `transcript.md`
- `metadata.json`
- `turns/<turn_id>_merged_prompt.md`

**Step 3: 保留兼容模式**

旧 `task_queue` 仍可作为外壳：
- task 只是一个 turn 的外部包装
- 但内部实际执行走 session API / session state

---

## Task 4: 云端 Hermes 侧重构

**Objective:** 把云端 Hermes 的工作流从“发任务”改成“发 turn / 审查 turn / 追问 turn”。

**Files:**
- Modify: `prompts/codex/*.md`
- Modify: `docs/multi_turn_codex.md`
- Modify: `README.md`
- Modify: `tasks/research_prd.json` 或上层调度文档

**Step 1: 统一编排语义**

云端侧不再默认要求完整任务分解，而是允许：
- 直接发起对话
- 追加修正轮次
- 让 Codex 继续改同一会话

**Step 2: 改写提示词模板**

把提示词从“执行这个单轮任务”改成“你在一个持续会话里继续推进本项目”。

**Step 3: 更新审查语言**

云端 Hermes 的审查应显式检查：
- 是否保留会话上下文
- 是否沿用了上轮约束
- 是否产生可回放产物

---

## Task 5: 迁移与兼容层

**Objective:** 让旧队列可以平滑迁移到新会话式架构，避免一次性切换导致全链路不可用。

**Files:**
- Modify: `src/local_runner/task_store.py`
- Modify: `src/local_runner/state_machine.py`
- Add: `tests/test_session_migration.py`
- Update: `tasks/task_queue.json` 示例

**Step 1: 兼容旧字段**

保留：
- `prompt_file`
- `assigned_to`
- `priority`
- `status`

新增：
- `conversation_id`
- `turn_id`
- `worker_id`
- `multi_turn`

**Step 2: 迁移映射**

把单轮 task 转成新 turn 时，确保旧流程仍能读懂历史记录。

**Step 3: 回滚方案**

保留一个开关，必要时可回退到单轮 task queue 模式。

---

## Task 6: 验证与演示

**Objective:** 用最小可运行样例证明 Hermes ↔ Codex 可以连续问答，而不是只跑一次任务。

**Files:**
- Add: `tests/test_session_roundtrip.py`
- Add: `docs/examples/session_roundtrip.md`
- Modify: `progress.md`

**Step 1: 做一个两轮最小样例**

- Turn 1：让 Codex 输出一个唯一 marker 并写入文件
- Turn 2：让 Codex 读取上轮 transcript，明确回应 marker 是否可见

**Step 2: 验证产物**

检查：
- `transcript.md` 是否有连续 turn
- `metadata.json` 是否记录 turn 历史
- 是否保留完整文件修改痕迹

**Step 3: 演示云端交互**

云端 Hermes 直接对本地 worker 追问 2-3 轮，确认不需要再通过任务队列拆分。

---

## 推荐实施顺序

1. 数据模型
2. Session API
3. Worker 改造
4. 云端 Hermes 提示词重构
5. 迁移兼容层
6. 两轮 roundtrip 验证

---

## 验收标准

- 能通过 `conversation_id` 连续追加多轮问题
- 本地 worker 能保留并读取完整 transcript
- 云端 Hermes 可以直接追问下一轮，不依赖重新拆任务
- 旧 task queue 仍能兼容运行
- 所有 turn 有可回放的文件和日志

---

## 回滚策略

如果新架构不稳定：
- 暂时关闭 session API
- 回退到旧 task queue runner
- 保留 transcript/metadata，不删除历史会话

