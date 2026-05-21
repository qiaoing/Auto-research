# LEAF-MPC MATLAB 仿真平台

本目录用于验证 **6DOF UUV + RL 可微 MPC/LEAF-MPC** 在三维大机动八字轨迹跟踪任务中的性能。

## 目录

```text
main/        主入口：baseline、RL、对比实验、smoke tests
models/      6DOF 离散 UUV 模型
trajectory/  3D 八字参考轨迹
mpc/         自写 MPC、MATLAB toolbox/fallback 求解器、代价/约束
rl/          RL 观测、动作到权重、奖励、训练循环
utils/       绘图、指标、动画、保存结果
tests/       MATLAB/Octave 风格测试脚本
results/     .mat 结果
figures/     .png/.gif/.mp4 图表动画
logs/        运行日志
```

## 推荐运行顺序

在 MATLAB 或 Octave 中进入仓库根目录后运行：

```matlab
cd matlab/leaf_mpc
addpath(genpath(pwd));
main.run_smoke_tests        % 或 run('main/run_smoke_tests.m')
run('main/run_baseline_mpc.m')
run('main/run_compare_experiments.m')
run('main/run_rl_leaf_mpc.m')
```

如无 MATLAB/Octave，可运行仓库侧验证脚本：

```bash
python3 scripts/validate_leaf_mpc_matlab.py
```

Python 验证脚本会检查文件完整性，并生成一组可复现的基线/对比/RL 训练示例结果，用于 CI 和论文图表管线打通。正式论文数值请以 MATLAB/Octave 闭环运行结果为准。

## 状态与接口约定

- 状态：`x = [eta; nu]`，其中 `eta=[x;y;z;phi;theta;psi]`，`nu=[u;v;w;p;q;r]`。
- 控制：`u` 为 6 维广义力/力矩。
- 模型接口：`x_next = uuv_model_step(x,u,params,disturbance)`。
- 轨迹接口：`ref = traj_fig8_3d(t,cfg)`，包含 `pos/vel/acc/yaw_ref/x_ref`。
- MPC 求解器统一接口：`[u_opt, info] = mpc_solve(xk, refSeq, weights, constraints, model, config)`。
- RL 动作：低维向量经 softplus 映射为 `P,Q,R,lambda` 的对角缩放。

## 设计说明

当前版本优先保证平台闭环、接口稳定和输出完整；自写 MPC 使用有限候选/启发式滚动优化作为 toolbox-free baseline，MATLAB toolbox 入口会在缺失工具箱时自动 fallback 到自写求解器。后续可将 `mpc_solver_custom.m` 替换为可微 QP/NLP 求解器，并把 `rl_train_loop.m` 替换为 PPO 更新。 
