function trainLog = rl_train_loop(config)
%RL_TRAIN_LOOP LEAF-MPC 参数学习外环示例。
%   当前版本实现可复现的轻量随机搜索/类 PPO 占位流程，记录 reward 和 P/Q/R/lambda 变化。
if nargin < 1, config = struct(); end
if ~isfield(config,'episodes'), config.episodes = 6; end
if ~isfield(config,'seed'), config.seed = 7; end
rng(config.seed);
params = model_params_default(); model = uuv_model_wrap(params);
[baseWeights, constraints, mpcConfig] = mpc_default_config(params);
mpcConfig.N = 8;
trajCfg = struct(); T = 12; steps = round(T/params.dt);
policyMean = zeros(4,1);
trainLog.reward = zeros(config.episodes,1);
trainLog.weightScale = zeros(config.episodes,4);
for ep = 1:config.episodes
    action = policyMean + 0.25*randn(4,1);
    weights = rl_action_to_weights(action, baseWeights);
    x = zeros(12,1); x(3) = -5;
    prev_u = zeros(6,1); epReward = 0;
    for k = 1:steps
        tk = (k-1)*params.dt;
        ref = traj_utils('sampleSeq', tk, mpcConfig.N, params.dt, trajCfg);
        [u, info] = mpc_solve(x, ref.x_ref, weights, constraints, model, mpcConfig);
        x = model.step(x, u, []);
        r = rl_reward(x, u, ref.x_ref(:,1), info.constraintInfo);
        epReward = epReward + r;
        prev_u = u;
        %#ok<NASGU> 观测接口预留给 PPO 策略网络
        obs = rl_observation(x, ref.x_ref(:,1), prev_u, info);
    end
    trainLog.reward(ep) = epReward;
    trainLog.weightScale(ep,:) = weights.rlScale(:)';
    % 简单策略改进：奖励较差时减小控制权重、提高跟踪权重探索均值。
    policyMean = 0.85*policyMean + 0.15*action + 0.01*sign(epReward)*[1;1;-0.5;0.2];
end
trainLog.description = '轻量 RL 参数学习占位流程；可替换为 PPO。';
end
