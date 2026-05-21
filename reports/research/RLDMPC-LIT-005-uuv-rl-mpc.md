# RLDMPC-LIT-005：UUV 场景下 RL-Learned Differentiable MPC Parameters 专题调研

## 1. 结论先行

- 对于论文小节“Differentiable MPC with RL-Learned Parameters”，当前最稳妥的文献叙事不是“RL 直接输出推进器/舵机控制量”，而是“RL 输出或调节 MPC 的代价参数、终端权重、控制权重、软约束惩罚与鲁棒补偿系数，而实际控制输入仍由带显式约束的 MPC 在线求解得到”。
- 已核验英文文献能够强力支撑三条技术主线：
  1. `differentiable MPC / policy gradient through MPC`
  2. `RL/DRL/PPO 调 MPC 权重或元参数`
  3. `UUV/AUV 在模型失配、海流扰动、输入约束下的 MPC 轨迹跟踪`
- 暂未找到“直接面向 UUV 高速大姿态大机动轨迹跟踪，且显式使用 PPO + differentiable MPC 学习完整 P/Q/R”的成熟一手论文。当前最强证据来自 UAV、自动驾驶、通用机器人轨迹跟踪与 UUV 鲁棒 MPC 文献的组合外推。
- 因此，本文 LEAF-MPC 的文献定位应写成：
  “面向 UUV 大机动轨迹跟踪，将 RL 作为高层参数调度器，学习状态/前视上下文相关的 MPC 权重与惩罚项；将可微 MPC 作为可解释、可约束、可在线重规划的低层优化器。”

## 2. 核心文献表

### 2.1 方法链核心文献

