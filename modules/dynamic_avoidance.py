#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模块2: 动态障碍物实时避障 (简化版A*算法)
功能: 动态障碍物出现时实时重规划
作者: 农业机械化工程专业校招展示
"""

import numpy as np
from typing import List, Tuple, Optional
import heapq


class DynamicObstacleplanner:
    """动态障碍物规划器"""
    
    def __init__(self, base_planner):
        self.base = base_planner
        self.resolution = 3.0  # 网格分辨率
        self.path = []
        self.obstacles_active: List[Tuple[float, float, float]] = []
        self._init_grid()
    
    def _init_grid(self):
        self.x_min = self.base.x_min - 5
        self.y_min = self.base.y_min - 5
        self.x_max = self.base.x_max + 5
        self.y_max = self.base.y_max + 5
        self.width = int((self.x_max - self.x_min) / self.resolution)
        self.height = int((self.y_max - self.y_min) / self.resolution)
        self.grid = np.zeros((self.height, self.width))
        self._mark_field_boundary()
    
    def _mark_field_boundary(self):
        """标记田块边界外的区域为障碍"""
        for y in range(self.height):
            for x in range(self.width):
                px = self.x_min + x * self.resolution
                py = self.y_min + y * self.resolution
                if not self._point_in_polygon(px, py):
                    self.grid[y, x] = 1
    
    def _point_in_polygon(self, x: float, y: float) -> bool:
        """射线法判断点是否在多边形内"""
        poly = self.base.boundary
        n = len(poly)
        inside = False
        p1x, p1y = poly[0]
        for i in range(1, n + 1):
            p2x, p2y = poly[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
        return inside
    
    def _coord_to_grid(self, x: float, y: float) -> Tuple[int, int]:
        gx = int((x - self.x_min) / self.resolution)
        gy = int((y - self.y_min) / self.resolution)
        return max(0, min(gx, self.width-1)), max(0, min(gy, self.height-1))
    
    def _grid_to_coord(self, gx: int, gy: int) -> Tuple[float, float]:
        return self.x_min + gx * self.resolution, self.y_min + gy * self.resolution
    
    def _mark_obstacles(self):
        """标记障碍物"""
        # 静态障碍物
        for (ox, oy), r in self.base.obstacles:
            self._mark_circle(ox, oy, r + 2)
        # 动态障碍物
        for ox, oy, r in self.obstacles_active:
            self._mark_circle(ox, oy, r + 2)
    
    def _mark_circle(self, cx: float, cy: float, radius: float):
        gcx, gcy = self._coord_to_grid(cx, cy)
        gr = int(radius / self.resolution) + 1
        for dy in range(-gr, gr+1):
            for dx in range(-gr, gr+1):
                nx, ny = gcx + dx, gcy + dy
                if 0 <= nx < self.width and 0 <= ny < self.height:
                    if dx*dx + dy*dy <= gr*gr:
                        self.grid[ny, nx] = 1
    
    def _heuristic(self, a: Tuple[int, int], b: Tuple[int, int]) -> float:
        return abs(a[0] - b[0]) + abs(a[1] - b[1])
    
    def _get_neighbors(self, node: Tuple[int, int]) -> List[Tuple[int, int]]:
        dirs = [(-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1)]
        result = []
        for dx, dy in dirs:
            nx, ny = node[0]+dx, node[1]+dy
            if 0 <= nx < self.width and 0 <= ny < self.height:
                if self.grid[ny, nx] == 0:
                    result.append((nx, ny))
        return result
    
    def _a_star(self, start: Tuple[int, int], goal: Tuple[int, int]) -> List[Tuple[int, int]]:
        """A*寻路"""
        open_set = []
        heapq.heappush(open_set, (0, start))
        came_from = {}
        g_score = {start: 0}
        
        while open_set:
            _, current = heapq.heappop(open_set)
            
            if current == goal:
                # 重建路径
                path = [current]
                while current in came_from:
                    current = came_from[current]
                    path.append(current)
                return path[::-1]
            
            for neighbor in self._get_neighbors(current):
                tentative_g = g_score[current] + 1
                if neighbor not in g_score or tentative_g < g_score[neighbor]:
                    came_from[neighbor] = current
                    g_score[neighbor] = tentative_g
                    f_score = tentative_g + self._heuristic(neighbor, goal)
                    heapq.heappush(open_set, (f_score, neighbor))
        
        return []
    
    def plan(self, start: Tuple[float, float], goal: Tuple[float, float], 
             dynamic_obstacles: List[Tuple[float, float, float]] = None):
        """规划路径"""
        # 重新初始化网格
        self._init_grid()
        
        # 标记障碍物
        self.obstacles_active = dynamic_obstacles or []
        self._mark_obstacles()
        
        # 坐标转换
        start_grid = self._coord_to_grid(*start)
        goal_grid = self._coord_to_grid(*goal)
        
        # A*寻路
        grid_path = self._a_star(start_grid, goal_grid)
        
        # 转换回坐标
        self.path = [self._grid_to_coord(gx, gy) for gx, gy in grid_path]
        
        return self.path
    
    def visualize_comparison(self, save_path: str = "output/test_dynamic.png"):
        """可视化对比"""
        import matplotlib.pyplot as plt
        
        fig, axes = plt.subplots(1, 2, figsize=(16, 7))
        
        # 左图：无障碍路径
        ax = axes[0]
        self._plot_scene(ax, title="Original Path")
        
        # 右图：动态避障
        ax = axes[1]
        if self.obstacles_active:
            self._init_grid()
            self._mark_obstacles()
        self._plot_scene(ax, title="Dynamic Avoidance")
        
        plt.tight_layout()
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"[动态避障] 对比图保存至 {save_path}")
        plt.close()
    
    def _plot_scene(self, ax, title: str = ""):
        """绘制场景"""
        import matplotlib.pyplot as plt
        b = np.vstack([self.base.boundary, self.base.boundary[0:1]])
        ax.plot(b[:,0], b[:,1], 'k-', lw=2)
        ax.fill(b[:,0], b[:,1], alpha=0.1, color='green')
        
        for (ox, oy), r in self.base.obstacles:
            circle = plt.Circle((ox, oy), r, color='gray', alpha=0.4)
            ax.add_patch(circle)
        
        for ox, oy, r in self.obstacles_active:
            circle = plt.Circle((ox, oy), r, color='red', alpha=0.5)
            ax.add_patch(circle)
        
        if self.path and len(self.path) > 1:
            arr = np.array(self.path)
            ax.plot(arr[:,0], arr[:,1], 'b-', lw=2, label='Path')
        
        ax.set_aspect('equal')
        ax.set_title(title)
        ax.grid(True, alpha=0.3)


if __name__ == '__main__':
    print("="*50)
    print("Test: 动态障碍物避障")
    print("="*50)
    
    from base_planner import FieldPlanner
    
    base = FieldPlanner(working_width=5.0)
    base.load_field([(0,0), (100,0), (100,60), (0,60)])
    base.generate_work_lines()
    
    planner = DynamicObstacleplanner(base)
    path = planner.plan((10, 5), (90, 55), [(50, 30, 8)])
    
    print(f"[动态避障] 路径点数: {len(path)}")
    planner.visualize_comparison("output/test_dynamic.png")
    print("Done: output/test_dynamic.png")
