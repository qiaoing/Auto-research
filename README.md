# Research Autopilot for Learning-based MPC of Multimodal Underwater Robots

本仓库是一个面向“多模态水下机器人学习型 MPC / RL-MPC 科研自动化”的本地执行工作区。它用于承接云端研究编排、完成本地代码实现、仿真、绘图、实验设计整理，以及论文工程搭建。

## 项目目标

- 建立可复现的水下机器人科研仓库骨架
- 支持文献筛选、创新点挖掘、理论建模与仿真实验
- 支持学习控制器、RL-MPC、强非线性系统与扰动不准场景研究
- 统一保存结果、图表、实验设计记录和论文素材

## 角色分工

- `Hermes`：云端总控，负责文献调研、创新点挖掘、任务拆分、阶段审查与下一步任务生成
- `Codex`：本地实现代理，负责动力学建模、控制器、仿真代码、测试和复杂实现任务
- `OpenCode`：本地辅助代理，负责绘图脚本、结果整理、轻量重构和论文基础设施
- `PythonRunner / PlotAgent / PaperAgent`：本地执行辅助角色，分别用于运行脚本、产出图表和维护论文工程

## 目录结构

```text
.
├── README.md
├── AGENTS.md
├── project_state.json
├── progress.md
├── tasks/                  # 本地任务队列、科研 PRD、已完成任务
├── prompts/                # 面向 Codex / OpenCode / Hermes 的任务提示词
├── research/               # 文献、创新点、理论建模材料
├── src/                    # Python 仿真与算法代码
├── configs/                # 默认配置、控制器配置、仿真配置
├── experiments/            # 仿真方案与实物实验设计文档
├── figures/                # 图表输出目录
├── results/                # 仿真结果、处理结果与指标汇总
├── data/                   # 原始数据与预处理数据
├── paper/                  # 论文主文件、章节与参考文献
├── scripts/                # 本地调度与辅助脚本
├── tests/                  # 结构测试与功能测试
├── logs/                   # 调度和任务运行日志
└── docs/                   # 规划文档与过程记录
```

## 本地运行方式

常用检查命令：

```bash
python -m pytest -q
python scripts/local_orchestrator.py
python src/visualization/plot_trajectory.py --help
```

典型使用流程：

1. 由 `Hermes` 更新 `tasks/task_queue.json`
2. 本地执行 `python scripts/local_orchestrator.py`
3. 由 `Codex` 或 `OpenCode` 按任务提示词完成实现
4. 结果写入 `results/`、图表写入 `figures/`、论文素材写入 `paper/`

### 多轮 Codex 任务

任务队列支持多个本地 Codex 逻辑会话。使用 `assigned_to: "codex:<instance>"` 加 `conversation_id`，runner 会在每一轮 Codex 执行前自动注入该会话的历史 transcript，并在完成后追加本轮输入/输出到 `state/codex_sessions/<instance>/<conversation_id>/transcript.md`。

示例：

```json
{
  "id": "CTRL-002",
  "assigned_to": "codex:controller",
  "conversation_id": "learning-mpc-controller",
  "status": "pending",
  "prompt_file": "prompts/codex/CTRL-002.md"
}
```

详见 `docs/multi_turn_codex.md`。

## 安全注意事项

- 禁止自动执行真实硬件实验
- 任何硬件相关任务只能停留在设计、脚本、检查项、dry-run 或离线回放阶段
- 涉及控制输出时必须考虑限幅、异常保护与急停机制
- 不得在仓库中硬编码 API key、token 或其他凭据

## 人工确认要求

以下事项必须人工确认后才能继续推进：

- 最终研究方向选择
- 真实硬件实验执行
- 论文投稿或对外发布
