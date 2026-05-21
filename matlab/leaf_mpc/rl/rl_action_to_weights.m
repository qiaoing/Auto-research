function weights = rl_action_to_weights(action, baseWeights)
%RL_ACTION_TO_WEIGHTS 将低维 RL 动作映射为 MPC 权重。
%   使用 softplus 保证权重为正，并限制缩放范围避免数值爆炸。
a = action(:);
if numel(a) < 4
    a(end+1:4) = 0;
end
scale = log(1 + exp(a(1:4))) + 0.2;
scale = min(max(scale, 0.2), 8.0);
weights = baseWeights;
weights.Q = baseWeights.Q * scale(1);
weights.P = baseWeights.P * scale(2);
weights.R = baseWeights.R * scale(3);
weights.lambda = baseWeights.lambda * scale(4);
weights.rlScale = scale;
end
