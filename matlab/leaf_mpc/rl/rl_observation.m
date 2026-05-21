function obs = rl_observation(state, ref, prev_u, info)
%RL_OBSERVATION 构造 RL 策略观测量。
if nargin < 3 || isempty(prev_u), prev_u = zeros(6,1); end
if nargin < 4 || isempty(info), info = struct(); end
e = state(:) - ref(:);
e(4:6) = arrayfun(@(a) mod(a+pi,2*pi)-pi, e(4:6));
if isfield(info,'constraintInfo')
    cActive = double(info.constraintInfo.active);
else
    cActive = 0;
end
trackNorm = norm(e(1:3));
obs = [e; state(7:12); prev_u(:); cActive; trackNorm];
end
