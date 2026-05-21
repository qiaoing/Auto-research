%RUN_BASELINE_MPC 固定权重 baseline MPC 闭环仿真。
clear; clc;
rootDir = fileparts(fileparts(mfilename('fullpath'))); addpath(genpath(rootDir));
params = model_params_default(); model = uuv_model_wrap(params);
[weights, constraints, config] = mpc_default_config(params); config.solverType = 'custom';
trajCfg = struct(); T = 24; steps = round(T/params.dt);
x = zeros(12,steps+1); x(:,1) = [0;0;-5;0;0;0; zeros(6,1)];
uHist = zeros(6,steps); refHist = zeros(12,steps+1); computeTime = zeros(steps,1);
for k = 1:steps
    tk = (k-1)*params.dt;
    refSeq = traj_utils('sampleSeq', tk, config.N, params.dt, trajCfg);
    refHist(:,k) = refSeq.x_ref(:,1);
    tic; [u, info] = mpc_solve(x(:,k), refSeq.x_ref, weights, constraints, model, config); computeTime(k)=toc; %#ok<NASGU>
    uHist(:,k) = u; x(:,k+1) = model.step(x(:,k), u, []);
end
refLast = traj_fig8_3d(T, trajCfg); refHist(:,end) = refLast.x_ref(:,1);
result.t = 0:params.dt:T; result.x = x; result.u = uHist; result.ref = refHist; result.computeTime = computeTime;
if ~exist(fullfile(rootDir,'results'),'dir'), mkdir(fullfile(rootDir,'results')); end
if ~exist(fullfile(rootDir,'figures'),'dir'), mkdir(fullfile(rootDir,'figures')); end
save_results(result, fullfile(rootDir,'results','baseline_mpc_result.mat'));
plot_results_3d(result, fullfile(rootDir,'figures','baseline_3d_tracking.png'));
metrics = plot_tracking_metrics(result, fullfile(rootDir,'figures','baseline_tracking_metrics.png')); %#ok<NASGU>
save(fullfile(rootDir,'results','baseline_metrics.mat'),'metrics');
fprintf('baseline MPC 完成：RMS误差 %.3f m\n', metrics.rmsError);
