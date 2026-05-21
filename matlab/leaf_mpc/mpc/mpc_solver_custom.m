function [u_opt, info] = mpc_solver_custom(xk, refSeq, weights, constraints, model, config)
%MPC_SOLVER_CUSTOM 自写 toolbox-free MPC 求解器。
%   当前实现采用参考加速度/误差反馈生成候选控制，并进行短视滚动评估。
%   该结构不是最终可微 QP，但接口与后续可微求解器保持一致。
if nargin < 6 || isempty(config), config = struct(); end
if ~isfield(config,'N'), config.N = min(10, size(refSeq,2)-1); end
if ~isfield(config,'candidateScale'), config.candidateScale = [1.0 0.55 0.25]; end
N = config.N;
params = model.params;

eta = xk(1:6); nu = xk(7:12);
ref0 = refSeq(:,1);
e = ref0 - xk;
e(4:6) = arrayfun(@(a) mod(a+pi,2*pi)-pi, e(4:6));

% 由权重粗略自整定 PD 增益，误差越重，反馈越强。
qdiag = diag(weights.Q); rdiag = diag(weights.R);
Kp_pos = [1.4; 1.4; 1.8; 0.8; 0.8; 1.0] .* sqrt(qdiag(1:6)./(mean(rdiag)+1e-6));
Kd_vel = [1.0; 1.0; 1.2; 0.4; 0.4; 0.5] .* sqrt(qdiag(7:12)./(mean(rdiag)+1e-6));
baseTau = params.M * (Kp_pos.*e(1:6) + Kd_vel.*(ref0(7:12)-nu)) + params.D_lin*nu;

bestJ = inf; bestU = zeros(6,N); bestSeq = [];
for s = config.candidateScale
    uFirst = s * baseTau;
    [uFirst, ~] = mpc_constraints(uFirst, xk, constraints);
    uSeq = repmat(uFirst, 1, N);
    % 末端逐渐减小控制，减少抖振。
    for k = 1:N
        uSeq(:,k) = uSeq(:,k) * (1 - 0.04*(k-1));
    end
    xSeq = mpc_build_prediction(xk, uSeq, model, []);
    [J, detail] = mpc_cost(xSeq, uSeq, refSeq(:,1:N+1), weights, constraints);
    if J < bestJ
        bestJ = J; bestU = uSeq; bestSeq = xSeq; bestDetail = detail;
    end
end
u_opt = bestU(:,1);
[capped, cinfo] = mpc_constraints(u_opt, xk, constraints);
u_opt = capped;
info.status = 'ok';
info.solver = 'custom_candidate_rollout';
info.cost = bestJ;
info.predictedX = bestSeq;
info.predictedU = bestU;
info.constraintInfo = cinfo;
info.costDetail = bestDetail;
end
