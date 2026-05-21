# RLDMPC-LIT-001 Differentiable MPC with RL-Learned Parameters

## 结论先行
这条文献链的主线很清楚：先用 `OptNet` / 可微优化层把“优化器”变成可训练模块，再由 Amos 等把 `MPC` 变成可微 policy class，随后 `PDP` 把 `PMP`/最优控制梯度也纳入可微框架，最后演化到 `RL` 学习 `MPC` 权重、终端权重、软约束惩罚和残差动力学。

对本文 `LEAF-MPC` 来说，最稳妥的写法不是“RL 直接输出控制量”，而是“RL 输出/调节 `P,Q,R` 和惩罚项，`MPC` 仍负责显式约束下的在线优化”。

## 核心文献表

| 文献 | 来源 | 相关性 | 与 LEAF-MPC 的关系 |
|---|---|---|---|
| Amos & Kolter, *OptNet* | arXiv:1703.00443, ICML 2017 | 背景相关 | 说明“优化层可嵌入神经网络并反向传播”，是可微 `MPC` 的底层思想来源。 |
| Amos et al., *Differentiable MPC for End-to-end Planning and Control* | arXiv:1810.13400, NeurIPS 2018 | 强相关 | 直接奠定“`MPC` 作为可微 policy class”的范式，用 `KKT` 反传学习代价和动力学。 |
| Agrawal et al., *Differentiable Convex Optimization Layers* | arXiv:1910.12430, NeurIPS 2019 | 背景相关 | 给出更通用、工程化的可微凸优化层实现，适合写方法论背景。 |
| Jin et al., *Pontryagin Differentiable Programming* | arXiv:1912.12970, NeurIPS 2020 | 强相关 | 从 `PMP` 角度做可微控制，支持学习动力学、策略和目标函数。 |
| Jin et al., *Safe Pontryagin Differentiable Programming* | arXiv:2105.14937, NeurIPS 2021 | 中等相关 | 强调训练/控制过程中的安全约束满足，可用于“安全学习”段落。 |
| Mehndiratta et al., *Automated Tuning of Nonlinear Model Predictive Controller by Reinforcement Learning* | DOI: `10.1109/iros.2018.8594350` | 强相关 | 早期 `RL` 自动调 `NMPC` 权重的直接证据，且是轨迹跟踪任务。 |
| Bøhn et al., *Optimization of the Model Predictive Control Meta-Parameters Through Reinforcement Learning* | DOI: `10.1016/j.engappai.2023.106211` | 强相关 | 直接把 `RL` 用于优化 `MPC` 元参数，说明学习对象可以是“控制器参数”而非动作。 |
| Bøhn et al., *Reinforcement Learning of the Prediction Horizon in Model Predictive Control* | arXiv:2102.11122 | 中等相关 | 证明 `RL` 也可学习 `MPC` 的结构超参数，但它调的是时域而不是权重。 |
| Mehndiratta et al., *Can Deep Models Help a Robot to Tune Its Controller?* | DOI: `10.3390/electronics10182187` | 中等相关 | 机器人自调权重的证据，强化“先调参、后控制”的路线。 |
| Zarrouki et al., *Weights-varying MPC for Autonomous Vehicle Guidance* | DOI: `10.23919/ECC54610.2021.9655042` | 强相关 | 典型 `RL-WMPC`：`RL` 学习上下文相关权重，而不是直接输出控制输入。 |
| Zarrouki et al., *Safe RL driven Weights-varying MPC* | arXiv:2402.02624 | 强相关 | 用安全动作空间/预优化权重集合约束 `RL`，非常适合安全关键场景。 |
| Romero et al., *Actor-Critic Model Predictive Control* | DOI: `10.1109/TRO.2025.3644945` | 强相关 | 把可微 `MPC` 嵌入 `actor-critic`，兼顾长时域探索和在线重规划。 |
| Tao et al., *DiffTune-MPC: Closed-Loop Learning for Model Predictive Control* | arXiv:2312.11384 | 强相关 | 闭环学习 `MPC` 代价函数，强调解析梯度和 closed-loop 评价之间的匹配。 |
| Jahncke et al., *Differentiable Weights-Varying Nonlinear MPC via Gradient-based Policy Learning* | DOI: `10.1109/LRA.2026.3662644` | 强相关 | 最新、最贴近本文：轻量策略网络根据前视观测输出 `MPC` 权重，并通过 solver-in-the-loop 反传。 |
| Hamadeh et al., *Deep Reinforcement Learning for Tuning of Adaptive MPC for Autonomous Driving* | DOI: `10.1109/iecon58223.2025.11221544` | 中等相关 | `PPO`/`DRL` 调权重与预测时域的邻近工作，可作“PPO + MPC”背景。 |

