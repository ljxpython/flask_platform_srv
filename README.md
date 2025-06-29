# 🌱 Flask Plant Test Platform

> 一个功能强大、设计优雅的全栈测试平台后端服务，让测试管理像种花一样简单有趣！

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![Flask](https://img.shields.io/badge/Flask-2.3+-green.svg)](https://flask.palletsprojects.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

## 🎯 项目简介

Flask Plant Test Platform是一个基于Flask构建的现代化测试管理平台后端服务。就像精心培育植物一样，我们用心打造了这个平台来帮助测试工程师们更好地管理和执行各种测试任务。

### ✨ 核心特性

- 🔧 **自动化测试管理** - 完整的pytest测试用例生命周期管理
- 🚀 **性能测试集成** - 内置Locust性能测试框架支持
- 👥 **用户权限管理** - 基于JWT的安全认证和权限控制
- 📊 **智能报告生成** - 自动生成美观的Allure测试报告
- ⏰ **定时任务调度** - 支持cron表达式的灵活任务调度
- 🔄 **异步任务处理** - 基于Celery的高性能异步任务队列
- 📁 **文件管理服务** - 安全的文件上传和管理功能
- 🎨 **RESTful API** - 完整的REST API支持前端集成

### 🏗️ 技术架构

```
┌─────────────────────────────────────────────────────────┐
│                    Flask API Server                    │
├─────────────────┬─────────────────┬─────────────────────┤
│   用户管理模块    │   测试管理模块    │   性能测试模块        │
│   JWT认证       │   pytest集成    │   Locust集成        │
│   权限控制       │   报告生成       │   负载测试          │
├─────────────────┼─────────────────┼─────────────────────┤
│              异步任务处理 (Celery)                      │
│              定时任务调度 (APScheduler)                 │
├─────────────────┬─────────────────┬─────────────────────┤
│   MySQL数据库    │   Redis缓存     │   文件存储系统        │
│   Peewee ORM    │   会话管理       │   报告文件          │
└─────────────────┴─────────────────┴─────────────────────┘
```

## 🚀 快速开始

### 环境要求

- **Python**: 3.8+
- **MySQL**: 8.0+
- **Redis**: 6.0+

## 在线体验

[巧克力测试平台](https://www.coder-ljx.cn:7524/welcome)

账号密码: test/test

### 安装步骤

1. **克隆项目**
```bash
git clone https://github.com/ljxpython/flask_platform_srv.git
cd flask_plant_srv
```

2. **安装依赖**
```bash
# 使用Poetry (推荐)
pip install poetry
poetry install

# 或使用pip
pip install -r requirements.txt
```

3. **配置环境**
```bash
# 复制配置文件
cp conf/settings.yaml.example conf/settings.yaml
# 编辑配置文件，设置数据库和Redis连接信息
vim conf/settings.yaml
```

4. **初始化数据库**
```bash
# 创建数据表
python -c "
from plant_srv.model.modelsbase import database
from plant_srv.model import *
database.create_tables([User, Goods, Project, CaseMoudle, CaseFunc, Suite, TestPlan, TestResult])
"
```

5. **启动服务**
```bash
# 启动主服务
python manage.py

# 启动Celery Worker (新终端)
celery -A plant_srv.utils.celery_util.make_celery:celery worker --loglevel=info

# 启动定时任务 (可选)
celery -A plant_srv.utils.celery_util.make_celery:celery beat --loglevel=info
```

6. **验证安装**
```bash
curl http://localhost:5000/health
# 应该返回健康检查信息
```

## 🌟 主要功能模块

### 👤 用户管理模块
**就像花园的门禁系统，确保只有合适的人能进入**

- **用户注册/登录** - 安全的用户认证机制
- **JWT Token认证** - 无状态的API认证
- **权限控制** - 基于角色的访问控制
- **会话管理** - Redis存储的会话管理

**代码示例**:
```python
@admin.route("/login", methods=["POST"])
def login():
    """用户登录接口"""
    data = request.get_json()
    username = data.get("username")
    password = data.get("password")

    # 验证用户凭据
    user = User.get_or_none(name=username)
    if user and pbkdf2_sha256.verify(password, user.password):
        access_token = create_access_token(identity=username)
        return JsonResponse()(
            data={"token": access_token},
            headers={"Authorization": "Bearer " + access_token}
        )
```

### 🧪 自动化测试模块
**平台的核心功能，像园丁的主要工具**

- **项目管理** - 测试项目的创建和配置
- **模块同步** - 自动发现和同步测试模块
- **用例管理** - 测试用例的增删改查
- **套件组装** - 灵活的测试套件组合
- **计划调度** - 基于cron的定时执行
- **结果管理** - 详细的测试结果和报告

**代码示例**:
```python
@auto_pytest.route("/run_test", methods=["POST"])
def run_test():
    """执行测试套件"""
    data = request.get_json()
    suite_id = data.get("suite_id")
    test_env = data.get("test_env", "test")

    # 异步执行测试
    task = execute_test_suite_async.delay(suite_id, test_env)
    return JsonResponse.success_response(
        data={"task_id": task.id, "status": "running"}
    )
```

### 🚀 性能测试模块
**像压力测试机，检验系统的承受能力**

- **Locust集成** - 现代化的性能测试框架
- **脚本管理** - 性能测试脚本的版本控制
- **负载配置** - 灵活的负载模式设置
- **实时监控** - 测试过程的实时性能指标
- **报告生成** - 详细的性能测试分析报告

**代码示例**:
```python
@locust_test.route("/run_locust_test", methods=["POST"])
def run_locust_test():
    """执行性能测试"""
    data = request.get_json()
    suite_id = data.get("suite_id")
    users = data.get("users", 10)
    spawn_rate = data.get("spawn_rate", 1)

    # 启动Locust性能测试
    result = start_locust_test(suite_id, users, spawn_rate)
    return JsonResponse.success_response(data=result)
```

### 🔄 异步任务模块
**像花园的自动灌溉系统，在后台默默工作**

- **Celery集成** - 分布式任务队列
- **任务监控** - 实时任务状态跟踪
- **失败重试** - 智能的任务重试机制
- **结果存储** - Redis存储的任务结果

## 📡 API接口概览

### 认证相关
- `POST /api/user/register` - 用户注册
- `POST /api/user/login` - 用户登录
- `GET /api/user/currentUser` - 获取当前用户信息
- `POST /api/user/logout` - 用户退出

### 自动化测试
- `POST /api/auto_pytest/sync_test_moudle` - 同步测试模块
- `POST /api/auto_pytest/create_suite` - 创建测试套件
- `POST /api/auto_pytest/run_test` - 执行测试
- `GET /api/auto_pytest/get_case_result` - 获取测试结果

### 性能测试
- `POST /api/locust_test/sync_locust_moudle` - 同步性能测试模块
- `POST /api/locust_test/run_locust_test` - 执行性能测试
- `GET /api/locust_test/get_locust_case` - 获取性能测试用例

### 文件管理
- `POST /api/uploadfile/upload` - 文件上传

> 📚 **完整API文档**: 查看 [docs/api/api-reference.md](docs/api/api-reference.md)

## 📁 项目结构

```
flask_plant_srv/
├── 📁 plant_srv/              # 主应用目录
│   ├── 📁 api/                # API路由模块
│   │   ├── user.py            # 用户管理API
│   │   ├── auto_pytest.py     # 自动化测试API
│   │   ├── locust_test.py     # 性能测试API
│   │   ├── goods.py           # 商品管理API (示例)
│   │   ├── uploadfile.py      # 文件上传API
│   │   └── async_task.py      # 异步任务API
│   ├── 📁 model/              # 数据模型
│   │   ├── modelsbase.py      # 基础模型类
│   │   ├── user.py            # 用户模型
│   │   ├── auto_pytest.py     # 自动化测试模型
│   │   └── locust_test.py     # 性能测试模型
│   ├── 📁 utils/              # 工具类
│   │   ├── 📁 celery_util/    # Celery相关工具
│   │   ├── 📁 apscheduler_util/ # 定时任务工具
│   │   ├── flask_util.py      # Flask工具函数
│   │   ├── json_response.py   # JSON响应封装
│   │   └── log_moudle.py      # 日志模块
│   └── __init__.py            # 应用工厂函数
├── 📁 conf/                   # 配置文件
│   ├── config.py              # 配置加载器
│   ├── constants.py           # 常量定义
│   └── settings.yaml          # 主配置文件
├── 📁 docs/                   # 完整文档
├── 📁 test/                   # 测试文件
├── 📁 logs/                   # 日志目录
├── manage.py                  # 应用启动入口
├── requirements.txt           # 依赖列表
└── README.md                  # 项目说明 (本文件)
```

## 🔧 配置说明

### 数据库配置
```yaml
# conf/settings.yaml
boe:  # 开发环境
  DB:
    host: localhost
    password: your_password
    port: 3306
    user: root
    database: plant_test_platform
```

### Redis配置
```yaml
redis:
  host: localhost
  port: 6379
  password: ""
  db: 0
```

### 测试配置
```yaml
test:
  base_dir: "/path/to/your/test/project"
  python_env: "python"
  report_dir: "/path/to/reports"
```

## 📚 文档导航

我们为您准备了完整的文档体系：

- 📖 **[项目总览](docs/README.md)** - 详细的项目介绍和快速开始
- 👤 **[用户指南](docs/user-guide/)** - 平台功能使用说明
  - [平台功能概览](docs/user-guide/platform-overview.md)
  - [自动化测试指南](docs/user-guide/auto-testing.md)
  - [性能测试指南](docs/user-guide/performance-testing.md)
- 👨‍💻 **[开发者指南](docs/developer-guide/)** - 开发环境和最佳实践
  - [开发环境搭建](docs/developer-guide/getting-started.md)
  - [开发最佳实践](docs/developer-guide/best-practices.md)
- 📡 **[API文档](docs/api/api-reference.md)** - 完整的API接口说明
- 🏛️ **[架构设计](docs/architecture/system-design.md)** - 系统架构和设计理念
- 🚀 **[部署指南](docs/deployment/installation.md)** - 生产环境部署说明

## 🤝 贡献指南

我们欢迎所有形式的贡献！

### 如何贡献
1. Fork 本项目
2. 创建您的特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开一个 Pull Request

### 开发规范
- 遵循 [PEP 8](https://www.python.org/dev/peps/pep-0008/) 代码风格
- 为新功能添加测试用例
- 更新相关文档
- 确保所有测试通过

## 📄 许可证

本项目采用 MIT 许可证

## 👨‍💻 作者

**JiaXin Li** - *项目创建者和主要维护者*

个人微信:

<img src="./docs/assets/image-20250531212549739.png" alt="Description" width="300"/>

如果感觉这个项目不错,也希望您能给个⭐️

## 🙏 致谢

感谢所有为这个项目做出贡献的开发者们！



---

<div align="center">

**让测试像种植物一样，用心培育，静待花开 🌸**



</div>