| 相关性 | 文献 | 核验来源 | 关系标签 | 与 LEAF-MPC 的关系 |
|---|---|---|---|---|
| 强相关 | Brandon Amos et al., *Differentiable MPC for End-to-end Planning and Control*, NeurIPS 2018, [arXiv:1810.13400](https://arxiv.org/abs/1810.13400) | NeurIPS 页面已核验 | `differentiable MPC` `policy gradient through MPC` | 直接提出将 MPC 视为可微 policy class，可通过 KKT/隐式微分回传梯度到成本项和动力学参数，是 LEAF-MPC 可微训练叙事的基础。 |
| 强相关 | Angel Romero, Yunlong Song, Davide Scaramuzza, *Actor-Critic Model Predictive Control*, ICRA 2024, DOI: [10.1109/ICRA57147.2024.10610381](https://doi.org/10.1109/ICRA57147.2024.10610381), [arXiv:2306.09852](https://arxiv.org/abs/2306.09852) | ICRA PDF 与 DOI 已核验 | `PPO + MPC` `diffMPC actor` `learn cost map` | 该文把可微 MPC 放在 actor 最后一层，训练时明确使用 PPO；学习对象不是直接控制量，而是 MPC 的神经 cost map，和 LEAF-MPC 的“RL 学参数，MPC 出控制”最接近。 |
| 强相关 | Mohit Mehndiratta et al., *Automated Tuning of Nonlinear Model Predictive Controller by Reinforcement Learning*, IROS 2018, DOI: [10.1109/IROS.2018.8594350](https://doi.org/10.1109/IROS.2018.8594350) | AU Pure 页面已核验 | `RL tuning NMPC weights` `trajectory tracking` | 早期直接证据：RL 自动搜索 NMPC 权重，任务就是轨迹跟踪。可直接支撑“RL 调 MPC 权重，而非直接输出控制输入”。 |
| 强相关 | Mohit Mehndiratta et al., *Can Deep Models Help a Robot to Tune Its Controller? A Step Closer to Self-Tuning Model Predictive Controllers*, *Electronics*, 2021, DOI: [10.3390/electronics10182187](https://doi.org/10.3390/electronics10182187) | 期刊页面已核验 | `self-tuning MPC` `learn weight set` | 强化了“先学习调参器，再保留 MPC 控制器”的路线，强调权重调节与 sim-to-real 过渡。 |
| 强相关 | Eivind Bøhn et al., *Optimization of the Model Predictive Control Meta-Parameters Through Reinforcement Learning*, *Engineering Applications of Artificial Intelligence*, 2023, DOI: [10.1016/j.engappai.2023.106211](https://doi.org/10.1016/j.engappai.2023.106211), [arXiv:2111.04146](https://arxiv.org/abs/2111.04146) | arXiv 与期刊 PDF 条目已核验 | `RL tunes MPC meta-parameters` `state-dependent tuning` | 虽然重点不只在 Q/R，而是广义元参数，但它证明了 RL 可学的是 MPC 结构与调度参数，而不是控制动作本身。 |
| 强相关 | Baha Zarrouki et al., *A Safe Reinforcement Learning driven Weights-varying Model Predictive Control for Autonomous Vehicle Motion Control*, [arXiv:2402.02624](https://arxiv.org/abs/2402.02624) | arXiv 已核验 | `safe RL with MPC` `weights-varying MPC` | 用安全权重库/离散权重动作替代连续任意权重探索，非常适合 LEAF-MPC 处理 UUV 安全约束与训练期不可行权重问题。 |
| 强相关 | Felix Jahncke et al., *Differentiable Weights-Varying Nonlinear MPC via Gradient-Based Policy Learning: An Autonomous Vehicle Guidance Example*, *IEEE RA-L*, 2026, DOI: [10.1109/LRA.2026.3662644](https://doi.org/10.1109/LRA.2026.3662644) | TUM 页面与项目页已核验 | `differentiable weights-varying MPC` `learn q,r` | 当前最贴近 LEAF-MPC 的结构：轻量策略网络根据 look-ahead context 输出 MPC 权重，并通过 solver sensitivities 反传。 |
| 强相关 | Feras Hamadeh et al., *Deep Reinforcement Learning for Tuning of Adaptive Model Predictive Control for Autonomous Driving*, IECON 2025, DOI: [10.1109/IECON58223.2025.11221544](https://doi.org/10.1109/IECON58223.2025.11221544) | 机构仓储页与 DOI 已核验 | `PPO + MPC` `weight + horizon tuning` | 明确写到用 PPO 和 DDPG 在线调代价权重与 prediction horizon，可作为“增强 PPO 调 MPC 参数”的直接邻近证据。 |
| 强相关 | Ran Tao et al., *DiffTune-MPC: Closed-Loop Learning for Model Predictive Control*, [arXiv:2312.11384](https://arxiv.org/abs/2312.11384) | arXiv 已核验 | `closed-loop learning` `learn MPC cost` | 不是 RL，但非常关键：它直指“为何要按闭环性能而非开环优化目标去学习 MPC 代价参数”，可支撑 LEAF-MPC 的训练目标设计。 |
| 中等相关 | Brandon Amos, J. Zico Kolter, *OptNet: Differentiable Optimization as a Layer in Neural Networks*, ICML 2017, [PMLR](https://proceedings.mlr.press/v70/amos17a.html), [arXiv:1703.00443](https://arxiv.org/abs/1703.00443) | PMLR 已核验 | `differentiable optimization layer` | 是可微优化层的一般性起点，但不专门针对 MPC。适合 related work 的理论背景。 |
| 中等相关 | Wanxin Jin et al., *Pontryagin Differentiable Programming*, NeurIPS 2020, [NeurIPS](https://proceedings.neurips.cc/paper/2020/hash/5a7b238ba0f6502e5d6be14424b20ded-Abstract.html), [arXiv:1912.12970](https://arxiv.org/abs/1912.12970) | NeurIPS 已核验 | `differentiable optimal control` | 从 PMP 角度说明“学习动力学/策略/目标函数”是可行的，可作 LEAF-MPC 方法论背景。 |
| 中等相关 | Wanxin Jin et al., *Safe Pontryagin Differentiable Programming*, NeurIPS 2021, [NeurIPS](https://proceedings.neurips.cc/paper/2021/hash/85ea6fd7a2ca3960d0cf5201933ac998-Abstract.html), [arXiv:2105.14937](https://arxiv.org/abs/2105.14937) | NeurIPS 已核验 | `safe differentiable control` | 说明约束可通过 barrier 风格进入可微学习框架，但它不是 MPC 权重学习文献。 |
| 中等相关 | Lukas P. Fröhlich et al., *Contextual Tuning of Model Predictive Control for Autonomous Racing*, IROS 2022, DOI: [10.1109/IROS47612.2022.9981780](https://doi.org/10.1109/IROS47612.2022.9981780), [arXiv:2110.02710](https://arxiv.org/abs/2110.02710) | ETH 研究库与 DOI 已核验 | `context-dependent tuning` | 不是 RL，而是 contextual BO；但它强力支持“工况变化时，MPC 权重应随上下文自适应变化”。 |
| 背景相关 | Lukas Hewing et al., *Learning-Based Model Predictive Control: Toward Safe Learning in Control*, *Annual Review of Control, Robotics, and Autonomous Systems*, 2020, DOI: [10.1146/annurev-control-090419-075625](https://doi.org/10.1146/annurev-control-090419-075625) | Annual Reviews 已核验 | `survey` `safe learning` | 系统综述，可用于给 LEAF-MPC 在“learning-based MPC”谱系中定位。 |
| 背景相关 | Lukas Brunke et al., *Safe Learning in Robotics: From Learning-Based Control to Safe Reinforcement Learning*, *Annual Review of Control, Robotics, and Autonomous Systems*, 2022, DOI: [10.1146/annurev-control-042920-020211](https://doi.org/10.1146/annurev-control-042920-020211) | Annual Reviews 已核验 | `safe RL` `robotics` | 有助于说明为何安全关键机器人更适合“学习调参 + 显式约束控制”的混合路线。 |

### 2.2 UUV/AUV/MPC/扰动抑制背景文献

| 相关性 | 文献 | 核验来源 | 关系标签 | 与 LEAF-MPC 的关系 |
|---|---|---|---|---|
| 强相关 | Chao Shen, Yang Shi, Brad Buckham, *Trajectory Tracking Control of an Autonomous Underwater Vehicle Using Lyapunov-Based Model Predictive Control*, *IEEE Transactions on Industrial Electronics*, 2018, DOI: [10.1109/TIE.2017.2779442](https://doi.org/10.1109/TIE.2017.2779442) | DOI 由交叉引用链核验，未直接打开 IEEE 页面 | `AUV trajectory tracking` `Lyapunov MPC` | UUV/AUV 轨迹跟踪中较经典的 MPC 稳定性文献，可支撑“约束 + 稳定性 + 大机动跟踪”的场景动机。 |
| 强相关 | Zheping Yan et al., *Model predictive control of autonomous underwater vehicles for trajectory tracking with external disturbances*, *Ocean Engineering*, 2020, DOI: [10.1016/j.oceaneng.2020.107884](https://doi.org/10.1016/j.oceaneng.2020.107884) | ScienceDirect 已核验 | `AUV MPC` `external disturbances` | 直接针对外扰下 AUV 轨迹跟踪，说明固定 MPC 结构已能处理约束与扰动，但仍依赖手工权重设计。 |
| 强相关 | Peng Gong et al., *Lyapunov-based model predictive control trajectory tracking for an autonomous underwater vehicle with external disturbances*, *Ocean Engineering*, 2021, DOI: [10.1016/j.oceaneng.2021.109010](https://doi.org/10.1016/j.oceaneng.2021.109010) | ScienceDirect 已核验 | `AUV LMPC` `disturbance rejection` | 在外扰环境中进一步引入 Lyapunov/contraction 约束，说明 UUV 场景需要“稳定性增强的 MPC”，非常适合作为 RL 学终端权重/收缩惩罚的背景。 |
| 强相关 | Chao Shen, Yang Shi, *Distributed implementation of nonlinear model predictive control for AUV trajectory tracking*, *Automatica*, 2020, DOI: [10.1016/j.automatica.2020.108863](https://doi.org/10.1016/j.automatica.2020.108863) | 元数据页已核验 | `NMPC for AUV` `trajectory tracking` | 说明 AUV NMPC 的实时实现难点，支持 LEAF-MPC 将学习层放在“低维权重调度”而非全量在线重构。 |
| 强相关 | Shahab Heshmati-Alamdari et al., *A Robust Predictive Control Approach for Underwater Robotic Vehicles*, *IEEE Transactions on Control Systems Technology*, 2020, DOI: [10.1109/TCST.2019.2939248](https://doi.org/10.1109/TCST.2019.2939248) | 大学研究门户已核验 | `robust NMPC` `underwater robots` | 强调约束工作空间、海流利用与鲁棒性保证，适合作为“模型失配和扰动下仍需显式约束”的背景。 |
| 强相关 | *Robust MPC-based trajectory tracking of autonomous underwater vehicles with model uncertainty*, 2023, DOI: [10.1016/j.oceaneng.2023.115617](https://doi.org/10.1016/j.oceaneng.2023.115617) | ScienceDirect 条目已核验 | `tube MPC` `model uncertainty` | 说明 UUV 轨迹跟踪的核心难点是模型不确定性与随机扰动，与 LEAF-MPC 动机高度一致。作者信息未在本次检索中完整展开。 |
| 强相关 | Jaime Arcos-Legarda, Álvaro Gutiérrez, *Disturbance Observer-Based Model Predictive Control for an Unmanned Underwater Vehicle*, *Journal of Marine Science and Engineering*, 2024, DOI: [10.3390/jmse12010094](https://doi.org/10.3390/jmse12010094) | 期刊页已核验 | `DOB + MPC` `parametric uncertainty` | 明确把预测模型中的未建模参数视作扰动项处理，和 LEAF-MPC 中“鲁棒补偿/残差校正”很契合。 |
| 强相关 | Wei Zhang et al., *Real-time NMPC for three-dimensional trajectory tracking control of AUV with disturbances*, *Ocean Engineering*, 2025, DOI: [10.1016/j.oceaneng.2024.120267](https://doi.org/10.1016/j.oceaneng.2024.120267) | ScienceDirect 已核验 | `real-time NMPC` `AUV disturbances` | 直接面对 3D 轨迹跟踪与扰动，说明在线求解效率仍是痛点，支持 LEAF-MPC 采用低维参数学习而非直接学控制律。 |
| 中等相关 | Shahab Heshmati-Alamdari et al., *Robust Trajectory Tracking Control for Underactuated Autonomous Underwater Vehicles in Uncertain Environments*, *IEEE Transactions on Automation Science and Engineering*, 2021, DOI: [10.1109/TASE.2020.3001183](https://doi.org/10.1109/TASE.2020.3001183) | DOI 索引页已核验 | `robust tracking` `uncertain environments` | 不是 MPC，但强力支撑 UUV 轨迹跟踪对不确定性和环境扰动的敏感性。 |
| 中等相关 | *Tube-based model predictive control of an autonomous underwater vehicle using line-of-sight re-planning*, 2024, DOI: [10.1016/j.oceaneng.2024.119688](https://doi.org/10.1016/j.oceaneng.2024.119688) | ScienceDirect 条目已核验 | `tube MPC` `input saturation` | 强调 tube MPC 与安全轨迹重规划，适合相关工作扩展，但与 RL 学参数无直接关系。 |
| 中等相关 | *MPC-based 3-D trajectory tracking for an autonomous underwater vehicle with constraints in complex ocean environments*, *Ocean Engineering*, 2019, DOI: [10.1016/j.oceaneng.2019.106309](https://doi.org/10.1016/j.oceaneng.2019.106309) | Worktribe/ScienceDirect 条目已核验 | `constraint handling` `AUV MPC` | 明确考虑输入和状态约束，是 LEAF-MPC 内层 MPC 保留硬约束的直接场景背景。 |
| 中等相关 | *Trajectory tracking control of vectored thruster autonomous underwater vehicles based on deep reinforcement learning*, *Ships and Offshore Structures*, 2024, DOI: [10.1080/17445302.2024.2391235](https://doi.org/10.1080/17445302.2024.2391235) | Taylor & Francis 页面已核验 | `end-to-end RL` `AUV tracking` | 可作为对照：它代表端到端 RL 直接学控制策略，而 LEAF-MPC 则保留 MPC 优化器，只学习其参数。 |
| 背景相关 | *Dynamic Target Tracking of Autonomous Underwater Vehicle Based on Deep Reinforcement Learning*, *Journal of Marine Science and Engineering*, 2022, DOI: [10.3390/jmse10101406](https://doi.org/10.3390/jmse10101406) | 期刊页已核验 | `AUV DRL tracking` | 适合用来对比“纯 RL 能做跟踪，但约束可解释性较弱”。 |
| 背景相关 | A.M. Eissa et al., *Trajectory tracking control of autonomous underwater vehicles: a review from classical methods to AI-based approaches*, *International Journal of Dynamics and Control*, 2025, DOI 待投稿版本外部核验 | Springer 页面已核验到期刊条目 | `review` `AUV tracking` | 综述价值高，但本次未继续追 DOI 细节，可作为背景补充，不宜当核心证据。 |

## 3. 关键公式与关键思想

### 3.1 推荐写成的双层结构

令外层学习器输出 MPC 参数化向量

$$
\theta_t = \pi_{\psi}(o_t),
\qquad
\theta_t=\{Q_t,R_t,P_t,\rho_t,\lambda_t,\dots\},
$$

其中 `o_t` 可包含当前跟踪误差、速度误差、姿态误差、估计海流、扰动观测器输出、参考轨迹前视曲率/俯仰变化率/航向变化率、以及约束余量。

内层 MPC 求解

$$
\mathbf{u}_{t:t+H-1}^*(\theta_t)
=
\arg\min_{\mathbf{u},\boldsymbol{\xi}}
\sum_{k=0}^{H-1}
\|x_{t+k}-x^{\mathrm{ref}}_{t+k}\|_{Q_t}^2
+\|u_{t+k}\|_{R_t}^2
+\|x_{t+H}-x_{t+H}^{\mathrm{ref}}\|_{P_t}^2
\,+\,\rho_t\|\xi_{t+k}\|^2
\,+\,\lambda_t\Phi_{\mathrm{rob}}(x_{t+k},u_{t+k},\hat d_{t+k}),
$$

subject to

$$
\begin{aligned}
x_{t+k+1} &= f_{\hat\phi}(x_{t+k},u_{t+k},\hat d_{t+k}),\\
g(x_{t+k},u_{t+k}) &\le \xi_{t+k},\quad \xi_{t+k}\ge 0,\\
u_{\min}\le u_{t+k}\le u_{\max},\quad x_{t+k}\in\mathcal{X}.
\end{aligned}
$$

执行量为首个控制量

$$
u_t = u_t^*(\theta_t).
$$

### 3.2 若采用可微 MPC 的梯度训练

则闭环损失关于外层参数的梯度可写为

$$
\nabla_{\psi}\mathcal{J}
=
\frac{\partial \mathcal{J}}{\partial u_t^*}
\frac{\partial u_t^*}{\partial \theta_t}
\frac{\partial \theta_t}{\partial \psi}.
$$

这里的关键不是“RL 直接输出动作”，而是“动作对权重参数的敏感度可通过可微 MPC 求得”。这正是 Amos 2018、Romero 2024、Jahncke 2026 的共同主线。

### 3.3 若采用 PPO 外层训练

可以把 `PPO` 的动作定义为权重参数而非控制输入：

$$
a_t=\theta_t=\pi_{\psi}(o_t), \qquad u_t=\mathrm{MPC}(x_t;\theta_t).
$$

对应 PPO surrogate 可写为

$$
\mathcal{L}_{\mathrm{PPO}}(\psi)
=
\mathbb{E}\Big[
\min\big(
 r_t(\psi)\hat A_t,\,
 \mathrm{clip}(r_t(\psi),1-\epsilon,1+\epsilon)\hat A_t
\big)
\Big]
-\beta \mathcal{L}_{\mathrm{viol}}
-\gamma \mathcal{L}_{\mathrm{energy}}.
$$

其中 `\mathcal{L}_{viol}` 可聚合软约束、饱和、姿态越界、求解失败等惩罚。

### 3.4 正定性与可行性参数化

若论文打算写“学习 P/Q/R”，建议不要写成完全无结构 full matrix 自由输出，更稳妥的是

$$
Q_t = \mathrm{diag}(\mathrm{softplus}(w_t^Q)+\varepsilon_Q),\quad
R_t = \mathrm{diag}(\mathrm{softplus}(w_t^R)+\varepsilon_R),\quad
P_t = \mathrm{diag}(\mathrm{softplus}(w_t^P)+\varepsilon_P),
$$

或

$$
Q_t=L_tL_t^\top+\varepsilon I.
$$

这与已核验的强相关文献趋势一致：多数工作学的是结构化权重、低维 cost vector、cost map 或安全权重集，而不是任意稠密全矩阵。

## 4. 论文小节可直接使用的写作要点

### 4.1 问题动机

- UUV 高速、大姿态、大机动轨迹跟踪下，固定 MPC 权重难以同时兼顾位置/姿态误差收敛、控制能耗、控制平滑性、约束满足与扰动恢复速度。
- 海流、附体扰动、流体参数偏差和执行器工况变化使得最优权重在不同机动阶段并不恒定。
- 因此，与其放弃 MPC，不如学习一个“上下文相关的 MPC 调参器”，让其根据当前状态与前视轨迹动态调节权重。

### 4.2 方法公式

- 外层 `RL/PPO` 输出 `Q/R/P` 的对角权重、终端权重、软约束惩罚、鲁棒补偿系数等低维参数。
- 内层 `differentiable MPC` 或常规 NMPC 保持动力学约束、输入/状态约束与滚动优化。
- 若求解器支持灵敏度，则可用 solver-in-the-loop 梯度对学习层微调；若数值稳定性不足，可先用 PPO 闭环训练，再做少量可微 fine-tuning。

### 4.3 学习变量

- 建议优先学习：
  `位置误差权重`、`姿态误差权重`、`速度误差权重`、`控制量权重`、`控制增量权重`、`终端权重`、`软约束惩罚`、`扰动补偿/鲁棒项系数`。
- 对 UUV 更可解释的做法是输出分组标量，而不是完整矩阵：
  `位置块`、`姿态块`、`线速度块`、`角速度块`、`执行器块`、`终端块`、`约束块`、`鲁棒块`。

### 4.4 训练目标

- 应按闭环性能而非仅按单步 MPC stage cost 训练。
- 推荐综合指标：
  `轨迹误差`、`姿态稳定性`、`控制能耗`、`控制抖振/变化率`、`约束违反量`、`恢复时间`、`终端误差`、`求解失败率`。
- `DiffTune-MPC` 的直接启发是：学习目标应对齐最终评价指标，避免“开环 cost 看起来好，但闭环表现不优”的错配。

### 4.5 约束处理

- 硬输入约束、状态约束、速率约束应保留在 MPC 内层，不建议让 RL 直接绕开约束生成控制动作。
- 可通过 slack 变量处理软约束，并令其惩罚系数可学习，但须保持正值且有下界。
- 若担心训练期出现危险权重，可采用：
  `权重投影`、`安全权重库`、`离散 Pareto 权重集`、`barrier/penalty`、`求解失败回退策略`。

### 4.6 与端到端 RL 的区别

- 端到端 RL 学的是 `o_t \mapsto u_t`。
- LEAF-MPC 学的是 `o_t \mapsto \theta_t \mapsto u_t^*`。
- 因而 LEAF-MPC 保留了：
  `显式约束`、`在线重规划`、`物理可解释性`、`更强的安全性结构`。
- 同时，它利用 RL 处理：
  `模型失配`、`时变扰动`、`机动阶段切换`、`代价偏好自适应`。

## 5. 可引用句子

以下句子为“可直接写入论文的归纳性表述”，不是文献原文直引：

- 可微 MPC 使闭环性能关于代价参数的敏感度能够通过优化器显式回传，从而将 MPC 权重学习转化为可训练的参数化控制问题。
- 与端到端强化学习直接输出控制输入不同，LEAF-MPC 仅学习 MPC 的权重参数和惩罚系数，而实际控制指令仍由带约束的在线优化器生成。
- 对于大机动轨迹跟踪任务，固定 MPC 权重难以在跟踪精度、控制平滑性、能耗和扰动抑制之间持续维持最优折中，因此需要上下文相关的自适应权重调度机制。
- 在安全关键机器人系统中，将强化学习限制在 MPC 参数空间内，而非直接绕过优化器生成动作，更有利于保留显式约束满足能力与工程可解释性。
- 面对模型失配和非平稳扰动，学习层的核心作用不是替代 MPC，而是在不同机动阶段动态重分配跟踪误差、控制 effort 与鲁棒性之间的权衡。
- 现有强相关文献普遍表明，相比直接学习完整稠密 P/Q/R，学习结构化对角权重、低维权重向量或安全权重集通常更稳定、更易解释，也更利于在线部署。

## 6. 对 LEAF-MPC 的具体启发

- 不建议一开始就让 PPO 输出完整 full `P/Q/R`。更稳妥的是输出结构化低维权重向量，再映射为对角或块对角矩阵。
- RL 观测建议显式加入前视机动信息，而不是只输入当前误差。可包含：
  `未来若干步曲率`、`期望航向变化率`、`期望俯仰变化率`、`参考速度变化`、`海流估计`、`扰动观测器输出`、`姿态误差`、`速度误差`、`约束余量`。
- 若模型失配显著，建议把“残差动力学/扰动估计”和“代价权重学习”分开设计：
  前者修正预测模型，后者调 tracking-effort-robustness trade-off。
- 可将鲁棒补偿项写为可学习系数 `\lambda_t`，但不建议让 RL 直接修改物理约束边界。
- 若可微求解器的数值稳定性有限，可以采用“两阶段训练”叙事：
  先用 PPO 学出鲁棒权重调度策略，再在仿真中使用 differentiable MPC 做局部梯度细化。
- 对 UUV 论文叙事最关键的一句应是：
  “LEAF-MPC 不是用 RL 替代 MPC，而是用 RL 学习不同工况下应如何重配置 MPC 的最优性偏好与约束惩罚。”

## 7. 不确定性与边界说明

- **强不确定项 1**：本次未核验到“UUV + differentiable MPC + PPO 学 P/Q/R”这一完全同构的一手英文论文。因此，LEAF-MPC 的论证应采用“方法链 + 场景链”组合支撑，而不是声称已有同类 UUV 成熟工作。
- **强不确定项 2**：Shen et al. 2018 的 DOI `10.1109/TIE.2017.2779442` 来自多处交叉引用链，未直接打开 IEEE Xplore 页面。该条可用，但正式投稿前建议再做一次 IEEE 官方核验。
- **中等不确定项 1**：`DiffTune-MPC` 目前本次核验到的是 arXiv 版本；适合支持方法论，不宜表述成已完全定版的期刊论文。
- **中等不确定项 2**：`Safe RL-WMPC` 当前核验到的是 arXiv 预印本；适合支撑安全权重学习思想，但应标注为预印本。
- **中等不确定项 3**：`Robust MPC-based trajectory tracking of autonomous underwater vehicles with model uncertainty` 已核验 DOI 与主题，但作者完整元数据未在本次检索中展开，不宜在正文里过度依赖作者细节。
- **边界建议**：若本文算法实际上只学习对角元素、若干标量权重或块权重，应在论文里明确写“structured P/Q/R parameterization”，不要笼统写“learn full P,Q,R matrices”。

## 8. 参考文献列表

1. Amos, B., Kolter, J. Z. *OptNet: Differentiable Optimization as a Layer in Neural Networks*. ICML 2017. PMLR: <https://proceedings.mlr.press/v70/amos17a.html>
2. Amos, B., Jimenez Rodriguez, I. D., Sacks, J., Boots, B., Kolter, J. Z. *Differentiable MPC for End-to-end Planning and Control*. NeurIPS 2018. <https://arxiv.org/abs/1810.13400>
3. Jin, W., Wang, Z., Yang, Z., Mou, S. *Pontryagin Differentiable Programming: An End-to-End Learning and Control Framework*. NeurIPS 2020. <https://arxiv.org/abs/1912.12970>
4. Jin, W., Mou, S., Pappas, G. J. *Safe Pontryagin Differentiable Programming*. NeurIPS 2021. <https://arxiv.org/abs/2105.14937>
5. Mehndiratta, M., Camci, E., Kayacan, E. *Automated Tuning of Nonlinear Model Predictive Controller by Reinforcement Learning*. IROS 2018. DOI: <https://doi.org/10.1109/IROS.2018.8594350>
6. Mehndiratta, M., Camci, E., Kayacan, E. *Can Deep Models Help a Robot to Tune Its Controller? A Step Closer to Self-Tuning Model Predictive Controllers*. *Electronics*, 2021. DOI: <https://doi.org/10.3390/electronics10182187>
7. Bøhn, E., Gros, S., Moe, S., Johansen, T. A. *Optimization of the Model Predictive Control Meta-Parameters Through Reinforcement Learning*. *Engineering Applications of Artificial Intelligence*, 2023. DOI: <https://doi.org/10.1016/j.engappai.2023.106211>
8. Romero, A., Song, Y., Scaramuzza, D. *Actor-Critic Model Predictive Control*. ICRA 2024. DOI: <https://doi.org/10.1109/ICRA57147.2024.10610381>
9. Tao, R., Cheng, S., Wang, X., Wang, S., Hovakimyan, N. *DiffTune-MPC: Closed-Loop Learning for Model Predictive Control*. arXiv 2023. <https://arxiv.org/abs/2312.11384>
10. Zarrouki, B., Spanakakis, M., Betz, J. *A Safe Reinforcement Learning driven Weights-varying Model Predictive Control for Autonomous Vehicle Motion Control*. arXiv 2024. <https://arxiv.org/abs/2402.02624>
11. Hamadeh, F., Abdelkarim, A., Hamadeh, A., Gorges, D., Voos, H. *Deep Reinforcement Learning for Tuning of Adaptive Model Predictive Control for Autonomous Driving*. IECON 2025. DOI: <https://doi.org/10.1109/IECON58223.2025.11221544>
12. Jahncke, F., Zarrouki, B., Piccinini, M., D'Sa, J., Isele, D., Bae, S., Betz, J. *Differentiable Weights-Varying Nonlinear MPC via Gradient-Based Policy Learning: An Autonomous Vehicle Guidance Example*. *IEEE Robotics and Automation Letters*, 2026. DOI: <https://doi.org/10.1109/LRA.2026.3662644>
13. Fröhlich, L. P., Küttel, C., Arcari, E., Hewing, L., Zeilinger, M. N., Carron, A. *Contextual Tuning of Model Predictive Control for Autonomous Racing*. IROS 2022. DOI: <https://doi.org/10.1109/IROS47612.2022.9981780>
14. Hewing, L., Wabersich, K. P., Menner, M., Zeilinger, M. N. *Learning-Based Model Predictive Control: Toward Safe Learning in Control*. *Annual Review of Control, Robotics, and Autonomous Systems*, 2020. DOI: <https://doi.org/10.1146/annurev-control-090419-075625>
15. Brunke, L., Greeff, M., Hall, A. W., Yuan, Z., Zhou, S., Panerati, J., Schoellig, A. P. *Safe Learning in Robotics: From Learning-Based Control to Safe Reinforcement Learning*. *Annual Review of Control, Robotics, and Autonomous Systems*, 2022. DOI: <https://doi.org/10.1146/annurev-control-042920-020211>
16. Shen, C., Shi, Y., Buckham, B. *Trajectory Tracking Control of an Autonomous Underwater Vehicle Using Lyapunov-Based Model Predictive Control*. *IEEE Transactions on Industrial Electronics*, 2018. DOI: <https://doi.org/10.1109/TIE.2017.2779442>
17. Yan, Z., Gong, P., Zhang, W., Wu, W. *Model predictive control of autonomous underwater vehicles for trajectory tracking with external disturbances*. *Ocean Engineering*, 2020. DOI: <https://doi.org/10.1016/j.oceaneng.2020.107884>
18. Gong, P., Yan, Z., Zhang, W., Tang, J. *Lyapunov-based model predictive control trajectory tracking for an autonomous underwater vehicle with external disturbances*. *Ocean Engineering*, 2021. DOI: <https://doi.org/10.1016/j.oceaneng.2021.109010>
19. Shen, C., Shi, Y. *Distributed implementation of nonlinear model predictive control for AUV trajectory tracking*. *Automatica*, 2020. DOI: <https://doi.org/10.1016/j.automatica.2020.108863>
20. Heshmati-Alamdari, S., Karras, G. C., Marantos, P., Kyriakopoulos, K. J. *A Robust Predictive Control Approach for Underwater Robotic Vehicles*. *IEEE Transactions on Control Systems Technology*, 2020. DOI: <https://doi.org/10.1109/TCST.2019.2939248>
21. *Robust MPC-based trajectory tracking of autonomous underwater vehicles with model uncertainty*. *Ocean Engineering*, 2023. DOI: <https://doi.org/10.1016/j.oceaneng.2023.115617>
22. Arcos-Legarda, J., Gutiérrez, Á. *Disturbance Observer-Based Model Predictive Control for an Unmanned Underwater Vehicle*. *Journal of Marine Science and Engineering*, 2024. DOI: <https://doi.org/10.3390/jmse12010094>
23. Zhang, W., Wang, Q., Du, X., Zheng, Y. *Real-time NMPC for three-dimensional trajectory tracking control of AUV with disturbances*. *Ocean Engineering*, 2025. DOI: <https://doi.org/10.1016/j.oceaneng.2024.120267>
24. *MPC-based 3-D trajectory tracking for an autonomous underwater vehicle with constraints in complex ocean environments*. *Ocean Engineering*, 2019. DOI: <https://doi.org/10.1016/j.oceaneng.2019.106309>
25. Liu, T., Zhao, J., Hu, Y., Huang, J. *Trajectory tracking control of vectored thruster autonomous underwater vehicles based on deep reinforcement learning*. *Ships and Offshore Structures*, 2024. DOI: <https://doi.org/10.1080/17445302.2024.2391235>
