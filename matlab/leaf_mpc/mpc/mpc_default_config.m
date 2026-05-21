function [weights, constraints, config] = mpc_default_config(params)
%MPC_DEFAULT_CONFIG 返回 baseline MPC 默认权重、约束和配置。
if nargin < 1 || isempty(params)
    params = model_params_default();
end
weights.Q = diag([30 30 45 3 3 10  2 2 3 0.5 0.5 0.8]);
weights.P = 3 * weights.Q;
weights.R = diag([0.02 0.02 0.025 0.04 0.04 0.05]);
weights.S = diag([0.08 0.08 0.10 0.03 0.03 0.04]);
weights.lambda = 100;
constraints.u_min = params.u_min;
constraints.u_max = params.u_max;
constraints.nu_max = params.nu_max;
constraints.eta_min = params.eta_min;
constraints.eta_max = params.eta_max;
config.N = 10;
config.solverType = 'custom';
config.maxIter = 3;
config.candidateScale = [1.0, 0.55, 0.25];
config.verbose = false;
end
