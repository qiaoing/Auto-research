function ref = traj_fig8_3d(t, cfg)
%TRAJ_FIG8_3D 生成三维八字参考轨迹。
%   ref = traj_fig8_3d(t,cfg) 支持标量或向量时间 t。
%   x-y 平面为 Lissajous 八字，z 方向为慢变起伏。

if nargin < 2 || isempty(cfg)
    cfg = struct();
end
cfg = local_defaults(cfg);
t = t(:)';
w = 2*pi / cfg.period * cfg.speedScale;

x = cfg.center(1) + cfg.ampX * sin(w*t);
y = cfg.center(2) + cfg.ampY * sin(w*t).*cos(w*t);
z = cfg.center(3) + cfg.ampZ * sin(cfg.zFreq*w*t + cfg.zPhase);

vx = cfg.ampX * w * cos(w*t);
vy = cfg.ampY * w * cos(2*w*t);
vz = cfg.ampZ * cfg.zFreq*w * cos(cfg.zFreq*w*t + cfg.zPhase);

ax = -cfg.ampX * w^2 * sin(w*t);
ay = -2*cfg.ampY * w^2 * sin(2*w*t);
az = -cfg.ampZ * (cfg.zFreq*w)^2 * sin(cfg.zFreq*w*t + cfg.zPhase);

yaw = atan2(vy, vx);
yaw = arrayfun(@(a) mod(a+pi,2*pi)-pi, yaw);

ref.pos = [x; y; z];
ref.vel = [vx; vy; vz];
ref.acc = [ax; ay; az];
ref.yaw_ref = yaw;
ref.x_ref = [ref.pos; zeros(2,numel(t)); yaw; ref.vel; zeros(3,numel(t))];
ref.t = t;
ref.cfg = cfg;
end

function cfg = local_defaults(cfg)
%LOCAL_DEFAULTS 补齐轨迹配置默认值。
defs.center = [0;0;-5];
defs.ampX = 8;
defs.ampY = 5;
defs.ampZ = 1.5;
defs.period = 28;
defs.speedScale = 1.0;
defs.zFreq = 0.5;
defs.zPhase = pi/6;
fields = fieldnames(defs);
for i = 1:numel(fields)
    f = fields{i};
    if ~isfield(cfg, f) || isempty(cfg.(f))
        cfg.(f) = defs.(f);
    end
end
cfg.center = cfg.center(:);
end
