# LEAF-MPC MATLAB 平台：双 MPC 求解器统一接口与 MATLAB toolbox fallback


你是本地 Codex，正在为 LEAF-MPC 论文实现 MATLAB 仿真平台。必须遵守：
- 代码注释用中文；文件路径严格按任务要求；不要执行真实硬件实验。
- 目标系统：6DOF 离散 UUV，状态 x=[eta(6); nu(6)]，控制 u 为 6 维广义力/力矩。
- 轨迹：3D 八字，x-y 为主，z 有起伏。
- 先跑通 baseline MPC；后续提供 RL 学 P,Q,R,lambda 的接口和可复现实验流程。
- MATLAB 代码需要尽量不依赖专有 toolbox；若 toolbox 不存在，应自动 fallback 到自写求解器/启发式优化器。
- 生成 results/*.mat、figures/*.png，并尽量生成 figures/*.gif 或 *.mp4 动画。
- 不能只写空壳：主脚本至少能用 Octave/MATLAB 语法检查或 dry-run 方式运行；如果本地无 MATLAB，请写 Python/Octave 兼容检查脚本并记录限制。
- 每个任务完成后更新 progress.md，并把关键结果、运行命令、生成文件写清楚。


这是第三轮，请审查并扩展已有 baseline。

必须实现：
1. `mpc/mpc_solver_matlab.m`：封装 MATLAB 工具箱/优化工具箱版本。如果 toolbox 不存在，必须自动 fallback 到 `mpc_solver_custom`，并在 info.solver/status 中说明。
2. `mpc/mpc_solve.m` 或统一接口层：根据 `config.solverType = "custom"/"matlab"` 切换求解器，上层主程序不需要改其它代码。
3. 修改 `main/run_baseline_mpc.m` 支持 solverType 参数。
4. 新增 `main/run_compare_experiments.m` 初版：至少比较 custom 与 matlab/fallback 两组，输出统一 metrics。
5. `utils/compute_metrics.m`：平均误差、RMS、最大误差、控制峰值、控制变化率、约束违背次数、平均计算时间。
6. 生成 `figures/solver_comparison_3d.png` 和 `results/solver_comparison.mat`。

验收：
- 同一主程序可切换 solverType。
- 两种接口输出结构一致 `[u_opt, info]`。
- 工具箱缺失时不崩溃。
- 更新 progress.md。
