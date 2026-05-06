# OpenClaw Works - 智能工具与自动化解决方案集合

> 🔧 AI 驱动的工作自动化平台，支持 Android 设备控制、数据采集、农业智能化

[![MIT License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 📚 项目总览

本仓库是一个**多功能工具集**，涵盖以下领域：

| 领域 | 项目 | 描述 |
|------|------|------|
| 🤖 **AI 农业** | [harvesting-robot](#-采摘机器人) | 采摘机器人路径规划、成熟度检测、播种优化 |
| 🛒 **电商同步** | [a2hmarket-sync](#-a2hmarket订单同步) | A2H Market 订单数据同步 |
| 📱 **设备自动化** | [skills](#-android设备自动化) | 基于 AI 视觉的 Android 手机自动化 |
| 📊 **数据采集** | [wechat-crawler](#-微信公众号爬虫) | 微信公众号文章数据采集 |
| ⚙️ **开发工具** | [openclaw-installer](#-openclaw安装助手) | OpenClaw 开发环境一键安装 |

---

## 🌾 采摘机器人

**目录**: `harvesting-robot/`

农业智能机器人的核心算法集，从播种到采摘的全流程自动化。

### 核心模块

| 文件 | 功能 |
|------|------|
| `harvesting_robot_planner.py` | 采摘路径规划 + 农民路径预测 |
| `fruit_maturity_detector.py` | 果实成熟度检测 (HSV颜色分析) |
| `smart_sowing_planner.py` | 智能播种规划 |
| `real_data_interface.py` | GPS/传感器数据接口 |

### 快速开始

```python
from harvesting_robot_planner import HarvestingRobotPlanner, FruitTarget

planner = HarvestingRobotPlanner()
targets = [
    FruitTarget(x=1.2, y=0.5, z=1.8, radius=0.04, maturity=0.85),
]
path = planner.plan_path(targets)
```

### 主要特性
- 🎯 **路径规划**: 最近邻 + 贪心优化算法
- 👁️ **成熟度检测**: HSV 颜色空间分析
- 🛡️ **农民避障**: GPS 轨迹预测 + 碰撞检测
- 🌱 **播种优化**: 密度计算 + 作物参数库

📖 **[子项目详细文档](harvesting-robot/README.md)**

---

## 🛒 A2HMarket 订单同步

**目录**: `a2hmarket-sync/`

A2H Market 电商平台的订单数据同步工具，支持 AI Agent 自动买卖。

### 功能特性
- 📦 订单数据自动同步
- 🤖 AI Agent 自主下单
- 💬 支持 AI-Human 对齐
- 🔄 自动协商与交易确认

### 快速开始

```bash
# 安装依赖
pip install -r requirements.txt

# 配置 API 密钥
cp config.example.py config.py
# 编辑 config.py 填入 API 密钥

# 运行同步
python sync.py
```

📖 **[子项目详细文档](a2hmarket-sync/README.md)**

---

## 📱 Android 设备自动化

**文件**: `skills` (Skill 格式)

基于 AI 视觉的 Android 设备自动化工具，通过视觉识别控制手机 App。

### 技术栈
- 🤖 **Midscene**: AI 视觉控制框架
- 📷 **ADB**: Android 调试桥接
- 🖼️ **智谱 GLM-4V-Flash**: 免费视觉模型

### 前置要求
- Android 设备或模拟器 (启用 USB 调试)
- Node.js v18+
- Python 3.8+
- ADB 工具

### 配置示例 (.env)
```bash
MIDSCENE_MODEL_API_KEY=你的智谱AI密钥
MIDSCENE_MODEL_NAME=glm-4v-flash
MIDSCENE_MODEL_BASE_URL=https://open.bigmodel.cn/
```

📖 **[技能完整文档](SKILL.md)**

---

## 📊 微信公众号爬虫

**目录**: `wechat-crawler/`

微信公众号文章数据采集工具，支持定时抓取与存储。

### 功能特性
- 🔍 关键词搜索文章
- 📝 自动提取标题、作者、正文
- 🗓️ 支持历史消息检索
- 🐳 Docker 部署支持

### 快速开始

```bash
# Docker 部署
docker-compose up -d

# 或手动运行
pip install -r requirements.txt
python crawler.py --keyword "人工智能"
```

📖 **[子项目详细文档](wechat-crawler/README.md)**

---

## ⚙️ OpenClaw 安装助手

**目录**: `openclaw-installer/`

OpenClaw 开发环境一键安装脚本。

### 支持功能
- 🐍 Python 环境配置
- 📦 常用依赖自动安装
- 🔧 开发工具链初始化
- 🌐 网络代理配置

### 使用方法

```bash
# 下载安装脚本
curl -fsSL https://raw.githubusercontent.com/AWTX550W/openclaw-works/main/openclaw-installer/install.sh | bash

# 或手动运行
chmod +x install.sh
./install.sh
```

📖 **[子项目详细文档](openclaw-installer/README.md)**

---

## 📂 完整目录结构

```
openclaw-works/
├── 🌾 harvesting-robot/          # 采摘机器人算法
│   ├── harvesting_robot_planner.py
│   ├── fruit_maturity_detector.py
│   ├── smart_sowing_planner.py
│   └── real_data_interface.py
│
├── 🛒 a2hmarket-sync/           # 电商订单同步
│   ├── sync.py
│   └── config.example.py
│
├── 📱 skills                     # Android自动化Skill
│
├── 📊 wechat-crawler/           # 微信公众号爬虫
│   ├── crawler.py
│   └── Dockerfile
│
├── ⚙️ openclaw-installer/       # 安装脚本
│   └── install.sh
│
├── 📄 docs/                     # 文档
│   ├── quick-start.md
│   └── faq.md
│
├── 📁 portfolio/                # 案例研究
│   └── case-studies.md
│
├── 📜 grab_gifts.py             # 他趣App抢礼物脚本
│
└── 📦 taqu-grabber.tar.gz       # 爬虫打包
```

---

## 🚀 快速开始

### 1. 克隆仓库
```bash
git clone https://github.com/AWTX550W/openclaw-works.git
cd openclaw-works
```

### 2. 选择项目
根据你的需求，选择相应的子项目：

| 需求 | 推荐项目 |
|------|----------|
| 想做农业机器人 | [harvesting-robot](#-采摘机器人) |
| 想做电商自动化 | [a2hmarket-sync](#-a2hmarket订单同步) |
| 想控制手机App | [skills](#-android设备自动化) |
| 想采集微信公众号 | [wechat-crawler](#-微信公众号爬虫) |
| 想快速搭建环境 | [openclaw-installer](#-openclaw安装助手) |

### 3. 阅读文档
- [快速开始指南](docs/quick-start.md)
- [常见问题](docs/faq.md)
- [API 申请指南](API申请指南.md)

---

## 🔧 常用工具

### API 密钥申请

| 服务 | 推荐方案 | 申请地址 |
|------|----------|----------|
| 视觉模型 | 智谱 GLM-4V-Flash (免费) | [open.bigmodel.cn](https://open.bigmodel.cn/) |
| AI 能力 | 阿里云 DashScope | [dashscope.console.aliyun.com](https://dashscope.console.aliyun.com/) |

详细申请指南: [API申请指南.md](API申请指南.md)

---

## 📖 文档导航

| 文档 | 内容 |
|------|------|
| [SUMMARY.md](SUMMARY.md) | 文档目录索引 |
| [docs/quick-start.md](docs/quick-start.md) | 快速开始教程 |
| [docs/faq.md](docs/faq.md) | 常见问题解答 |
| [PUBLISH.md](PUBLISH.md) | 发布到 GitHub 指南 |
| [CONTRIBUTING.md](CONTRIBUTING.md) | 贡献指南 |

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. 🍴 Fork 本仓库
2. 🌿 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 📝 提交更改 (`git commit -m 'Add amazing feature'`)
4. 🚀 推送到分支 (`git push origin feature/amazing-feature`)
5. 🎁 创建 Pull Request

---

## 📄 许可证

本项目采用 [MIT License](LICENSE)。

---

## 📬 联系方式

- 🐛 GitHub Issues: [提交 Bug 或功能请求](https://github.com/AWTX550W/openclaw-works/issues)
- 💬 讨论区: [GitHub Discussions](https://github.com/AWTX550W/openclaw-works/discussions)
- 📧 邮箱: awtx550w@example.com
