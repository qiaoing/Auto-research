# LEAF-MPC MATLAB 平台：最终集成审查、修复与论文级交付整理


你是本地 Codex，正在为 LEAF-MPC 论文实现 MATLAB 仿真平台。必须遵守：
- 代码注释用中文；文件路径严格按任务要求；不要执行真实硬件实验。
- 目标系统：6DOF 离散 UUV，状态 x=[eta(6); nu(6)]，控制 u 为 6 维广义力/力矩。
- 轨迹：3D 八字，x-y 为主，z 有起伏。
- 先跑通 baseline MPC；后续提供 RL 学 P,Q,R,lambda 的接口和可复现实验流程。
- MATLAB 代码需要尽量不依赖专有 toolbox；若 toolbox 不存在，应自动 fallback 到自写求解器/启发式优化器。
- 生成 results/*.mat、figures/*.png，并尽量生成 figures/*.gif 或 *.mp4 动画。
- 不能只写空壳：主脚本至少能用 Octave/MATLAB 语法检查或 dry-run 方式运行；如果本地无 MATLAB，请写 Python/Octave 兼容检查脚本并记录限制。
- 每个任务完成后更新 progress.md，并把关键结果、运行命令、生成文件写清楚。


这是第五轮，也是最终拷打审查。你要像严格 reviewer 一样检查前四轮实现，并直接修复发现的问题。

审查清单：
1. 文件结构是否符合要求：main/models/trajectory/mpc/rl/utils/results/figures/logs。
2. 所有指定函数是否存在，接口是否一致，中文注释是否充分。
3. `run_smoke_tests.m`、`run_baseline_mpc.m`、`run_compare_experiments.m`、`run_rl_leaf_mpc.m` 是否能按顺序运行或 dry-run。
4. 若本地没有 MATLAB/Octave，也要提供 `scripts/check_matlab_project.py` 或类似脚本检查函数/接口/输出文件，并运行它。
5. 检查并补齐 README：说明 baseline、双求解器、RL、动画、结果路径、后续接 PPO 的方式。
6. 生成最终交付清单 `reports/matlab_leaf_mpc_delivery.md`，列出代码框架、实验结果、训练过程、动画文件、已知限制。
7. 确保 progress.md 有最终记录。

如果前面任务有失败或缺文件，你必须自己补齐，不要只报告问题。
