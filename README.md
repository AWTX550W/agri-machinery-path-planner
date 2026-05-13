# 🌾 农机自动驾驶路径规划系统

> 适配中联重科/雷沃/极飞校招场景，支持弓字形覆盖路径、动态避障、路径平滑、多机协同

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## 功能特性

| 模块 | 功能 | 算法 |
|------|------|------|
| **基础路径规划** | 凸/凹多边形田块弓字形作业 | 扫描线裁剪 |
| **动态避障** | 实时障碍物绕行 | A*网格搜索 |
| **路径平滑** | 运动学约束平滑 | Catmull-Rom样条 |
| **多机协同** | 区域划分、负载均衡 | 分配算法 |
| **Web可视化** | 实时监控、参数配置 | Flask + Plotly |

## 项目结构

```
agri-robot-planner/
├── main.py                 # 主程序入口
├── requirements.txt        # 依赖列表
├── README.md              # 本文件
├── modules/
│   ├── __init__.py
│   ├── base_planner.py    # 基础路径规划
│   ├── dynamic_avoidance.py # 动态避障
│   ├── path_smoothing.py   # 路径平滑
│   └── multi_robot.py     # 多机协同
└── web/
    ├── app.py             # Flask后端
    └── templates/
        └── index.html     # 可视化前端
```

## 快速开始

### 安装依赖

```bash
pip install numpy matplotlib flask
```

### 运行完整流程

```bash
python main.py --full --field rectangle
```

### 测试单个模块

```bash
python main.py --test base      # 基础路径规划
python main.py --test dynamic    # 动态避障
python main.py --test smooth     # 路径平滑
python main.py --test multi      # 多机协同
```

### 启动Web服务

```bash
pip install flask plotly
python main.py --web --port 5000
# 访问 http://localhost:5000
```

## 使用示例

### Python API

```python
from modules.base_planner import FieldPlanner
from modules.path_smoothing import BSplineSmoother
from modules.multi_robot import MultiRobotPlanner

# 1. 基础规划
planner = FieldPlanner(working_width=5.0)
planner.load_field([(0,0), (100,0), (100,60), (0,60)])
planner.load_obstacles([((50, 30), 8)])
planner.generate_work_lines()
planner.generate_zigzag()
planner.visualize()

# 2. 平滑
smoother = BSplineSmoother(max_curvature=0.15)
smoothed, curvatures, headings = smoother.smooth(planner.path)

# 3. 多机协同
multi = MultiRobotPlanner(boundary, num_robots=3)
multi.assign_work_lines()
multi.plan_paths()
multi.visualize()
```

## 输出示例

```
[Step 1/4] 基础弓字形路径规划
[基础] 田块: 60.0m x 60.0m, 凹多边形
[基础] 生成 12 条作业线
统计: 作业线12条, 总路径595.0m, 覆盖率75.0%

[Step 2/4] 动态障碍物避障
[动态避障] 路径点数: 50

[Step 3/4] B样条路径平滑
平滑后: 300 点, 最大曲率0.12

[Step 4/4] 多机协同作业规划
农机3台, 作业线12条
  Robot 0: 4条线, 285.0m
  Robot 1: 4条线, 285.0m
  Robot 2: 4条线, 285.0m
```

## 算法详解

### 1. 弓字形路径规划
- 支持凸多边形和凹多边形
- 扫描线算法裁剪作业线
- 奇偶行交替方向遍历

### 2. 动态避障 (A*)
- 网格化田块环境
- A*寻路算法
- 障碍物膨胀处理

### 3. 路径平滑
- Catmull-Rom样条插值
- 可约束最大曲率
- 保留运动学可行性

### 4. 多机协同
- 等距区域划分
- 作业线负载均衡
- 时序冲突检测与解决

## 扩展方向

1. **实时定位**: RTK-GPS + IMU融合
2. **运动控制**: 最小转弯半径约束
3. **多机通信**: 实时状态同步
4. **地形适应**: 坡度地图路径规划
5. **能耗优化**: 续航/油耗最优

## 校招亮点

- 完整闭环的路径规划系统
- 覆盖感知→规划→控制核心链路
- 支持复杂地形和动态障碍
- 模块化设计，易于扩展
- Web可视化，便于演示

## 适用岗位

- 自动驾驶算法工程师
- 农机控制系统开发
- 农业机器人研发
- 智能农业装备

## License

MIT License
