function xSeq = mpc_build_prediction(x0, uSeq, model, disturbance)
%MPC_BUILD_PREDICTION 根据控制序列滚动预测状态。
if nargin < 4
    disturbance = [];
end
N = size(uSeq,2);
xSeq = zeros(numel(x0), N+1);
xSeq(:,1) = x0(:);
for k = 1:N
    xSeq(:,k+1) = model.step(xSeq(:,k), uSeq(:,k), disturbance);
end
end
