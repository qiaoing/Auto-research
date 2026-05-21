function [u_opt, info] = mpc_solver_matlab(xk, refSeq, weights, constraints, model, config)
%MPC_SOLVER_MATLAB MATLAB toolbox/优化工具箱求解器封装。
%   若缺少 Optimization Toolbox 或 MPC Toolbox，则自动 fallback 到自写求解器。
if nargin < 6 || isempty(config), config = struct(); end
hasFmincon = exist('fmincon','file') == 2;
if ~hasFmincon
    [u_opt, info] = mpc_solver_custom(xk, refSeq, weights, constraints, model, config);
    info.solver = 'matlab_fallback_custom';
    info.status = 'fallback_no_fmincon';
    return;
end
% 为保持示例稳健，此处仍使用 custom 初值并预留 fmincon 接口。
[u0, info0] = mpc_solver_custom(xk, refSeq, weights, constraints, model, config);
u_opt = u0;
info = info0;
info.solver = 'matlab_wrapper_custom_initialization';
info.status = 'ok_fmincon_available_placeholder';
end
