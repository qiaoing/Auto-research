function model = uuv_model_wrap(params)
%UUV_MODEL_WRAP 返回供 MPC 调用的模型包装器。
%   model.step(x,u,d) 进行一步离散推进；model.params 保存参数。
if nargin < 1 || isempty(params)
    params = model_params_default();
end
model.params = params;
model.nx = 12;
model.nu = 6;
model.dt = params.dt;
model.step = @(x,u,disturbance) uuv_model_step(x, u, params, local_default_dist(params, disturbance));
end

function d = local_default_dist(params, disturbance)
if nargin < 2 || isempty(disturbance)
    d = params.disturbance_default;
else
    d = disturbance;
end
end
