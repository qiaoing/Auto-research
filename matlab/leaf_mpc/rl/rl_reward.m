function r = rl_reward(state, u, ref, constraintInfo)
%RL_REWARD 闭环性能奖励：误差小、控制小、违约少。
if nargin < 4 || isempty(constraintInfo)
    constraintInfo.controlViolation = 0;
    constraintInfo.stateViolation = 0;
end
e = state(:) - ref(:);
e(4:6) = arrayfun(@(a) mod(a+pi,2*pi)-pi, e(4:6));
Gamma = constraintInfo.controlViolation + constraintInfo.stateViolation;
r = -2.0*norm(e(1:3))^2 - 0.2*norm(e(4:6))^2 - 0.002*norm(u)^2 - 20*Gamma;
end
