function params = model_params_default()
%MODEL_PARAMS_DEFAULT 返回 6DOF UUV 离散模型默认参数。
%   所有参数集中在一个结构体中，便于 MPC、RL 和对比实验共享。

params.dt = 0.1;                         % 离散采样时间 [s]
params.mass = 45.0;                      % 质量 [kg]
params.inertia = diag([3.2, 4.1, 4.8]);  % 转动惯量 [kg*m^2]
params.M_rb = diag([params.mass, params.mass, params.mass, 3.2, 4.1, 4.8]);
params.added_mass = diag([8, 10, 12, 0.8, 1.0, 1.2]);
params.M = params.M_rb + params.added_mass;
params.M_inv = inv(params.M);

% 线性和二次阻尼。数值选择偏保守，保证示例闭环不发散。
params.D_lin = diag([18, 22, 26, 2.2, 2.6, 3.0]);
params.D_quad = diag([4.0, 4.5, 5.0, 0.5, 0.6, 0.7]);

% 恢复力/姿态软约束项，避免姿态漂移过大。
params.K_eta = diag([0, 0, 0, 1.0, 1.2, 0.15]);

% 控制与状态约束。
params.u_min = [-120; -120; -140; -35; -35; -40];
params.u_max = [ 120;  120;  140;  35;  35;  40];
params.nu_max = [2.5; 2.5; 2.0; 1.2; 1.2; 1.4];
params.eta_min = [-inf; -inf; -30; -pi/2; -pi/2; -inf];
params.eta_max = [ inf;  inf;   2;  pi/2;  pi/2;  inf];

% 默认扰动为 0，可由主程序注入海流/建模误差。
params.disturbance_default = zeros(6,1);

% 数值积分设置。
params.integration = 'semi_euler';
params.name = '6DOF_UUV_discrete_default';
end
