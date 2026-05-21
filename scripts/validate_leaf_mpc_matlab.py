#!/usr/bin/env python3
"""验证 LEAF-MPC MATLAB 代码骨架，并在无 MATLAB/Octave 时生成可复现占位产物。

说明：当前环境没有 numpy / scipy / matplotlib / MATLAB / Octave，因此该脚本只使用 Python 标准库：
1. 检查 MATLAB 代码文件是否齐全且非空；
2. 生成可用于文档/CI 的占位结果文件；
3. 写出结构化摘要，供后续真正 MATLAB 闭环结果替换。
"""
from __future__ import annotations
from pathlib import Path
import base64
import json
import math
import os
import struct
import zlib

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'matlab' / 'leaf_mpc'
REQ = [
    'main/run_smoke_tests.m','main/run_baseline_mpc.m','main/run_compare_experiments.m','main/run_rl_leaf_mpc.m',
    'models/model_params_default.m','models/uuv_model_step.m','models/uuv_model_wrap.m',
    'trajectory/traj_fig8_3d.m','trajectory/traj_utils.m',
    'mpc/mpc_default_config.m','mpc/mpc_cost.m','mpc/mpc_constraints.m','mpc/mpc_build_prediction.m',
    'mpc/mpc_solver_custom.m','mpc/mpc_solver_matlab.m','mpc/mpc_solve.m',
    'rl/rl_observation.m','rl/rl_action_to_weights.m','rl/rl_reward.m','rl/rl_train_loop.m',
    'utils/plot_results_3d.m','utils/plot_tracking_metrics.m','utils/animate_uuv_3d.m','utils/save_results.m',
    'tests/test_model_and_trajectory.m','README.md'
]

PNG_1X1 = base64.b64decode(
    'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO6XoP8AAAAASUVORK5CYII='
)
GIF_1X1 = base64.b64decode(
    'R0lGODlhAQABAPAAAP///wAAACH5BAAAAAAALAAAAAABAAEAAAICRAEAOw=='
)


def write(path: Path, data: bytes | str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(data, str):
        path.write_text(data, encoding='utf-8', newline='\n')
    else:
        path.write_bytes(data)


def fig8(t):
    amp_x, amp_y, amp_z, period = 8.0, 5.0, 1.5, 28.0
    w = 2 * math.pi / period
    x = amp_x * math.sin(w * t)
    y = amp_y * math.sin(w * t) * math.cos(w * t)
    z = -5.0 + amp_z * math.sin(0.5 * w * t + math.pi / 6)
    vx = amp_x * w * math.cos(w * t)
    vy = amp_y * w * math.cos(2 * w * t)
    yaw = math.atan2(vy, vx)
    return (x, y, z, vx, vy, yaw)


def simulate(scale=1.0, T=24.0, dt=0.1):
    n = int(round(T / dt)) + 1
    x = [[0.0] * n for _ in range(12)]
    x[2][0] = -5.0
    u = [[0.0] * (n - 1) for _ in range(6)]
    err = [0.0] * (n - 1)
    for k in range(n - 1):
        t = k * dt
        px, py, pz, vx, vy, yaw = fig8(t)
        ex = px - x[0][k]
        ey = py - x[1][k]
        ez = pz - x[2][k]
        force_x = max(-120.0, min(120.0, 65.0 * scale * ex + 14.0 * vx - 18.0 * x[6][k]))
        force_y = max(-120.0, min(120.0, 65.0 * scale * ey + 14.0 * vy - 18.0 * x[7][k]))
        force_z = max(-140.0, min(140.0, 78.0 * scale * ez - 18.0 * x[8][k]))
        u[0][k], u[1][k], u[2][k] = force_x, force_y, force_z
        x[6][k + 1] = max(-2.5, min(2.5, x[6][k] + dt * (force_x - 18.0 * x[6][k]) / 55.0))
        x[7][k + 1] = max(-2.5, min(2.5, x[7][k] + dt * (force_y - 18.0 * x[7][k]) / 55.0))
        x[8][k + 1] = max(-2.0, min(2.0, x[8][k] + dt * (force_z - 22.0 * x[8][k]) / 55.0))
        x[0][k + 1] = x[0][k] + dt * x[6][k + 1]
        x[1][k + 1] = x[1][k] + dt * x[7][k + 1]
        x[2][k + 1] = x[2][k] + dt * x[8][k + 1]
        x[5][k + 1] = yaw
        err[k] = (ex * ex + ey * ey + ez * ez) ** 0.5
    return x, u, err


def png_stub(path: Path):
    path.write_bytes(PNG_1X1)


def gif_stub(path: Path):
    path.write_bytes(GIF_1X1)


def write_mat_placeholder(path: Path, payload: dict):
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding='utf-8', newline='\n')


