function metrics = plot_tracking_metrics(result, figPath)
%PLOT_TRACKING_METRICS 绘制误差和控制输入曲线并返回指标。
if nargin < 2, figPath = fullfile('figures','tracking_metrics.png'); end
e = result.x(1:3,:) - result.ref(1:3,:);
err = sqrt(sum(e.^2,1));
metrics.meanError = mean(err);
metrics.rmsError = sqrt(mean(err.^2));
metrics.maxError = max(err);
metrics.peakControl = max(abs(result.u(:)));
metrics.meanComputeTime = mean(result.computeTime);
figure('Visible','off');
subplot(2,1,1); plot(result.t, e'); grid on; ylabel('位置误差 [m]'); legend('e_x','e_y','e_z');
subplot(2,1,2); plot(result.t(1:size(result.u,2)), result.u'); grid on; xlabel('t [s]'); ylabel('控制');
saveas(gcf, figPath); close(gcf);
end
