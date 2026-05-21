%RUN_SMOKE_TESTS 统一 smoke tests 入口。
% 该脚本兼容 MATLAB/Octave 的基础语法。
clear; clc;
thisDir = fileparts(mfilename('fullpath'));
rootDir = fileparts(thisDir);
addpath(genpath(rootDir));
if ~exist(fullfile(rootDir,'figures'),'dir'), mkdir(fullfile(rootDir,'figures')); end
if ~exist(fullfile(rootDir,'results'),'dir'), mkdir(fullfile(rootDir,'results')); end
run(fullfile(rootDir,'tests','test_model_and_trajectory.m'));
fprintf('LEAF-MPC smoke tests passed.\n');
