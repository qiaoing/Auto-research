function [u, info] = mpc_constraints(u, x, constraints)
%MPC_CONSTRAINTS 对控制输入执行限幅并统计约束违背。
raw = u(:);
u = min(max(raw, constraints.u_min), constraints.u_max);
info.controlViolation = norm(raw-u, 1);
if nargin >= 2 && ~isempty(x)
    nuv = x(7:12);
    info.stateViolation = sum(max(0, abs(nuv)-constraints.nu_max));
else
    info.stateViolation = 0;
end
info.active = info.controlViolation > 1e-9 || info.stateViolation > 1e-9;
end
