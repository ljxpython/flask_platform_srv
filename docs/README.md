# 🌱 Flask Plant Test Platform

> 一个功能强大、设计优雅的全栈测试平台，让测试变得像种花一样简单有趣！

## 🎯 项目简介

Flask Plant Test Platform（简称"植物测试平台"）是一个基于Flask构建的现代化测试管理平台。就像精心培育植物一样，我们用心打造了这个平台来帮助测试工程师们更好地管理和执行各种测试任务。

### ✨ 核心特性

- 🔧 **自动化测试管理** - 支持pytest测试用例的完整生命周期管理
- 🚀 **性能测试集成** - 内置Locust性能测试框架支持
- 👥 **用户权限管理** - 完善的用户注册、登录和权限控制
- 📊 **测试报告生成** - 自动生成美观的Allure测试报告
- ⏰ **定时任务调度** - 支持cron表达式的定时测试执行
- 🔄 **异步任务处理** - 基于Celery的异步任务队列
- 📁 **文件管理** - 支持测试文件的上传和管理
- 🎨 **现代化UI** - 配合前端项目提供优雅的用户界面

## 在线体验

[巧克力测试平台](https://www.coder-ljx.cn:7524/welcome)

账号密码: test/test



### 🏗️ 技术架构

```
Frontend (React/Ant Design)
         ↓
Flask API Server
         ↓
┌─────────────┬─────────────┬─────────────┐
│   MySQL     │    Redis    │   Celery    │
│  (数据存储)   │  (缓存/会话)  │  (异步任务)  │
└─────────────┴─────────────┴─────────────┘
```

### 🎭 设计理念

我们相信测试应该是：
- **简单的** - 复杂的功能，简单的操作
- **可靠的** - 稳定运行，值得信赖
- **高效的** - 自动化一切可以自动化的
- **有趣的** - 让枯燥的测试工作变得生动有趣

## 🚀 快速开始

### 环境要求

- Python 3.8+
- MySQL 5.7+
- Redis 6.0+
- Node.js 16+ (前端项目)

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/ljxpython/flask_platform_srv.git
cd flask_plant_srv
```

2. **安装依赖**
```bash
pip install -r requirements.txt
# 或使用poetry
poetry install
```

3. **配置环境**
```bash
cp conf/settings.yaml.example conf/settings.yaml
# 编辑配置文件，设置数据库和Redis连接信息
```

4. **启动服务**
```bash
python manage.py
```

5. **访问平台**
- 后端API: http://localhost:5000
- 前端界面: https://github.com/ljxpython/test_platform

## 📚 文档导航

### 👤 用户指南
- [平台功能概览](user-guide/platform-overview.md) - 了解平台的主要功能
- [自动化测试指南](user-guide/auto-testing.md) - 学习如何使用自动化测试功能
- [性能测试指南](user-guide/performance-testing.md) - 掌握性能测试的使用方法

### 👨‍💻 开发者指南
- [开发环境搭建](developer-guide/getting-started.md) - 快速搭建开发环境
- [开发最佳实践](developer-guide/best-practices.md) - 代码规范和最佳实践
- [API接口文档](api/api-reference.md) - 详细的API接口说明

### 🏛️ 架构文档
- [系统架构设计](architecture/system-design.md) - 深入了解系统设计理念
- [部署指南](deployment/installation.md) - 生产环境部署说明

## 🤝 贡献指南

我们欢迎所有形式的贡献！无论是：
- 🐛 报告Bug
- 💡 提出新功能建议
- 📝 改进文档
- 🔧 提交代码

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 👨‍💻 作者

**JiaXin Li** - *项目创建者和主要维护者*

<img src="./assets/image-20250531212549739.png" alt="Description" width="300"/>



---

*让测试像种植物一样，用心培育，静待花开 🌸*
