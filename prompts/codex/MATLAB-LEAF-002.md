# LEAF-MPC MATLAB 平台：baseline MPC 闭环、结果图表


你是本地 Codex，正在为 LEAF-MPC 论文实现 MATLAB 仿真平台。必须遵守：
- 代码注释用中文；文件路径严格按任务要求；不要执行真实硬件实验。
- 目标系统：6DOF 离散 UUV，状态 x=[eta(6); nu(6)]，控制 u 为 6 维广义力/力矩。
- 轨迹：3D 八字，x-y 为主，z 有起伏。
- 先跑通 baseline MPC；后续提供 RL 学 P,Q,R,lambda 的接口和可复现实验流程。
- MATLAB 代码需要尽量不依赖专有 toolbox；若 toolbox 不存在，应自动 fallback 到自写求解器/启发式优化器。
- 生成 results/*.mat、figures/*.png，并尽量生成 figures/*.gif 或 *.mp4 动画。
- 不能只写空壳：主脚本至少能用 Octave/MATLAB 语法检查或 dry-run 方式运行；如果本地无 MATLAB，请写 Python/Octave 兼容检查脚本并记录限制。
- 每个任务完成后更新 progress.md，并把关键结果、运行命令、生成文件写清楚。


这是第二轮，请基于上一轮代码继续，不要重写已有接口。

必须实现 baseline MPC 闭环：
1. `mpc/mpc_cost.m`：实现 J=sum e'Qe+u'Ru+du'Sdu+terminal e'Pe。
2. `mpc/mpc_constraints.m`：控制/状态约束检查与违背统计。
3. `mpc/mpc_build_prediction.m`：给定 x0 和控制序列预测 N 步。
4. `mpc/mpc_solver_custom.m`：自写 MPC 求解器。可先用 fmincon；若没有 Optimization Toolbox，则使用 deterministic random shooting / CEM-like 简化优化作为 fallback。接口：`[u_opt, info] = mpc_solver_custom(xk, refHorizon, weights, constraints, model)`。
5. `main/run_baseline_mpc.m`：闭环跟踪 3D 八字，滚动优化，每步应用第一个控制量。
6. `utils/plot_results_3d.m`、`utils/plot_tracking_metrics.m`、`utils/save_results.m`。

输出：
- `results/baseline_mpc_result.mat`
- `figures/baseline_3d_tracking.png`
- `figures/baseline_tracking_errors.png`
- `figures/baseline_control_inputs.png`
- logs 中保存运行摘要。

验收：
- baseline 脚本可运行或至少 dry-run 到保存结果；误差不能明显发散（若参数需调整，自行调整）。
- 控制输入有限且限幅。
- 更新 progress.md。