## 关键公式与思想

`LEAF-MPC` 可写成双层问题：

$$
u_t^*(\theta_t)=\arg\min_{u_{0:H-1}} \sum_{k=0}^{H-1}
\|x_k-x_k^{ref}\|_{Q_t}^2+\|u_k\|_{R_t}^2+\|x_H-x_H^{ref}\|_{P_t}^2+\rho_t\|\xi_k\|^2
$$

subject to

$$
x_{k+1}=f_\phi(x_k,u_k,d_k),\quad g(x_k,u_k)\le 0
$$

外层学习：

$$
\theta_t=\pi_\psi(o_t),\qquad \nabla_\psi \mathcal{L}
=\frac{\partial \mathcal{L}}{\partial u^*}
\frac{\partial u^*}{\partial \theta}
\frac{\partial \theta}{\partial \psi}
$$

若用 `PPO`，外层目标是轨迹回报；若用可微训练，则可直接最小化轨迹损失。工程上，`Q,R,P` 建议用 `softplus`、Cholesky 或投影参数化，保证正定/正值。

## 小节写作要点

- 问题动机：`UUV` 在大机动、高姿态、非平稳扰动下，固定 `MPC` 权重难以兼顾跟踪精度、能耗和鲁棒性。
- 方法核心：`RL` 不直接出控制量，而是根据前视信息输出 `P,Q,R`、终端权重和软约束惩罚，`MPC` 负责显式约束优化。
- 学习变量：优先学对轨迹最敏感的项，例如姿态/速度跟踪权重、控制抑制权重、终端权重、松弛变量惩罚、鲁棒补偿系数。
- 训练目标：轨迹误差、控制平滑性、能耗、约束违背、扰动下恢复速度的加权组合。
- 约束处理：硬约束留在内层 `MPC`；学习层只动权重，不动状态/输入约束；必要时加安全权重集合、正值参数化和不可行回退。
- 与端到端 `RL` 的区别：这里学的是“优化问题的参数化”，不是“动作映射”；因此可解释性、样本效率和安全性都更好。

## 可引用句子

- `MPC` 可以被视为一个可微 policy class，梯度通过 `KKT` 或隐式微分回传到上层学习模块。
- 与直接输出控制输入的端到端 `RL` 不同，`LEAF-MPC` 学习的是 `MPC` 的代价权重与惩罚项，因此能保留显式约束和可解释性。
- 在安全关键场景中，更合适的做法是限制 `RL` 的动作空间，或通过正值参数化确保权重始终可行。
- 对时变工况，使用前视观测驱动的权重调节通常比全局固定权重更稳健。

## 对本文 LEAF-MPC 的启发

- `P,Q,R` 最好做成“上下文相关、但受约束”的输出，而不是无界连续量。
- `UUV` 场景可把海流估计、姿态误差、速度误差、深度变化率、参考曲率/机动强度作为前视输入。
- 若模型失配很强，建议把“残差动力学/扰动估计”与“权重学习”分开，否则学习会把模型误差错误吸收进权重。
- 若 `d-MPC` 反传数值不稳，可采用 `PPO` 学权重，再用可微 `MPC` 做局部 fine-tuning。
- 论文表述上可强调：`LEAF-MPC` 不是替代 `MPC`，而是给 `MPC` 加一个可学习的调参器。

## 不确定之处

- 本次检索未找到直接面向 `UUV` 的“`differentiable MPC + RL 学权重`”一手论文；这里的结论主要从 `UAV`、赛车、自动驾驶与机器人轨迹跟踪文献外推。
- `Diff-WMPC` 的 DOI 和题录来自作者官网/索引页，最终卷期页码建议投稿前再核一次。
- `PPO-MPC` 这类工作主要调预测时域，不是权重学习，只能作为邻近背景，不宜当作核心证据。

## 参考文献

