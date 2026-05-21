function out = traj_utils(action, varargin)
%TRAJ_UTILS 轨迹相关工具函数集合。
%   traj_utils('wrapPi', angle)
%   traj_utils('refState', ref, idx)
%   traj_utils('sampleSeq', t0, N, dt, cfg)

switch lower(action)
    case 'wrappi'
        out = mod(varargin{1}+pi, 2*pi) - pi;
    case 'refstate'
        ref = varargin{1}; idx = varargin{2};
        out = ref.x_ref(:, idx);
    case 'sampleseq'
        t0 = varargin{1}; N = varargin{2}; dt = varargin{3}; cfg = varargin{4};
        out = traj_fig8_3d(t0 + (0:N)*dt, cfg);
    otherwise
        error('traj_utils:unknownAction', '未知轨迹工具动作: %s', action);
end
end
