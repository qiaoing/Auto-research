%TEST_MODEL_AND_TRAJECTORY 模型和轨迹最小测试。
params = model_params_default();
x0 = zeros(12,1); x0(3) = -5;
u0 = [10; -5; 3; 0.5; -0.3; 0.2];
x1 = uuv_model_step(x0, u0, params, []);
assert(all(size(x1)==[12,1]), 'x_next 维度错误');
assert(all(isfinite(x1)), 'x_next 必须为有限数值');
x2 = uuv_model_step(x0, u0, params, []);
assert(norm(x1-x2) < 1e-12, '固定输入下模型应可复现');

cfg = struct('ampX',8,'ampY',5,'ampZ',1.5,'period',28);
t = linspace(0, 56, 300);
ref = traj_fig8_3d(t, cfg);
assert(all(size(ref.pos)==[3,numel(t)]), '参考位置维度错误');
assert(max(ref.pos(3,:))-min(ref.pos(3,:)) > 2.0, 'z 方向起伏不足');
assert(all(isfinite(ref.x_ref(:))), '参考状态包含非有限数值');

figDir = fullfile(fileparts(fileparts(mfilename('fullpath'))),'figures');
try
    figure('Visible','off'); plot3(ref.pos(1,:), ref.pos(2,:), ref.pos(3,:), 'LineWidth', 1.5); grid on;
    xlabel('x'); ylabel('y'); zlabel('z'); title('3D 八字参考轨迹'); view(3);
    saveas(gcf, fullfile(figDir,'fig8_reference_3d.png')); close(gcf);
catch ME
    fid = fopen(fullfile(figDir,'fig8_reference_3d_degraded.txt'),'w');
    fprintf(fid, '图形后端不可用，降级记录：%s\n', ME.message); fclose(fid);
end
