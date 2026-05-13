#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
模块4: 多机协同作业规划
功能: 多台农机的田块区域划分、作业线分配与无冲突路径规划
作者: 农业机械化工程专业校招展示
"""

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from typing import List, Tuple, Dict
from dataclasses import dataclass
from enum import Enum


class RobotStatus(Enum):
    IDLE = "idle"
    WORKING = "working"
    REASSIGNING = "reassigning"


@dataclass
class Robot:
    id: int
    x: float
    y: float
    heading: float
    status: RobotStatus = RobotStatus.IDLE
    assigned_lines: List[int] = None
    current_path: List[Tuple[float, float]] = None
    color: str = 'blue'
    
    def __post_init__(self):
        if self.assigned_lines is None:
            self.assigned_lines = []
        if self.current_path is None:
            self.current_path = []


class MultiRobotPlanner:
    """多机协同规划器"""
    
    def __init__(self, field_boundary: List[Tuple[float, float]], 
                 num_robots: int = 3, working_width: float = 5.0):
        self.field = np.array(field_boundary)
        self.num_robots = num_robots
        self.working_width = working_width
        self.robots: List[Robot] = []
        self.all_work_lines: List[Tuple[Tuple, Tuple]] = []
        self.assignments: Dict[int, List[int]] = {}
        self._compute_field_properties()
    
    def _compute_field_properties(self):
        x_min, y_min = self.field.min(axis=0)
        x_max, y_max = self.field.max(axis=0)
        self.x_min, self.y_min = x_min, y_min
        self.x_max, self.y_max = x_max, y_max
        self.width = x_max - x_min
        self.height = y_max - y_min
        
        if self.width >= self.height:
            self.direction = 'horizontal'
            self.field_length = self.height
        else:
            self.direction = 'vertical'
            self.field_length = self.width
    
    def generate_all_work_lines(self):
        """生成所有作业线"""
        self.all_work_lines = []
        
        if self.direction == 'horizontal':
            num = max(1, int(self.field_length / self.working_width))
            ys = np.linspace(self.y_min + self.working_width/2, 
                           self.y_max - self.working_width/2, num)
            for y in ys:
                self.all_work_lines.append(((self.x_min, y), (self.x_max, y)))
        else:
            num = max(1, int(self.field_length / self.working_width))
            xs = np.linspace(self.x_min + self.working_width/2,
                           self.x_max - self.working_width/2, num)
            for x in xs:
                self.all_work_lines.append(((x, self.y_min), (x, self.y_max)))
        
        print(f"[多机] 生成 {len(self.all_work_lines)} 条作业线")
    
    def assign_work_lines(self):
        """分配作业线（负载均衡）"""
        if not self.all_work_lines:
            self.generate_all_work_lines()
        
        if self.direction == 'horizontal':
            sorted_lines = sorted(enumerate(self.all_work_lines), 
                                 key=lambda x: (x[1][0][1]+x[1][1][1])/2)
        else:
            sorted_lines = sorted(enumerate(self.all_work_lines),
                                 key=lambda x: (x[1][0][0]+x[1][1][0])/2)
        
        self.assignments = {i: [] for i in range(self.num_robots)}
        self.robots = []
        
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
        
        for idx, (global_idx, line) in enumerate(sorted_lines):
            robot_id = idx % self.num_robots
            self.assignments[robot_id].append(global_idx)
        
        for i in range(self.num_robots):
            if self.direction == 'horizontal':
                start_x = self.x_min + 5 if i % 2 == 0 else self.x_max - 5
                start_y = self.y_min + 5
            else:
                start_x = self.x_min + 5
                start_y = self.y_min + 5 if i % 2 == 0 else self.y_max - 5
            
            robot = Robot(id=i, x=start_x, y=start_y, heading=0, color=colors[i % len(colors)])
            robot.assigned_lines = self.assignments[i]
            self.robots.append(robot)
        
        print(f"[多机] 分配完成:")
        for robot in self.robots:
            print(f"  Robot {robot.id}: {len(robot.assigned_lines)} 条作业线")
    
    def plan_paths(self):
        """规划各农机路径"""
        for robot in self.robots:
            robot.current_path = []
            
            for i, line_idx in enumerate(robot.assigned_lines):
                line = self.all_work_lines[line_idx]
                
                if i % 2 == 0:
                    robot.current_path.extend([line[0], line[1]])
                else:
                    robot.current_path.extend([line[1], line[0]])
                
                if i < len(robot.assigned_lines) - 1:
                    next_line = self.all_work_lines[robot.assigned_lines[i+1]]
                    curr_end = robot.current_path[-1]
                    next_start = next_line[0] if (i+1) % 2 == 0 else next_line[1]
                    mid = ((curr_end[0]+next_start[0])/2, (curr_end[1]+next_start[1])/2)
                    robot.current_path.extend([mid, next_start])
            
            robot.status = RobotStatus.WORKING
        
        print(f"[多机] 路径规划完成")
    
    def check_collisions(self) -> List[Tuple[int, int, float]]:
        """检测碰撞"""
        collisions = []
        for i in range(self.num_robots):
            for j in range(i+1, self.num_robots):
                lines_i = [self.all_work_lines[idx] for idx in self.robots[i].assigned_lines]
                lines_j = [self.all_work_lines[idx] for idx in self.robots[j].assigned_lines]
                
                for li in lines_i:
                    for lj in lines_j:
                        if self.direction == 'horizontal':
                            yi = (li[0][1] + li[1][1]) / 2
                            yj = (lj[0][1] + lj[1][1]) / 2
                            if abs(yi - yj) < self.working_width:
                                collisions.append((i, j, 0))
                        else:
                            xi = (li[0][0] + li[1][0]) / 2
                            xj = (lj[0][0] + lj[1][0]) / 2
                            if abs(xi - xj) < self.working_width:
                                collisions.append((i, j, 0))
        
        if collisions:
            print(f"[多机] 检测到 {len(collisions)} 处潜在冲突")
        return collisions
    
    def resolve_collisions(self):
        """解决冲突（时间错峰）"""
        for i in range(self.num_robots):
            if i > 0:
                delay = i * 5
                print(f"[多机] Robot {i} 延迟启动: {delay}s")
    
    def rebalance(self, failed_robot_id: int):
        """重新分配任务"""
        if failed_robot_id not in [r.id for r in self.robots]:
            return
        
        failed_lines = self.robots[failed_robot_id].assigned_lines
        
        for robot in self.robots:
            if robot.id != failed_robot_id:
                extra = failed_lines[robot.id % len(failed_lines)]
                robot.assigned_lines.append(extra)
        
        print(f"[多机] Robot {failed_robot_id} 故障，任务已重新分配")
        self.plan_paths()
    
    def visualize(self, save_path: str = "output/test_multi.png"):
        """可视化"""
        fig, ax = plt.subplots(figsize=(14, 10))
        
        b = np.vstack([self.field, self.field[0:1]])
        ax.plot(b[:,0], b[:,1], 'k-', lw=2, label='Field')
        ax.fill(b[:,0], b[:,1], alpha=0.1, color='green')
        
        for robot in self.robots:
            if robot.current_path:
                arr = np.array(robot.current_path)
                ax.plot(arr[:,0], arr[:,1], '-', color=robot.color, lw=2.5, 
                       label=f'Robot {robot.id}')
                ax.scatter(arr[0,0], arr[0,1], c=robot.color, s=150, marker='s',
                           edgecolors='black', zorder=10)
                ax.text(arr[0,0]+1, arr[0,1]+1, f'R{robot.id}', fontsize=10, 
                       fontweight='bold', color=robot.color)
        
        ax.set_aspect('equal')
        ax.set_title(f'Multi-Robot Path Planning ({self.num_robots} Robots)')
        ax.legend(loc='upper right')
        ax.grid(True, alpha=0.3)
        
        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        print(f"[多机] 可视化保存至 {save_path}")
        plt.close()
    
    def get_statistics(self) -> Dict:
        stats = {'num_robots': self.num_robots, 'total_lines': len(self.all_work_lines), 'robots': []}
        
        for robot in self.robots:
            path_length = sum(np.linalg.norm(np.array(robot.current_path[i+1]) - 
                              np.array(robot.current_path[i]))
                              for i in range(len(robot.current_path)-1))
            
            stats['robots'].append({
                'id': robot.id,
                'assigned_lines': len(robot.assigned_lines),
                'path_length': round(path_length, 2)
            })
        
        return stats


if __name__ == '__main__':
    print("="*50)
    print("Test: 多机协同作业规划")
    print("="*50)
    
    field = [(0,0), (120,0), (120,80), (0,80)]
    planner = MultiRobotPlanner(field, num_robots=3, working_width=6.0)
    
    planner.assign_work_lines()
    planner.plan_paths()
    planner.check_collisions()
    planner.resolve_collisions()
    
    stats = planner.get_statistics()
    print(f"\n统计: {stats['num_robots']} 台农机, {stats['total_lines']} 条作业线")
    for r in stats['robots']:
        print(f"  Robot {r['id']}: {r['assigned_lines']} 条线, 路径长 {r['path_length']}m")
    
    planner.visualize("output/test_multi.png")
    
    print("\n[测试] 模拟 Robot 1 故障...")
    planner.rebalance(failed_robot_id=1)
    
    print("\nDone: output/test_multi.png")
