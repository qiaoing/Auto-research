# RLDMPC-LIT-002 RL-Learned MPC Weights for Differentiable MPC

## 调研范围与核验口径
- 主题聚焦：`RL/PPO/DDPG` 学习或调节 `MPC` 的 `P/Q/R`、终端权重、控制权重、软约束惩罚、预测时域等参数，而不是直接输出控制输入。
- 优先核验来源：`arXiv`、`NeurIPS/CoRL/PMLR/Annual Reviews` 官方页面、大学官方论文库、会议目录、期刊/出版社题录页。
- 本报告只保留已核验到英文主来源的条目；若仅能确认预印本或项目页，会明确标注不确定性。

## 结论先行
1. 已核验文献明确支持一条与 `LEAF-MPC` 高度一致的路线：`RL` 学的是 `MPC` 的代价权重或元参数，`MPC` 仍负责约束下的在线优化，而不是让 `RL` 直接输出推进器/舵面控制量。强证据包括 `Mehndiratta et al. (IROS 2018)`、`Zarrouki et al. (ECC 2021, arXiv 2024)`、`Bøhn et al. (EAAI 2023)`、`Hamadeh et al. (IECON 2025)`。
2. 已核验文献也明确支持“梯度穿过 `MPC`”来学习成本参数或 cost map：`Amos et al. (NeurIPS 2018)` 奠定 `differentiable MPC` 基础，`Romero et al. (ICRA 2024)` 明确把 `PPO` 与 `diffMPC` 结合，`Tao et al. (arXiv 2023/2024)` 与 `Jahncke et al. (RA-L 2026)` 则把闭环 cost/weights 学习进一步推进到更贴近工程的 setting。
3. 对本文 `LEAF-MPC` 最稳妥的表述，不应写成“`RL` 学控制律”，而应写成“`RL` 输出受约束的 `MPC` 参数化，包括 `Q,R,P`、终端项、软约束惩罚与鲁棒补偿系数；控制输入由可微 `MPC` 求解器在线给出”。
4. 当前强证据更常见于“学习对角权重、低维权重向量、权重集合、终端/线性 cost term 或时域元参数”，而不是直接学习稠密 full `P/Q/R`。因此，`LEAF-MPC` 若采用 `block-diagonal`、`diagonal` 或 `Cholesky` 参数化，更符合现有文献证据。

## 核心文献表

