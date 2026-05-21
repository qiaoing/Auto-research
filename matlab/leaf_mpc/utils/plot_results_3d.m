function plot_results_3d(result, figPath)
%PLOT_RESULTS_3D 绘制三维轨迹跟踪图。
if nargin < 2, figPath = fullfile('figures','baseline_3d_tracking.png'); end
figure('Visible','off'); hold on; grid on; view(3);
plot3(result.ref(1,:), result.ref(2,:), result.ref(3,:), 'k--', 'LineWidth', 1.8);
plot3(result.x(1,:), result.x(2,:), result.x(3,:), 'b-', 'LineWidth', 1.5);
xlabel('x [m]'); ylabel('y [m]'); zlabel('z [m]');
legend('参考轨迹','UUV 实际轨迹'); title('3D 八字轨迹跟踪');
saveas(gcf, figPath); close(gcf);
end
