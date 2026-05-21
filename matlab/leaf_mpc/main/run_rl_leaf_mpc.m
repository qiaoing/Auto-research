%RUN_RL_LEAF_MPC 运行 RL 参数学习示例并绘图。
clear; clc;
rootDir = fileparts(fileparts(mfilename('fullpath'))); addpath(genpath(rootDir));
config.episodes = 8; config.seed = 7;
trainLog = rl_train_loop(config);
save(fullfile(rootDir,'results','rl_training_log.mat'),'trainLog');
figure('Visible','off');
subplot(2,1,1); plot(trainLog.reward,'LineWidth',1.5); grid on; ylabel('episode reward'); title('RL-MPC 训练过程');
subplot(2,1,2); plot(trainLog.weightScale,'LineWidth',1.2); grid on; xlabel('episode'); ylabel('权重缩放'); legend('Q','P','R','lambda');
saveas(gcf, fullfile(rootDir,'figures','rl_training_curves.png')); close(gcf);
fprintf('RL 参数学习示例完成。\n');
