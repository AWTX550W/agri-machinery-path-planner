#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模块3: 路径平滑与运动学约束 (三次B样条)
功能: 对离散路径点进行平滑，满足农机最大转向角/曲率限制
作者: 农业机械化工程专业校招展示
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from typing import List, Tuple


class BSplineSmoother:
    """三次B样条路径平滑器"""
    
    def __init__(self, max_curvature: float = 0.15, max_steering_angle: float = 30.0):
        self.max_curvature = max_curvature
        self.max_steering_angle = np.radians(max_steering_angle)
        self.vehicle_wheelbase = 2.5
    
    def smooth(self, control_points: List[Tuple[float, float]], 
               num_samples: int = 300) -> Tuple[List[Tuple], List[float], List[float]]:
        """平滑路径"""
        if len(control_points) < 4:
            control_points = self._interpolate(control_points, 10)
        
        pts = np.array(control_points)
        n = len(pts)
        
        # 均匀采样
        t_values = np.linspace(0, 1, num_samples)
        
        # 简单参数化曲线（Catmull-Rom转B样条效果）
        x_vals, y_vals = [], []
        for t in t_values:
            idx = int(t * (n - 1))
            idx = min(idx, n - 2)
            local_t = (t * (n - 1)) - idx
            
            # 三次多项式插值
            p0, p1 = pts[max(0, idx-1)], pts[min(idx, n-1)]
            p2, p3 = pts[min(idx+1, n-1)], pts[min(idx+2, n-1)]
            
            t2, t3 = local_t**2, local_t**3
            x = 0.5 * ((2*p1[0] + (-p0[0]+p2[0])*local_t + 
                       (2*p0[0]-5*p1[0]+4*p2[0]-p3[0])*t2 + 
                       (-p0[0]+3*p1[0]-3*p2[0]+p3[0])*t3))
            y = 0.5 * ((2*p1[1] + (-p1[1]+p2[1])*local_t + 
                       (2*p1[1]-5*p2[1]+4*p3[1]-p2[1])*t2 + 
                       (-p1[1]+3*p2[1]-3*p3[1]+p2[1])*t3))
            x_vals.append(x)
            y_vals.append(y)
        
        smoothed = list(zip(x_vals, y_vals))
        curvatures = self._calculate_curvature(smoothed)
        headings = self._calculate_heading(smoothed)
        
        violations = sum(1 for c in curvatures if abs(c) > self.max_curvature)
        if violations > 0:
            print(f"[B样条] 警告: {violations} 个点超出最大曲率限制")
        
        return smoothed, curvatures, headings
    
    def _interpolate(self, points: List[Tuple], num: int) -> List[Tuple]:
        """线性插值加密点"""
        if len(points) < 2:
            return points
        result = []
        for i in range(len(points) - 1):
            segs = num // (len(points) - 1)
            for t in np.linspace(0, 1, segs):
                x = points[i][0] + t * (points[i+1][0] - points[i][0])
                y = points[i][1] + t * (points[i+1][1] - points[i][1])
                result.append((x, y))
        result.append(points[-1])
        return result
    
    def _calculate_curvature(self, path: List[Tuple]) -> List[float]:
        """计算路径曲率"""
        if len(path) < 3:
            return [0.0] * len(path)
        
        k = 0.5
        curvatures = []
        
        for i in range(len(path)):
            if i < len(path) - 1:
                dx1 = path[i+1][0] - path[i][0]
                dy1 = path[i+1][1] - path[i][1]
            else:
                dx1, dy1 = path[i][0] - path[i-1][0], path[i][1] - path[i-1][1]
            
            if i > 0:
                dx2 = path[i][0] - path[i-1][0]
                dy2 = path[i][1] - path[i-1][1]
            else:
                dx2, dy2 = dx1, dy1
            
            dx = k * dx1 + (1-k) * dx2
            dy = k * dy1 + (1-k) * dy2
            ddx = dx1 - dx2
            ddy = dy1 - dy2
            
            denom = (dx**2 + dy**2)**1.5
            if abs(denom) < 1e-10:
                curvatures.append(0.0)
            else:
                curvatures.append(abs(ddx*dy - ddy*dx) / denom)
        
        return curvatures
    
    def _calculate_heading(self, path: List[Tuple]) -> List[float]:
        """计算航向角"""
        if len(path) < 2:
            return [0.0] * len(path)
        
        headings = [0.0]
        for i in range(1, len(path)):
            dx = path[i][0] - path[i-1][0]
            dy = path[i][1] - path[i-1][1]
            headings.append(np.arctan2(dy, dx))
        return headings
    
    def visualize(self, original: List[Tuple], smoothed: List[Tuple],
                  curvatures: List[float], headings: List[float],
                  save_path: str = "output/test_smooth.png"):
        """可视化"""
        fig, axes = plt.subplots(2, 2, figsize=(14, 12))
        
        # 路径对比
        ax = axes[0, 0]
        orig_arr = np.array(original)
        smooth_arr = np.array(smoothed)
        ax.plot(orig_arr[:,0], orig_arr[:,1], 'r--', lw=1.5, alpha=0.6, label='Original')
        ax.plot(smooth_arr[:,0], smooth_arr[:,1], 'b-', lw=2, label='Smoothed')
        ax.scatter(orig_arr[::5,0], orig_arr[::5,1], c='red', s=30, zorder=5, label='Control Points')
        ax.set_title('Path Comparison')
        ax.legend()
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        
        # 曲率变化
        ax = axes[0, 1]
        s = np.arange(len(curvatures)) * 100 / len(curvatures)
        ax.plot(s, curvatures, 'g-', lw=2)
        ax.axhline(self.max_curvature, color='r', linestyle='--', label=f'Max: {self.max_curvature}')
        ax.set_title('Curvature Profile')
        ax.set_xlabel('Path Progress (%)')
        ax.set_ylabel('Curvature (1/m)')
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        # 曲率热力图
        ax = axes[1, 0]
        scatter = ax.scatter(smooth_arr[:,0], smooth_arr[:,1], c=curvatures, 
                           cmap='RdYlGn_r', s=20, vmin=0, vmax=self.max_curvature*2)
        plt.colorbar(scatter, ax=ax, label='Curvature')
        ax.set_title('Curvature Heatmap')
        ax.set_aspect('equal')
        ax.grid(True, alpha=0.3)
        
        # 航向角
        ax = axes[1, 1]
        ax.plot(s, np.degrees(headings), 'purple', lw=2)
        ax.set_title('Heading Angle Profile')
        ax.set_xlabel('Path Progress (%)')
        ax.set_ylabel('Heading (degrees)')
        ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"[B样条] 平滑结果保存至 {save_path}")
        plt.close()


if __name__ == '__main__':
    print("="*50)
    print("Test: B样条路径平滑")
    print("="*50)
    
    # 生成测试路径
    path = []
    for y in np.linspace(5, 55, 6):
        if len(path) % 2 == 0:
            path.extend([(10, y), (90, y)])
        else:
            path.extend([(90, y), (10, y)])
    
    np.random.seed(42)
    noisy_path = [(x + np.random.randn()*0.5, y + np.random.randn()*0.5) for x, y in path]
    
    print(f"[测试] 原始路径: {len(noisy_path)} 个点")
    
    smoother = BSplineSmoother(max_curvature=0.15, max_steering_angle=30)
    smoothed, curvatures, headings = smoother.smooth(noisy_path, num_samples=300)
    
    print(f"[测试] 平滑路径: {len(smoothed)} 个点")
    print(f"[测试] 最大曲率: {max(curvatures):.4f}")
    
    smoother.visualize(noisy_path, smoothed, curvatures, headings, "output/test_smooth.png")
    print("Done: output/test_smooth.png")
