#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
农机自动驾驶路径规划系统 - Web可视化
Flask轻量后端 + Plotly前端
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from flask import Flask, render_template, jsonify, request
from modules.base_planner import FieldPlanner
from modules.dynamic_avoidance import DynamicObstacleplanner
from modules.path_smoothing import BSplineSmoother
from modules.multi_robot import MultiRobotPlanner


app = Flask(__name__)
app.config['SECRET_KEY'] = 'agri-robot-planner-2024'

global_planner = None
global_multi_robot = None


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/api/plan', methods=['POST'])
def api_plan():
    global global_planner, global_multi_robot
    
    data = request.json
    boundary = data.get('boundary', [[0,0], [100,0], [100,60], [0,60]])
    working_width = float(data.get('working_width', 5.0))
    obstacles = data.get('obstacles', [])
    num_robots = int(data.get('num_robots', 1))
    
    if num_robots == 1:
        global_planner = FieldPlanner(working_width=working_width)
        global_planner.load_field(boundary)
        if obstacles:
            global_planner.load_obstacles([((o['x'], o['y']), o['radius']) for o in obstacles])
        global_planner.generate_work_lines()
        global_planner.generate_zigzag()
        stats = global_planner.get_stats()
        
        return jsonify({
            'success': True, 'mode': 'single',
            'path': global_planner.path,
            'work_lines': [list(s) + list(e) for s, e in global_planner.work_lines],
            'boundary': boundary, 'obstacles': obstacles,
            'stats': {'work_lines': stats.work_lines, 'total_length': stats.total_length, 'coverage_rate': stats.coverage_rate}
        })
    else:
        global_multi_robot = MultiRobotPlanner(boundary, num_robots, working_width)
        global_multi_robot.assign_work_lines()
        global_multi_robot.plan_paths()
        
        robot_paths = [{'id': r.id, 'path': r.current_path, 'assigned_lines': r.assigned_lines, 'color': r.color} 
                      for r in global_multi_robot.robots]
        
        return jsonify({
            'success': True, 'mode': 'multi', 'boundary': boundary,
            'robots': robot_paths, 'stats': global_multi_robot.get_statistics()
        })


@app.route('/api/smooth', methods=['POST'])
def api_smooth():
    data = request.json
    path = data.get('path', [])
    max_curvature = float(data.get('max_curvature', 0.15))
    
    smoother = BSplineSmoother(max_curvature=max_curvature)
    smoothed, curvatures, headings = smoother.smooth(path, num_samples=300)
    
    return jsonify({
        'success': True, 'original_path': path,
        'smoothed_path': smoothed, 'curvatures': curvatures, 'headings': headings
    })


@app.route('/api/presets', methods=['GET'])
def api_presets():
    return jsonify({
        'rectangle': {'name': '矩形田块', 'boundary': [[0,0], [100,0], [100,60], [0,60]], 'obstacles': []},
        'l_shape': {'name': 'L形田块', 'boundary': [[0,0], [60,0], [60,30], [30,30], [30,60], [0,60]], 'obstacles': []},
        'with_obstacle': {'name': '带障碍物', 'boundary': [[0,0], [100,0], [100,60], [0,60]], 'obstacles': [{'x': 50, 'y': 30, 'radius': 8}]},
        'irregular': {'name': '不规则田块', 'boundary': [[0,0], [80,5], [100,20], [90,50], [70,55], [50,80], [20,70], [5,40]], 'obstacles': [{'x': 55, 'y': 45, 'radius': 6}]}
    })


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', type=int, default=5000)
    args = parser.parse_args()
    
    print("="*50)
    print("农机路径规划 Web 可视化系统")
    print(f"访问地址: http://localhost:{args.port}")
    print("="*50)
    
    app.run(host='0.0.0.0', port=args.port, debug=True)
