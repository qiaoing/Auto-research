You are local Codex instance `sim` continuing conversation `leaf-mpc-matlab-sim-20260521-sim` for repository `G:\AI_workspace\localserver`.

This is a multi-turn task. Use the prior transcript as durable conversation context, then answer/act on the new turn. Keep changes scoped to the new task, but preserve decisions, APIs, and assumptions already established in this conversation.


# New turn task

# LEAF-MPC MATLAB 平台：项目骨架、6DOF UUV 模型、3D 八字轨迹


你是本地 Codex，正在为 LEAF-MPC 论文实现 MATLAB 仿真平台。必须遵守：
- 代码注释用中文；文件路径严格按任务要求；不要执行真实硬件实验。
- 目标系统：6DOF 离散 UUV，状态 x=[eta(6); nu(6)]，控制 u 为 6 维广义力/力矩。
- 轨迹：3D 八字，x-y 为主，z 有起伏。
- 先跑通 baseline MPC；后续提供 RL 学 P,Q,R,lambda 的接口和可复现实验流程。
- MATLAB 代码需要尽量不依赖专有 toolbox；若 toolbox 不存在，应自动 fallback 到自写求解器/启发式优化器。
- 生成 results/*.mat、figures/*.png，并尽量生成 figures/*.gif 或 *.mp4 动画。
- 不能只写空壳：主脚本至少能用 Octave/MATLAB 语法检查或 dry-run 方式运行；如果本地无 MATLAB，请写 Python/Octave 兼容检查脚本并记录限制。
- 每个任务完成后更新 progress.md，并把关键结果、运行命令、生成文件写清楚。


这是第一轮实现任务。请创建完整 MATLAB 项目骨架：

目标目录建议为 `matlab/leaf_mpc/`，内部至少包含：
main/, models/, trajectory/, mpc/, rl/, utils/, tests/, results/, figures/, logs/。

必须实现：
1. `models/model_params_default.m`：返回 params，包含 dt、质量/惯量、阻尼、控制限幅、状态限幅、扰动默认值等。
2. `models/uuv_model_step.m`：统一接口 `function x_next = uuv_model_step(x, u, params, disturbance)`，12维状态、6维控制、离散积分，默认扰动 0。要有中文注释和输入检查。
3. `models/uuv_model_wrap.m`：便于 MPC 调用的包装器。
4. `trajectory/traj_fig8_3d.m`：接口 `function ref = traj_fig8_3d(t, cfg)`，输出 ref.pos/ref.vel/ref.acc/ref.yaw_ref/ref.x_ref，x-y 八字且 z 有起伏。
5. `trajectory/traj_utils.m`：提供角度 wrap、参考状态拼接等工具函数。
6. `tests/test_model_and_trajectory.m`：最小 MATLAB/Octave 风格测试脚本，验证维度、可复现、轨迹连续、z 起伏。
7. `main/run_smoke_tests.m`：统一运行 smoke tests。
8. `README.md` 或 `matlab/leaf_mpc/README.md`：说明如何运行。

验收：
- 文件存在且不是空壳。
- 固定 x/u 调用模型可得到有限数值 x_next。
- 轨迹生成器能生成 3D 八字采样并保存一张 `figures/fig8_reference_3d.png`（如环境无图形后端，写明降级）。
- 更新 progress.md。
