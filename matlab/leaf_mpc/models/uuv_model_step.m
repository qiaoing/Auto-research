function x_next = uuv_model_step(x, u, params, disturbance)
%UUV_MODEL_STEP 6DOF UUV 离散一步推进。
%   x_next = uuv_model_step(x,u,params,disturbance)
%   状态 x=[eta(6);nu(6)]，eta=[x;y;z;phi;theta;psi]，nu=[u;v;w;p;q;r]。
%   控制 u 为 6 维广义力/力矩。disturbance 为 6 维外部扰动，默认 0。

if nargin < 3 || isempty(params)
    params = model_params_default();
end
if nargin < 4 || isempty(disturbance)
    disturbance = params.disturbance_default;
end

x = x(:); u = u(:); disturbance = disturbance(:);
if numel(x) ~= 12
    error('uuv_model_step:badState', '状态 x 必须为 12 维列向量。');
end
if numel(u) ~= 6
    error('uuv_model_step:badControl', '控制 u 必须为 6 维列向量。');
end
if numel(disturbance) ~= 6
    error('uuv_model_step:badDisturbance', '扰动 disturbance 必须为 6 维列向量。');
end

eta = x(1:6);
nu = x(7:12);
dt = params.dt;

% 控制限幅，保证仿真数值安全。
tau = min(max(u, params.u_min), params.u_max) + disturbance;

% 运动学：体坐标速度到惯性坐标速度的简化 6DOF 变换。
J = local_kinematic_matrix(eta);
eta_dot = J * nu;

% 动力学：M*nu_dot = tau - D(nu)nu - K_eta*eta_att。
D = params.D_lin + params.D_quad * diag(abs(nu));
restoring = params.K_eta * eta;
nu_dot = params.M_inv * (tau - D * nu - restoring);

% 半隐式 Euler：先更新速度，再更新位置姿态，数值更稳。
nu_next = nu + dt * nu_dot;
nu_next = min(max(nu_next, -params.nu_max), params.nu_max);
eta_next = eta + dt * (J * nu_next);
eta_next(4:6) = arrayfun(@wrap_pi_local, eta_next(4:6));
eta_next = min(max(eta_next, params.eta_min), params.eta_max);

x_next = [eta_next; nu_next];
if any(~isfinite(x_next))
    error('uuv_model_step:nonFinite', '模型输出出现非有限数值。');
end
end

function J = local_kinematic_matrix(eta)
%LOCAL_KINEMATIC_MATRIX 简化刚体运动学矩阵。
phi = eta(4); theta = eta(5); psi = eta(6);
cp = cos(phi); sp = sin(phi); ct = cos(theta); st = sin(theta); cy = cos(psi); sy = sin(psi);
Rz = [cy -sy 0; sy cy 0; 0 0 1];
Ry = [ct 0 st; 0 1 0; -st 0 ct];
Rx = [1 0 0; 0 cp -sp; 0 sp cp];
R = Rz * Ry * Rx;
ct_safe = sign(ct) * max(abs(ct), 1e-3);
T = [1, sp*st/ct_safe, cp*st/ct_safe; 0, cp, -sp; 0, sp/ct_safe, cp/ct_safe];
J = blkdiag(R, T);
end

function a = wrap_pi_local(a)
%WRAP_PI_LOCAL 将角度限制到 [-pi,pi]。
a = mod(a + pi, 2*pi) - pi;
end