1. Brandon Amos, J. Zico Kolter. *OptNet: Differentiable Optimization as a Layer in Neural Networks*. ICML 2017. https://arxiv.org/abs/1703.00443
2. Brandon Amos, Ivan Dario Jimenez Rodriguez, Jacob Sacks, Byron Boots, J. Zico Kolter. *Differentiable MPC for End-to-end Planning and Control*. NeurIPS 2018. https://arxiv.org/abs/1810.13400
3. Akshay Agrawal, Brandon Amos, Shane Barratt, Stephen Boyd, Steven Diamond, J. Zico Kolter. *Differentiable Convex Optimization Layers*. NeurIPS 2019. https://arxiv.org/abs/1910.12430
4. Wanxin Jin, Zhaoran Wang, Zhuoran Yang, Shaoshuai Mou. *Pontryagin Differentiable Programming: An End-to-End Learning and Control Framework*. NeurIPS 2020. https://arxiv.org/abs/1912.12970
5. Wanxin Jin, Shaoshuai Mou, George J. Pappas. *Safe Pontryagin Differentiable Programming*. NeurIPS 2021. https://arxiv.org/abs/2105.14937
6. Wanxin Jin, Todd D. Murphey, Dana Kulić, Neta Ezer, Shaoshuai Mou. *Learning from Sparse Demonstrations*. https://arxiv.org/abs/2008.02159
7. Mohit Mehndiratta, Efe Camci, Erdal Kayacan. *Automated Tuning of Nonlinear Model Predictive Controller by Reinforcement Learning*. IROS 2018. https://doi.org/10.1109/iros.2018.8594350
8. Eivind Bøhn, Sebastien Gros, Signe Moe, Tor Arne Johansen. *Optimization of the Model Predictive Control Meta-Parameters Through Reinforcement Learning*. Engineering Applications of Artificial Intelligence, 2023. https://doi.org/10.1016/j.engappai.2023.106211
9. Eivind Bøhn, Sebastien Gros, Signe Moe, Tor Arne Johansen. *Reinforcement Learning of the Prediction Horizon in Model Predictive Control*. arXiv:2102.11122. https://arxiv.org/abs/2102.11122
10. Mohit Mehndiratta, Efe Camci, Erdal Kayacan. *Can Deep Models Help a Robot to Tune Its Controller? A Step Closer to Self-Tuning Model Predictive Controllers*. Electronics 2021. https://doi.org/10.3390/electronics10182187
11. Baha Zarrouki, Verena Klos, Nikolas Heppner, Simon Schwan, Robert Ritschel, Rick Voswinkel. *Weights-varying MPC for Autonomous Vehicle Guidance: A Deep Reinforcement Learning Approach*. ECC 2021. https://doi.org/10.23919/ECC54610.2021.9655042
12. Baha Zarrouki, Marios Spanakakis, Johannes Betz. *A Safe Reinforcement Learning driven Weights-varying Model Predictive Control for Autonomous Vehicle Motion Control*. arXiv:2402.02624. https://arxiv.org/abs/2402.02624
13. Angel Romero, Elie Aljalbout, Yunlong Song, Davide Scaramuzza. *Actor-Critic Model Predictive Control: Differentiable Optimization Meets Reinforcement Learning for Agile Flight*. IEEE Transactions on Robotics, 2025/2026. https://doi.org/10.1109/TRO.2025.3644945
14. Ran Tao, Sheng Cheng, Xiaofeng Wang, Shenlong Wang, Naira Hovakimyan. *DiffTune-MPC: Closed-Loop Learning for Model Predictive Control*. arXiv:2312.11384. https://arxiv.org/abs/2312.11384
15. Felix Jahncke, Baha Zarrouki, Mattia Piccinini, Jovin D'Sa, David Isele, Sangjae Bae, Johannes Betz. *Differentiable Weights-Varying Nonlinear MPC via Gradient-based Policy Learning: An Autonomous Vehicle Guidance Example*. IEEE RA-L 2026. https://doi.org/10.1109/LRA.2026.3662644
16. Feras Hamadeh, Anas Abdelkarim, Amar Hamadeh, Daniel Görges, Holger Voos. *Deep Reinforcement Learning for Tuning of Adaptive Model Predictive Control for Autonomous Driving*. IEEE IECON 2025. https://doi.org/10.1109/iecon58223.2025.11221544
