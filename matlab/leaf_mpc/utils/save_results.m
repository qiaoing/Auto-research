function save_results(result, filename)
%SAVE_RESULTS 保存结果结构体。
if nargin < 2, filename = fullfile('results','result.mat'); end
folder = fileparts(filename);
if ~isempty(folder) && ~exist(folder,'dir'), mkdir(folder); end
save(filename, 'result');
end
