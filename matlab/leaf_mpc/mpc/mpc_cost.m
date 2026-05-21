function [J, detail] = mpc_cost(xSeq, uSeq, refSeq, weights, constraints)
%MPC_COST 计算 MPC 预测代价。
N = size(uSeq,2);
J = 0; detail.track = 0; detail.control = 0; detail.smooth = 0; detail.constraint = 0;
uprev = zeros(size(uSeq,1),1);
for k = 1:N
    e = xSeq(:,k) - refSeq(:,k);
    e(4:6) = arrayfun(@(a) mod(a+pi,2*pi)-pi, e(4:6));
    du = uSeq(:,k) - uprev;
    c = local_constraint_penalty(xSeq(:,k), uSeq(:,k), constraints);
    detail.track = detail.track + e' * weights.Q * e;
    detail.control = detail.control + uSeq(:,k)' * weights.R * uSeq(:,k);
    detail.smooth = detail.smooth + du' * weights.S * du;
    detail.constraint = detail.constraint + weights.lambda * c;
    uprev = uSeq(:,k);
end
eN = xSeq(:,N+1) - refSeq(:,N+1);
eN(4:6) = arrayfun(@(a) mod(a+pi,2*pi)-pi, eN(4:6));
J = detail.track + detail.control + detail.smooth + detail.constraint + eN' * weights.P * eN;
end

function p = local_constraint_penalty(x,u,constraints)
eta = x(1:6); nu = x(7:12);
p = sum(max(0, u-constraints.u_max).^2) + sum(max(0, constraints.u_min-u).^2) + ...
    sum(max(0, abs(nu)-constraints.nu_max).^2) + ...
    sum(max(0, eta-constraints.eta_max).^2) + sum(max(0, constraints.eta_min-eta).^2);
end