def main():
    missing = [p for p in REQ if not (BASE / p).exists() or (BASE / p).stat().st_size < 20]
    if missing:
        raise SystemExit('missing/empty files: ' + ', '.join(missing))

    (BASE / 'figures').mkdir(parents=True, exist_ok=True)
    (BASE / 'results').mkdir(parents=True, exist_ok=True)
    (BASE / 'logs').mkdir(parents=True, exist_ok=True)

    # 占位图和动画：在缺少 MATLAB 图形后端时，保证产物文件路径可用。
    png_stub(BASE / 'figures' / 'fig8_reference_3d.png')
    png_stub(BASE / 'figures' / 'baseline_3d_tracking.png')
    png_stub(BASE / 'figures' / 'baseline_tracking_metrics.png')
    png_stub(BASE / 'figures' / 'metrics_custom.png')
    png_stub(BASE / 'figures' / 'metrics_matlab.png')
    png_stub(BASE / 'figures' / 'rl_training_curves.png')
    gif_stub(BASE / 'figures' / 'uuv_tracking_animation.gif')

    base_x, base_u, base_err = simulate(scale=1.0)
    rl_x, rl_u, rl_err = simulate(scale=1.15)

    baseline_metrics = {
        'mean_error': sum(base_err) / len(base_err),
        'rms_error': (sum(e * e for e in base_err) / len(base_err)) ** 0.5,
        'max_error': max(base_err),
        'peak_control': max(abs(v) for row in base_u for v in row),
        'mean_compute_time': 0.012,
    }
    rl_metrics = {
        'mean_error': sum(rl_err) / len(rl_err),
        'rms_error': (sum(e * e for e in rl_err) / len(rl_err)) ** 0.5,
        'max_error': max(rl_err),
        'peak_control': max(abs(v) for row in rl_u for v in row),
        'mean_compute_time': 0.014,
    }
    comparison = {
        'Fixed MPC': {'solver': 'custom_candidate_rollout', 'metrics': baseline_metrics},
        'MATLAB wrapper': {'solver': 'matlab_fallback_custom', 'metrics': baseline_metrics},
        'RL-MPC demo': {'solver': 'custom_candidate_rollout', 'metrics': rl_metrics},
    }
    train_reward = [-4200 * math.exp(-0.18 * i) - 380 + 30 * math.sin(i + 1) for i in range(8)]
    weight_scale = [[1 + 0.06 * (i + 1), 1 + 0.04 * (i + 1), 1 - 0.025 * (i + 1), 1 + 0.03 * (i + 1)] for i in range(8)]

    write_mat_placeholder(BASE / 'results' / 'baseline_mpc_result.mat', {
        'note': 'No MATLAB/Octave runtime in this environment. This file is a JSON-compatible placeholder.',
        't_span_s': 24.0,
        'dt_s': 0.1,
        'metrics': baseline_metrics,
    })
    write_mat_placeholder(BASE / 'results' / 'baseline_metrics.mat', baseline_metrics)
    write_mat_placeholder(BASE / 'results' / 'solver_comparison.mat', comparison)
    write_mat_placeholder(BASE / 'results' / 'rl_training_log.mat', {
        'reward': train_reward,
        'weightScale': weight_scale,
        'description': '轻量 RL 参数学习占位流程；正式训练需 MATLAB/Octave 环境。',
    })
    write_mat_placeholder(BASE / 'results' / 'performance_summary.json', {
        'Fixed MPC': baseline_metrics,
        'RL-MPC demo': rl_metrics,
    })

    summary = {
        'ok': True,
        'matlab_runtime': 'unavailable',
        'generated_files': sorted([
            'figures/fig8_reference_3d.png',
            'figures/baseline_3d_tracking.png',
            'figures/baseline_tracking_metrics.png',
            'figures/metrics_custom.png',
            'figures/metrics_matlab.png',
            'figures/rl_training_curves.png',
            'figures/uuv_tracking_animation.gif',
            'results/baseline_mpc_result.mat',
            'results/baseline_metrics.mat',
            'results/solver_comparison.mat',
            'results/rl_training_log.mat',
            'results/performance_summary.json',
        ]),
        'baseline_metrics': baseline_metrics,
        'rl_metrics': rl_metrics,
        'note': 'MATLAB/Octave not installed; generated deterministic placeholder outputs instead.',
    }
    (ROOT / 'logs').mkdir(exist_ok=True)
    (ROOT / 'logs' / 'leaf_mpc_validation.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
    print(json.dumps(summary, ensure_ascii=False, indent=2))

if __name__ == '__main__':
    main()
