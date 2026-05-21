# LEAF-MPC MATLAB 平台：RL 学 P,Q,R,lambda 接口、训练日志、动画


你是本地 Codex，正在为 LEAF-MPC 论文实现 MATLAB 仿真平台。必须遵守：
- 代码注释用中文；文件路径严格按任务要求；不要执行真实硬件实验。
- 目标系统：6DOF 离散 UUV，状态 x=[eta(6); nu(6)]，控制 u 为 6 维广义力/力矩。
- 轨迹：3D 八字，x-y 为主，z 有起伏。
- 先跑通 baseline MPC；后续提供 RL 学 P,Q,R,lambda 的接口和可复现实验流程。
- MATLAB 代码需要尽量不依赖专有 toolbox；若 toolbox 不存在，应自动 fallback 到自写求解器/启发式优化器。
- 生成 results/*.mat、figures/*.png，并尽量生成 figures/*.gif 或 *.mp4 动画。
- 不能只写空壳：主脚本至少能用 Octave/MATLAB 语法检查或 dry-run 方式运行；如果本地无 MATLAB，请写 Python/Octave 兼容检查脚本并记录限制。
- 每个任务完成后更新 progress.md，并把关键结果、运行命令、生成文件写清楚。


这是第四轮，请在已有 MPC 平台上加入 RL 参数学习框架。可以先实现轻量级、可复现的代理训练循环，不要求真正 PPO 完整收敛，但接口必须为后续 PPO/强化学习工具箱可替换。

必须实现：
1. `rl/rl_observation.m`：观测包括 e、de、当前速度 nu、上一控制量 u_prev、约束活跃信息、跟踪质量指标。
2. `rl/rl_action_to_weights.m`：动作映射到 P,Q,R,lambda，使用对角缩放/softplus 或 exp 保证正权重。
3. `rl/rl_reward.m`：实现 r=-alpha_e||e||^2-alpha_u||u||^2-alpha_du||du||^2-alpha_c Gamma。
4. `rl/rl_train_loop.m`：可复现训练循环，至少支持随机策略/简化策略梯度/启发式搜索，记录 reward、权重变化、最佳权重。
5. `main/run_rl_leaf_mpc.m`：使用训练得到的权重或启发式权重运行 RL-MPC/LEAF-MPC 对比。
6. `utils/animate_uuv_3d.m`：输出 GIF 或 MP4/逐帧图片；函数名必须存在。
7. 生成 reward 曲线、权重变化曲线、baseline vs RL-MPC 对比图。

输出：
- `results/rl_training_log.mat`
- `results/rl_leaf_mpc_result.mat`
- `figures/rl_reward_curve.png`
- `figures/rl_weight_evolution.png`
- `figures/baseline_vs_rl_3d.png`
- `figures/uuv_3d_animation.gif` 或 `figures/uuv_3d_animation.mp4` 或 frames。

验收：
- RL 接口不是空壳，能输出 P/Q/R/lambda。
- 训练过程可复现，固定随机种子。
- 动画函数能处理 result/trajRef。
- 更新 progress.md。
