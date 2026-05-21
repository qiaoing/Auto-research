function animate_uuv_3d(result, trajRef, cfg)
%ANIMATE_UUV_3D 生成三维轨迹动画 GIF。
if nargin < 3, cfg = struct(); end
if ~isfield(cfg,'filename'), cfg.filename = fullfile('figures','uuv_tracking_animation.gif'); end
if nargin < 2 || isempty(trajRef), trajRef = result.ref; end
fig = figure('Visible','off');
for k = 1:5:numel(result.t)
    clf; hold on; grid on; view(3);
    plot3(trajRef(1,:), trajRef(2,:), trajRef(3,:), 'k--');
    plot3(result.x(1,1:k), result.x(2,1:k), result.x(3,1:k), 'b-', 'LineWidth', 1.5);
    plot3(result.x(1,k), result.x(2,k), result.x(3,k), 'ro', 'MarkerFaceColor','r');
    xlabel('x'); ylabel('y'); zlabel('z'); title('UUV 3D 跟踪动画'); drawnow;
    frame = getframe(fig); im = frame2im(frame); [A,map] = rgb2ind(im,256);
    if k == 1
        imwrite(A,map,cfg.filename,'gif','LoopCount',Inf,'DelayTime',0.08);
    else
        imwrite(A,map,cfg.filename,'gif','WriteMode','append','DelayTime',0.08);
    end
end
close(fig);
end
