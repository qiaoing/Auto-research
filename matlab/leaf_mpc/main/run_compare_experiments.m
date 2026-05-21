%RUN_COMPARE_EXPERIMENTS 对比 custom 与 matlab/fallback 求解器。
clear; clc;
rootDir = fileparts(fileparts(mfilename('fullpath'))); addpath(genpath(rootDir));
solvers = {'custom','matlab'}; summary = struct();
for i = 1:numel(solvers)
    params = model_params_default(); model = uuv_model_wrap(params); [weights,constraints,config]=mpc_default_config(params);
    config.solverType = solvers{i}; config.N = 8; T=10; steps=round(T/params.dt); trajCfg=struct();
    x=zeros(12,steps+1); x(:,1)=[0;0;-5;0;0;0;zeros(6,1)]; uHist=zeros(6,steps); refHist=zeros(12,steps+1); computeTime=zeros(steps,1);
    for k=1:steps
        tk=(k-1)*params.dt; refSeq=traj_utils('sampleSeq',tk,config.N,params.dt,trajCfg); refHist(:,k)=refSeq.x_ref(:,1);
        tic; [u,info]=mpc_solve(x(:,k),refSeq.x_ref,weights,constraints,model,config); computeTime(k)=toc; %#ok<NASGU>
        uHist(:,k)=u; x(:,k+1)=model.step(x(:,k),u,[]);
    end
    refLast=traj_fig8_3d(T,trajCfg); refHist(:,end)=refLast.x_ref(:,1);
    result.t=0:params.dt:T; result.x=x; result.u=uHist; result.ref=refHist; result.computeTime=computeTime;
    metrics=plot_tracking_metrics(result, fullfile(rootDir,'figures',['metrics_' solvers{i} '.png']));
    summary.(solvers{i}).metrics=metrics; summary.(solvers{i}).solver=info.solver; summary.(solvers{i}).status=info.status;
end
save(fullfile(rootDir,'results','solver_comparison.mat'),'summary');
fprintf('求解器对比完成。\n');
