function [u_opt, info] = mpc_solve(xk, refSeq, weights, constraints, model, config)
%MPC_SOLVE 统一 MPC 求解器入口。
if nargin < 6 || isempty(config) || ~isfield(config,'solverType')
    config.solverType = 'custom';
end
switch lower(char(config.solverType))
    case 'custom'
        [u_opt, info] = mpc_solver_custom(xk, refSeq, weights, constraints, model, config);
    case {'matlab','toolbox'}
        [u_opt, info] = mpc_solver_matlab(xk, refSeq, weights, constraints, model, config);
    otherwise
        error('mpc_solve:unknownSolver', '未知 solverType: %s', config.solverType);
end
end