| 文献 | 来源核验 | 相关度 | 关系标签 | 与 `LEAF-MPC` 的直接关系 |
|---|---|---|---|---|
| Amos et al., *Differentiable MPC for End-to-end Planning and Control* | NeurIPS 2018, [arXiv:1810.13400](https://arxiv.org/abs/1810.13400) | 强相关 | `dMPC` / `policy gradient through MPC` / `learn cost` | 把 `MPC` 明确写成可微 policy class，梯度可经 `KKT`/隐式微分回传；是 `RL` 或梯度法学习 `MPC` 成本参数的理论起点。 |
| Mehndiratta et al., *Automated Tuning of Nonlinear Model Predictive Controller by Reinforcement Learning* | IROS 2018, [doi:10.1109/IROS.2018.8594350](https://doi.org/10.1109/IROS.2018.8594350) | 强相关 | `RL调权重` / `NMPC` / `trajectory tracking` | 明确把 `RL` 用于 `NMPC` 目标函数权重自动整定，且任务就是 aerial robot 轨迹跟踪。这是“`RL` 调 `MPC` 权重而非直接出控制量”的早期直接证据。 |
| Zarrouki et al., *Weights-varying MPC for Autonomous Vehicle Guidance: a Deep Reinforcement Learning Approach* | ECC 2021, [doi:10.23919/ECC54610.2021.9655042](https://doi.org/10.23919/ECC54610.2021.9655042) | 强相关 | `DRL调权重` / `weights-varying MPC` / `trajectory tracking` | 直接学习上下文相关 cost weights，并在线切换/调节，最接近“机动阶段不同，`Q/R` 取值不同”的论证。 |
| Zarrouki et al., *A Safe Reinforcement Learning driven Weights-varying Model Predictive Control for Autonomous Vehicle Motion Control* | 2024, [arXiv:2402.02624](https://arxiv.org/abs/2402.02624) | 强相关 | `safe RL with MPC` / `RL权重调度` | 核心思想不是让 `RL` 直接在连续不可控空间里乱学权重，而是把动作限制在“安全权重集合/ Pareto 权重目录”中，适合安全关键 UUV 写法。 |
| Bøhn et al., *Optimization of the Model Predictive Control Meta-Parameters Through Reinforcement Learning* | Eng. Appl. AI 2023, [doi:10.1016/j.engappai.2023.106211](https://doi.org/10.1016/j.engappai.2023.106211) | 强相关 | `RL调MPC元参数` / `state-dependent tuning` | 虽然主调对象不只是 `Q/R`，但它明确证明：`RL` 可以学非直接可微的 `MPC` 元参数，并且可以做状态依赖调节。对 `LEAF-MPC` 学终端权重、重计算策略、惩罚因子很有借鉴价值。 |
| Hamadeh et al., *Deep Reinforcement Learning for Tuning of Adaptive Model Predictive Control for Autonomous Driving* | IECON 2025, [doi:10.1109/IECON58223.2025.11221544](https://doi.org/10.1109/IECON58223.2025.11221544) | 强相关 | `PPO+MPC` / `DDPG+MPC` / `weight+horizon tuning` | 直接核验到该文使用 `PPO` 与 `DDPG` 在线调节 cost weights 和 prediction horizon；是“`PPO` 学 `MPC` 参数”的直接近邻证据。 |
| Jahncke et al., *Differentiable Weights-Varying Nonlinear MPC via Gradient-Based Policy Learning* | IEEE RA-L 2026, [doi:10.1109/LRA.2026.3662644](https://doi.org/10.1109/LRA.2026.3662644) | 强相关 | `differentiable weights-varying MPC` / `learn q,r` | 该文直接用轻量策略网络根据前视观测输出 `MPC` 权重，并通过 solver sensitivities 反传；与 `LEAF-MPC` 的“前视机动强度/扰动态势驱动权重调节”高度同构。 |
| Romero et al., *Actor-Critic Model Predictive Control* | ICRA 2024, [doi:10.1109/ICRA57147.2024.10610381](https://doi.org/10.1109/ICRA57147.2024.10610381) | 强相关 | `PPO+diffMPC` / `learn cost map` / `actor-critic` | 官方论文页明确写到：`MPC` 作为 actor 的可微最后一层，训练时用 `PPO`，学习对象是 `Q(s_k), p(s_k)` 神经 cost map，而部署时执行的仍是 `MPC` 输出。 |
| Tao et al., *DiffTune-MPC: Closed-Loop Learning for Model Predictive Control* | 2023/2024, [arXiv:2312.11384](https://arxiv.org/abs/2312.11384) | 强相关 | `closed-loop learning` / `learn MPC cost` / `analytic gradients` | 不是 `RL`，但它非常直接地回答“如何按闭环性能学习 `MPC` cost，而不是按开环优化目标调参”。对论文里说明“为什么要学成本参数”尤其有用。 |
| Fröhlich et al., *Contextual Tuning of Model Predictive Control for Autonomous Racing* | IROS 2022, [doi:10.1109/IROS47612.2022.9981780](https://doi.org/10.1109/IROS47612.2022.9981780) | 中等相关 | `context-dependent tuning` / `objective adaptation` | 不是 `RL` 而是 contextual Bayesian optimization，但它证明了“环境上下文变化时，模型和 objective 都应联动调节”，与海流/工况变化下的 `UUV` 很契合。 |
| Hoeller et al., *Deep Value Model Predictive Control* | CoRL 2020, [PMLR 100:990-1004](https://proceedings.mlr.press/v100/hoeller20a.html) | 中等相关 | `actor-critic MPC` / `critic enters cost` | 该文不是学 `P/Q/R`，而是把 critic 的 value function 引入 `MPC` 目标；可作为“RL 与 MPC 融合但不直接替代优化器”的背景链。 |
| Hewing et al., *Learning-Based Model Predictive Control: Toward Safe Learning in Control* | Annual Review 2020, [doi:10.1146/annurev-control-090419-075625](https://doi.org/10.1146/annurev-control-090419-075625) | 背景相关 | `survey` / `safe learning` / `controller parameterization` | 综述明确把 `MPC` 学习分成模型学习、控制器参数化学习、`MPC` 作为安全层三类；很适合给 `LEAF-MPC` 在 related work 里定位置。 |

## 补充方法链：可微最优控制与安全微分层
- `Jin et al., Pontryagin Differentiable Programming`（NeurIPS 2020, [arXiv:1912.12970](https://arxiv.org/abs/1912.12970)）证明了通过 `Pontryagin Maximum Principle` 也可以对目标函数、策略和动力学做端到端求导。它不是显式 `MPC`，但说明“学习控制目标函数”在最优控制框架中是成立的。
- `Jin et al., Safe Pontryagin Differentiable Programming`（NeurIPS 2021, [arXiv:2105.14937](https://arxiv.org/abs/2105.14937)）把安全约束通过 barrier 形式纳入可微学习，说明“学参数”与“全过程保持约束安全”并不矛盾。
- 这两篇更像 `LEAF-MPC` 的方法论背景，而不是最直接的 `RL` 调 `P/Q/R` 证据，因此放在补充链而不是核心表中。

## 关键公式与思想

### 1. 推荐的 `LEAF-MPC` 双层结构
下面的式子是结合上述文献对本文第二小节的归纳写法，不是任何单篇论文的逐字原式：

$$
\theta_t = \pi_{\psi}(o_t), \qquad
\theta_t = \{Q_t, R_t, P_t, \rho_t, \lambda_t, \dots\}
$$

其中 `RL` 策略 `\pi_{\psi}` 不直接输出控制输入，而是输出 `MPC` 参数。内层 `MPC` 求解：

$$
\begin{aligned}
\mathbf{u}_{t:t+H-1}^*(\theta_t)
= \arg\min_{\mathbf{u},\,\boldsymbol\xi}\;
& \sum_{k=0}^{H-1}
\|x_{t+k}-x^{\mathrm{ref}}_{t+k}\|_{Q_t}^2
+ \|u_{t+k}\|_{R_t}^2 \\
& + \|x_{t+H}-x^{\mathrm{ref}}_{t+H}\|_{P_t}^2
+ \rho_t\|\xi_{t+k}\|^2
+ \lambda_t \Phi_{\mathrm{rob}}(x_{t+k},u_{t+k},\hat d_{t+k})
\end{aligned}
$$

subject to

$$
\begin{aligned}
& x_{t+k+1}=f_{\hat\phi}(x_{t+k},u_{t+k},\hat d_{t+k}),\\
& g(x_{t+k},u_{t+k}) \le \xi_{t+k},\quad \xi_{t+k}\ge 0,\\
& u_{\min} \le u_{t+k} \le u_{\max},\quad x_{t+k}\in \mathcal X.
\end{aligned}
$$

执行量为首个控制量：

$$
u_t = u_t^*(\theta_t).
$$

### 2. 若采用可微 `MPC`，外层梯度可写为
同样是归纳写法：

$$
\nabla_{\psi} \mathcal{J}
=
\frac{\partial \mathcal{J}}{\partial u_t^*}
\frac{\partial u_t^*}{\partial \theta_t}
\frac{\partial \theta_t}{\partial \psi}.
$$

`Amos et al. 2018` 给出通过 `KKT` / 固定点近似求导的路径；`Romero et al. 2024` 明确把这条路径放进 `PPO + diffMPC` actor-critic 中；`Jahncke et al. 2026` 则把它用于上下文相关 `q,r` 学习。

### 3. 若采用 `PPO` 外层训练，动作是权重参数而非控制输入
可写成：

$$
a_t = \theta_t = \pi_{\psi}(o_t),
$$

但环境真正执行的是

$$
u_t = \mathrm{MPC}(x_t;\theta_t).
$$

`Romero et al. 2024` 的已核验算法步骤可概括为：
- actor 输出 cost map 中的 `Q(s_k), p(s_k)`；
- 控制均值由 `diffMPC(x_k, Q(s_k), p(s_k))` 给出；
- 用 `PPO-clip objective` 更新 cost map，并通过 `diffMPC backward` 传播梯度。

对 `LEAF-MPC` 而言，若用户文中采用增强 `PPO`，完全可以把 `PPO` 的 action 定义成 `Q/R/P`、软约束罚因子、鲁棒补偿权重等的低维向量，而不是把 action 定义成推进器命令。

### 4. 权重参数化建议
现有强相关文献反复给出的经验是一致的：学习量需要被约束。
- 最常见做法是只学对角项或低维权重向量，而不是 full matrix。
- 为保证正定/半正定，可设

$$
Q_t = \mathrm{diag}(\mathrm{softplus}(w_t^Q)+\varepsilon_Q),
\quad
R_t = \mathrm{diag}(\mathrm{softplus}(w_t^R)+\varepsilon_R),
\quad
P_t = \mathrm{diag}(\mathrm{softplus}(w_t^P)+\varepsilon_P).
$$

- 若必须学 full matrix，更稳妥的写法是 `Cholesky` 参数化：`Q_t=L_tL_t^\top+\varepsilon I`。
- `Romero et al. 2024` 和 `Jahncke et al. 2026` 都明确采用了有界/正值输出，支持这一写法。

### 5. 安全约束处理的三条可用路线
- 路线 A：硬状态/输入约束全部保留在内层 `MPC`，外层 `RL` 只调 cost parameters。这最适合本文的表述。
- 路线 B：对软约束引入 `slack` 与惩罚 `\rho_t`，由 `RL` 调 `\rho_t`，而不是让 `RL` 改约束边界本身。
- 路线 C：参考 `Safe RL-WMPC`，把 `RL` 动作限制在可行的权重集合或预优化权重库中，避免训练期走到危险权重区域。

## 写作要点：可直接用于论文第二小节

### 1. 问题动机
- 在 `UUV` 高速、大姿态、大机动轨迹跟踪中，固定 `Q/R/P` 很难同时兼顾姿态误差、路径误差、能耗、舵机/推进器平滑性以及扰动恢复速度。
- 当海流、附体扰动、流体参数偏差和工况切换导致模型失配时，固定权重常把不同机动阶段强行用同一组 trade-off 处理，闭环表现容易失衡。
- 因此，更合理的做法不是放弃 `MPC`，而是学习一个“上下文相关的 `MPC` 调参器”。

### 2. 方法核心
- `RL`/`PPO` 的输出定义为 `MPC` 参数向量 `\theta_t`，其中包含 `Q,R,P`、终端项、控制惩罚、软约束惩罚和鲁棒补偿系数。
- `MPC` 仍在每个采样时刻根据当前状态和参考轨迹解带约束优化问题，输出满足动力学与约束的最优控制。
- 若使用可微 `MPC`，则可以把闭环损失对权重参数的敏感度显式回传到上层策略；若数值稳定性不足，则可先用 `PPO` 进行黑箱闭环训练，再做局部可微微调。

### 3. 学习变量建议
- 首选学习变量：`Q` 中位置/姿态/速度误差权重，`R` 中推进器/舵面控制量与控制增量权重，`P` 终端权重，软约束惩罚 `\rho`，以及扰动补偿或鲁棒项系数 `\lambda`。
- 对 `UUV` 更实用的是学“结构化权重”而不是 full matrix，例如：姿态块、位置块、速度块、执行器块、终端块、约束块。
- 若需要更强可解释性，可以让策略只输出若干物理含义明确的标量，再映射到矩阵对角元。

### 4. 训练目标
- 外层回报/损失应覆盖：轨迹误差、姿态稳定性、控制能耗、控制抖振、约束违反、恢复时间、终端误差。
- 对 `PPO`，推荐把这些量聚合为长期累计奖励；对可微闭环学习，推荐直接优化闭环性能指标而非仅优化单次 `MPC` 开环目标。
- `DiffTune-MPC` 的启发是：学习目标最好与最终评估指标一致，避免“内层开环 cost 很漂亮，但闭环效果并不好”的错配。

### 5. 约束处理
- 状态、输入、速率、姿态包线等硬约束建议保留在 `MPC` 内层；`RL` 不应绕开约束直接出控制。
- 不可行性可由 `slack` 变量处理，并把 `slack penalty` 也做成可学习参数，但必须保持正值并设置下界。
- 若训练时担心探索导致危险参数，可采用离散安全权重库、权重边界投影、或 barrier/penalty 强化。

### 6. 与端到端 `RL` 的区别
- 端到端 `RL` 直接学习 `o_t \mapsto u_t`，可表达能力强，但样本需求大、可解释性弱、约束处理通常依赖额外安全层。
- 本文 `LEAF-MPC` 采用的是 `o_t \mapsto \theta_t \mapsto u_t^*`：学习的是“优化问题的参数化”，不是“动作映射本身”。
- 因而它保留了 `MPC` 的显式约束、在线重规划与物理可解释性，同时利用 `RL` 适应模型失配和非平稳扰动。

## 可直接写进论文的句子
- 与端到端强化学习直接输出控制输入不同，`LEAF-MPC` 仅学习 `MPC` 的代价权重、终端权重与软约束惩罚，而实际控制输入仍由带约束的在线优化器求得。
- 可微 `MPC` 使闭环性能关于权重参数的敏感度可以通过 `KKT` 条件或隐式微分显式获得，从而为基于梯度的代价参数学习提供了理论基础。
- 在大机动轨迹跟踪任务中，固定 `MPC` 权重难以在误差收敛、控制平滑性、能耗与扰动抑制之间持续维持最优折中，因此需要上下文相关的自适应权重调度机制。
- 现有文献的共同趋势表明，相比直接学习稠密 full `P/Q/R` 矩阵，学习结构化对角权重、低维权重向量或安全权重集合更稳定、更可解释，也更利于在线部署。
- 将强化学习限制在 `MPC` 参数空间内，而不是让其直接绕过优化器生成控制动作，有助于在保留显式约束满足能力的同时提升对模型失配和时变扰动的适应性。
- 对安全关键机器人系统而言，更合理的做法不是去掉 `MPC`，而是给 `MPC` 加一个可学习且受约束的参数调度层。

## 对本文 `LEAF-MPC` 的具体启发
- 不建议一开始就让 `PPO` 输出 full `P/Q/R`。更稳妥的是输出若干分组权重，例如：位置误差、姿态误差、速度误差、控制量、控制增量、终端项、软约束项、鲁棒项。
- `RL` 观测中应加入参考轨迹前视信息，而不只是当前误差。`Diff-WMPC` 和 `RL-WMPC` 的成功都依赖“look-ahead / context”信息。
- 对 `UUV`，建议把前视曲率、期望航向变化率、期望俯仰变化率、速度参考变化、估计海流、姿态误差、速度误差、约束余量纳入 `o_t`。
- 若模型失配显著，最好把“残差动力学/扰动估计”和“代价参数学习”分开设计：前者负责修正预测模型，后者负责重分配 tracking-effort-robustness 的权衡。
- 若可微求解器仅天然支持输入约束，而本文还需要姿态/空间包线约束，则应通过 soft constraints、barrier 或外层安全过滤补足，而不是在文中默认“所有状态约束都能无缝反传”。
- 强相关文献普遍表明，学习层输出必须做正值和边界约束。对本文可直接写成 `softplus`、sigmoid-bound 或 `Cholesky` 参数化。
- 若增强 `PPO` 已经是本文既定方案，一个自然写法是：先用 `PPO` 学出鲁棒的权重调度策略，再视需要用可微 `MPC` 在仿真中做少量 gradient fine-tuning。
- 论文叙事上可强调：`LEAF-MPC` 不是用 `RL` 替代 `MPC`，而是用 `RL` 学习在不同机动阶段如何重新配置 `MPC` 的最优性偏好与约束惩罚。

## 不确定与边界
- 本次未核验到“直接面向 `UUV` 高速大姿态轨迹跟踪，且由 `RL`/`PPO` 显式学习 `P/Q/R` 或终端权重”的成熟一手论文。现有最强证据主要来自 `UAV`、自动驾驶和通用机器人轨迹跟踪场景。
- 已核验的强相关工作中，很多学习对象是对角权重、低维 cost vector、cost map、prediction horizon 或安全权重集合，而不是稠密 full `P/Q/R`。因此若本文写成“学习完整矩阵”，需要更谨慎地说明结构化参数化。
- `Actor-Critic MPC` 的 `ICRA 2024` 版本已核验；其后续 `TRO` 扩展在官方项目页可见，但本报告引用采用已直接核验的 `ICRA 2024` 会议版本，以避免题录不确定性。
- `Safe RL-WMPC (2024)` 当前核验到的是 `arXiv` 预印本，而不是已确认的期刊版；可用于方法论支持，但正式投稿时建议再查是否已有定版发表信息。
- `Bøhn et al. 2023` 主要学习的是 `MPC` 元参数，而不只是 cost weights；因此它更适合作为“`RL` 可以调 `MPC` 参数族”的证据，而不是“直接学 `P/Q/R`”的最核心引文。

## 参考文献列表
1. Brandon Amos, Ivan Dario Jimenez Rodriguez, Jacob Sacks, Byron Boots, J. Zico Kolter. *Differentiable MPC for End-to-end Planning and Control*. NeurIPS 2018. [https://arxiv.org/abs/1810.13400](https://arxiv.org/abs/1810.13400)
2. Mohit Mehndiratta, Efe Camci, Erdal Kayacan. *Automated Tuning of Nonlinear Model Predictive Controller by Reinforcement Learning*. IROS 2018. [https://doi.org/10.1109/IROS.2018.8594350](https://doi.org/10.1109/IROS.2018.8594350)
3. Baha Zarrouki, Verena Klös, Nikolas Heppner, Simon Schwan, Robert Ritschel, Rick Voßwinkel. *Weights-varying MPC for Autonomous Vehicle Guidance: a Deep Reinforcement Learning Approach*. ECC 2021. [https://doi.org/10.23919/ECC54610.2021.9655042](https://doi.org/10.23919/ECC54610.2021.9655042)
4. Baha Zarrouki, Marios Spanakakis, Johannes Betz. *A Safe Reinforcement Learning driven Weights-varying Model Predictive Control for Autonomous Vehicle Motion Control*. arXiv 2024. [https://arxiv.org/abs/2402.02624](https://arxiv.org/abs/2402.02624)
5. Eivind Bøhn, Sebastien Gros, Signe Moe, Tor Arne Johansen. *Optimization of the Model Predictive Control Meta-Parameters Through Reinforcement Learning*. Engineering Applications of Artificial Intelligence, 2023. [https://doi.org/10.1016/j.engappai.2023.106211](https://doi.org/10.1016/j.engappai.2023.106211)
6. Feras Hamadeh, Anas Abdelkarim, Amar Hamadeh, Daniel Görges, Holger Voos. *Deep Reinforcement Learning for Tuning of Adaptive Model Predictive Control for Autonomous Driving*. IECON 2025. [https://doi.org/10.1109/IECON58223.2025.11221544](https://doi.org/10.1109/IECON58223.2025.11221544)
7. Felix Jahncke, Baha Zarrouki, Mattia Piccinini, Jovin D'Sa, David Isele, Sangjae Bae, Johannes Betz. *Differentiable Weights-Varying Nonlinear MPC via Gradient-Based Policy Learning: An Autonomous Vehicle Guidance Example*. IEEE Robotics and Automation Letters, 2026. [https://doi.org/10.1109/LRA.2026.3662644](https://doi.org/10.1109/LRA.2026.3662644)
8. Angel Romero, Yunlong Song, Davide Scaramuzza. *Actor-Critic Model Predictive Control*. ICRA 2024. [https://doi.org/10.1109/ICRA57147.2024.10610381](https://doi.org/10.1109/ICRA57147.2024.10610381)
9. Ran Tao, Sheng Cheng, Xiaofeng Wang, Shenlong Wang, Naira Hovakimyan. *DiffTune-MPC: Closed-Loop Learning for Model Predictive Control*. arXiv 2023/2024. [https://arxiv.org/abs/2312.11384](https://arxiv.org/abs/2312.11384)
10. Lukas P. Fröhlich, Christian Küttel, Elena Arcari, Lukas Hewing, Melanie N. Zeilinger, Andrea Carron. *Contextual Tuning of Model Predictive Control for Autonomous Racing*. IROS 2022. [https://doi.org/10.1109/IROS47612.2022.9981780](https://doi.org/10.1109/IROS47612.2022.9981780)
11. David Hoeller, Farbod Farshidian, Marco Hutter. *Deep Value Model Predictive Control*. CoRL 2020, PMLR 100:990-1004. [https://proceedings.mlr.press/v100/hoeller20a.html](https://proceedings.mlr.press/v100/hoeller20a.html)
12. Lukas Hewing, Kim P. Wabersich, Marcel Menner, Melanie N. Zeilinger. *Learning-Based Model Predictive Control: Toward Safe Learning in Control*. Annual Review of Control, Robotics, and Autonomous Systems, 2020. [https://doi.org/10.1146/annurev-control-090419-075625](https://doi.org/10.1146/annurev-control-090419-075625)
13. Anil Aswani, Humberto González, S. Shankar Sastry, Claire Tomlin. *Provably Safe and Robust Learning-Based Model Predictive Control*. Automatica, 2013. [https://doi.org/10.1016/j.automatica.2013.02.003](https://doi.org/10.1016/j.automatica.2013.02.003)
14. Chris J. Ostafew, Angela P. Schoellig, Timothy D. Barfoot. *Robust Constrained Learning-based NMPC Enabling Reliable Mobile Robot Path Tracking*. The International Journal of Robotics Research, 2016. [https://doi.org/10.1177/0278364916645661](https://doi.org/10.1177/0278364916645661)
15. Wanxin Jin, Zhaoran Wang, Zhuoran Yang, Shaoshuai Mou. *Pontryagin Differentiable Programming: An End-to-End Learning and Control Framework*. NeurIPS 2020. [https://arxiv.org/abs/1912.12970](https://arxiv.org/abs/1912.12970)
16. Wanxin Jin, Shaoshuai Mou, George J. Pappas. *Safe Pontryagin Differentiable Programming*. NeurIPS 2021. [https://arxiv.org/abs/2105.14937](https://arxiv.org/abs/2105.14937)
