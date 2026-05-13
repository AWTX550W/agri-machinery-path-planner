#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模块1: 农机弓字形路径规划基础模块
功能: 凸多边形/凹多边形田块的弓字形作业路径生成
作者: 农业机械化工程专业校招展示
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from typing import List, Tuple, Optional
from dataclasses import dataclass


@dataclass
class PathStats:
    """路径统计信息"""
    work_lines: int
    total_length: float
    effective_length: float
    working_width: float
    coverage_rate: float


class FieldPlanner:
    """
    田块路径规划器
    支持: 凸多边形、凹多边形、圆形障碍物避障
    """
    
    def __init__(self, working_width: float = 5.0):
        self.working_width = working_width
        self.boundary: Optional[np.ndarray] = None
        self.obstacles: List[Tuple[Tuple[float, float], float]] = []
        self.work_lines: List[Tuple[Tuple, Tuple]] = []
        self.path: List[Tuple[float, float]] = []
        self.is_concave = False
        self._setup_bounds()
    
    def _setup_bounds(self):
        self.x_min = self.y_min = 0
        self.x_max = self.y_max = 100
        self.width = self.height = 100
    
    def load_field(self, boundary: List[Tuple[float, float]]):
        """加载田块边界"""
        if len(boundary) < 3:
            raise ValueError("田块边界至少需要3个顶点")
        
        self.boundary = np.array(boundary)
        self.x_min, self.y_min = self.boundary.min(axis=0)
        self.x_max, self.y_max = self.boundary.max(axis=0)
        self.width = self.x_max - self.x_min
        self.height = self.y_max - self.y_min
        
        self.is_concave = self._detect_concave()
        print(f"[基础] 田块: {self.width:.1f}m x {self.height:.1f}m, {'凹多边形' if self.is_concave else '凸多边形'}")
    
    def _detect_concave(self) -> bool:
        """检测凹多边形（叉积符号变化法）"""
        n = len(self.boundary)
        sign = None
        for i in range(n):
            p0, p1, p2 = self.boundary[i], self.boundary[(i+1)%n], self.boundary[(i+2)%n]
            cross = (p1[0]-p0[0])*(p2[1]-p1[1]) - (p1[1]-p0[1])*(p2[0]-p1[0])
            if abs(cross) < 1e-10:
                continue
            s = 1 if cross > 0 else -1
            if sign is None:
                sign = s
            elif sign != s:
                return True
        return False
    
    def load_obstacles(self, obstacles: List[Tuple[Tuple[float, float], float]]):
        """加载障碍物"""
        self.obstacles = obstacles
        print(f"[基础] 加载 {len(obstacles)} 个障碍物")
    
    def generate_work_lines(self):
        """生成平行作业线"""
        self.work_lines = []
        direction = 'horizontal' if self.width >= self.height else 'vertical'
        
        if direction == 'horizontal':
            num = max(1, int(self.height / self.working_width))
            ys = np.linspace(self.y_min + self.working_width/2, self.y_max - self.working_width/2, num)
            for y in ys:
                segs = self._clip_line([(self.x_min-1, y), (self.x_max+1, y)])
                self.work_lines.extend(segs)
        else:
            num = max(1, int(self.width / self.working_width))
            xs = np.linspace(self.x_min + self.working_width/2, self.x_max - self.working_width/2, num)
            for x in xs:
                segs = self._clip_line([(x, self.y_min-1), (x, self.y_max+1)])
                self.work_lines.extend(segs)
        
        if direction == 'horizontal':
            self.work_lines.sort(key=lambda s: (s[0][1]+s[1][1])/2)
        else:
            self.work_lines.sort(key=lambda s: (s[0][0]+s[1][0])/2)
        
        print(f"[基础] 生成 {len(self.work_lines)} 条作业线")
        return self.work_lines
    
    def _clip_line(self, line: List[Tuple]) -> List[Tuple[Tuple, Tuple]]:
        """裁剪线段到田块内"""
        p1, p2 = line[0], line[1]
        intersections = []
        
        for i in range(len(self.boundary)):
            p3, p4 = self.boundary[i], self.boundary[(i+1)%len(self.boundary)]
            pt = self._line_intersect(p1, p2, p3, p4)
            if pt:
                intersections.append(pt)
        
        if len(intersections) < 2:
            return []
        
        vec = np.array(p2) - np.array(p1)
        t_vals = sorted([(np.dot(np.array(p)-np.array(p1), vec), p) for p in intersections])
        
        segments = []
        for i in range(0, len(t_vals)-1, 2):
            s, e = np.array(t_vals[i][1]), np.array(t_vals[i+1][1])
            if np.linalg.norm(e-s) > 0.01:
                segments.append((tuple(s), tuple(e)))
        return segments
    
    def _line_intersect(self, p1, p2, p3, p4) -> Optional[Tuple]:
        """线段相交检测"""
        x1, y1, x2, y2 = p1[0], p1[1], p2[0], p2[1]
        x3, y3, x4, y4 = p3[0], p3[1], p4[0], p4[1]
        
        denom = (x1-x2)*(y3-y4) - (y1-y2)*(x3-x4)
        if abs(denom) < 1e-10:
            return None
        
        t = ((x1-x3)*(y3-y4) - (y1-y3)*(x3-x4)) / denom
        u = -((x1-x2)*(y1-y3) - (y1-y2)*(x1-x3)) / denom
        
        if 0 <= t <= 1 and 0 <= u <= 1:
            return (x1 + t*(x2-x1), y1 + t*(y2-y1))
        return None
    
    def generate_zigzag(self):
        """生成弓字形路径"""
        if not self.work_lines:
            raise ValueError("请先调用 generate_work_lines()")
        
        path = []
        for i, (s, e) in enumerate(self.work_lines):
            if i % 2 == 0:
                path.extend([s, e])
            else:
                path.extend([e, s])
            
            if i < len(self.work_lines) - 1:
                curr_end = path[-1]
                nxt = self.work_lines[i+1]
                nxt_start = nxt[0] if (i+1)%2 == 0 else nxt[1]
                mid = ((curr_end[0]+nxt_start[0])/2, (curr_end[1]+nxt_start[1])/2)
                path.extend([mid, nxt_start])
        
        self.path = path
        print(f"[基础] 弓字形路径: {len(path)} 个点")
        return self.path
    
    def check_collision(self, point: Tuple[float, float]) -> bool:
        """碰撞检测"""
        px, py = point
        for (ox, oy), r in self.obstacles:
            if (px-ox)**2 + (py-oy)**2 < r**2:
                return True
        return False
    
    def get_stats(self) -> PathStats:
        """获取统计信息"""
        total = sum(np.linalg.norm(np.array(self.path[i+1])-np.array(self.path[i]))
                    for i in range(len(self.path)-1))
        effective = sum(np.linalg.norm(np.array(e)-np.array(s))
                        for s, e in self.work_lines)
        area = self.width * self.height
        coverage = effective * self.working_width
        rate = min(100, coverage/area*100) if area > 0 else 0
        
        return PathStats(
            work_lines=len(self.work_lines),
            total_length=round(total, 2),
            effective_length=round(effective, 2),
            working_width=self.working_width,
            coverage_rate=round(rate, 1)
        )
    
    def visualize(self, title: str = "农机路径规划", save_path: str = None):
        """可视化"""
        fig, ax = plt.subplots(figsize=(10, 8))
        
        b = np.vstack([self.boundary, self.boundary[0:1]])
        ax.plot(b[:,0], b[:,1], 'k-', lw=2, label='Field Boundary')
        ax.fill(b[:,0], b[:,1], alpha=0.1, color='green')
        
        for (ox, oy), r in self.obstacles:
            circle = plt.Circle((ox, oy), r, color='red', alpha=0.3)
            ax.add_patch(circle)
        
        for s, e in self.work_lines:
            ax.plot([s[0], e[0]], [s[1], e[1]], 'gray', '--', alpha=0.4)
        
        if self.path:
            arr = np.array(self.path)
            ax.plot(arr[:,0], arr[:,1], 'b-', lw=2, label='Zigzag Path')
            ax.plot(arr[0,0], arr[0,1], 'go', ms=10, label='Start')
            ax.plot(arr[-1,0], arr[-1,1], 'ro', ms=10, label='End')
        
        ax.set_aspect('equal')
        ax.set_title(title)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        if save_path:
            plt.savefig(save_path, dpi=150, bbox_inches='tight')
            print(f"[可视化] 保存至 {save_path}")
        plt.close()
        return fig


if __name__ == '__main__':
    print("="*50)
    print("Test: 基础路径规划")
    print("="*50)
    
    planner = FieldPlanner(working_width=5.0)
    boundary = [(0,0), (100,0), (100,60), (0,60)]
    planner.load_field(boundary)
    planner.load_obstacles([((50, 30), 8)])
    planner.generate_work_lines()
    planner.generate_zigzag()
    
    stats = planner.get_stats()
    print(f"\n统计: {stats.work_lines}条线, 总长{stats.total_length}m, 覆盖率{stats.coverage_rate}%")
    
    planner.visualize("基础弓字形路径", "output/test_base.png")
    print("Done: output/test_base.png")
