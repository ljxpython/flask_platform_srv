# 🛠️ 开发环境搭建指南

> 欢迎加入Flask Plant测试平台的开发者大家庭！让我们一起种植代码的花园 🌱

## 🎯 开发环境概览

### 技术栈一览

**后端技术栈 🐍**
- **Flask 2.3+** - 轻量级Web框架
- **Peewee ORM** - 简洁的数据库操作
- **Celery 5.3+** - 异步任务队列
- **APScheduler** - 定时任务调度
- **Redis 6.0+** - 缓存和消息队列
- **MySQL 8.0+** - 主数据库
- **JWT** - 用户认证
- **Dynaconf** - 配置管理

**前端技术栈 ⚛️**
- **React 18+** - 现代化前端框架
- **Ant Design 5+** - 企业级UI组件库
- **TypeScript** - 类型安全的JavaScript
- **Vite** - 快速构建工具

**开发工具 🔧**
- **Poetry** - Python依赖管理
- **Black** - 代码格式化
- **Pytest** - 测试框架
- **Pre-commit** - Git钩子管理

## 🚀 快速开始

### 第一步：环境准备

**1. 系统要求**
```bash
# 操作系统
macOS 10.15+ / Ubuntu 18.04+ / Windows 10+

# Python版本
Python 3.8+

# Node.js版本 (前端开发需要)
Node.js 16+

# 数据库
MySQL 8.0+ / MariaDB 10.5+
Redis 6.0+
```

**2. 安装基础工具**
```bash
# 安装Poetry (推荐的Python包管理工具)
curl -sSL https://install.python-poetry.org | python3 -

# 安装Git (如果还没有)
# macOS
brew install git

# Ubuntu
sudo apt-get install git

# 安装Docker (可选，用于快速启动数据库)
# 请参考官方文档安装Docker
```

### 第二步：克隆项目

```bash
# 克隆后端项目
git clone <your-backend-repo-url>
cd flask_plant_srv

# 克隆前端项目 (可选)
git clone https://github.com/ljxpython/test_platform
```

### 第三步：后端环境搭建

**1. 安装Python依赖**
```bash
# 使用Poetry安装依赖 (推荐)
poetry install

# 或使用pip安装
pip install -r requirements.txt

# 激活虚拟环境 (Poetry)
poetry shell

# 或创建虚拟环境 (pip)
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows
```

**2. 配置数据库**

**使用Docker快速启动 (推荐)**
```bash
# 启动MySQL和Redis
docker-compose up -d mysql redis

# 或者分别启动
docker run -d --name mysql-dev \
  -e MYSQL_ROOT_PASSWORD=boe \
  -e MYSQL_DATABASE=boe \
  -p 3306:3306 \
  mysql:8.0

docker run -d --name redis-dev \
  -p 6379:6379 \
  redis:6-alpine
```

**手动安装数据库**
```bash
# macOS (使用Homebrew)
brew install mysql redis
brew services start mysql
brew services start redis

# Ubuntu
sudo apt-get install mysql-server redis-server
sudo systemctl start mysql
sudo systemctl start redis

# 创建数据库
mysql -u root -p
CREATE DATABASE boe CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

**3. 配置文件设置**
```bash
# 复制配置文件模板
cp conf/settings.yaml.example conf/settings.yaml

# 编辑配置文件
vim conf/settings.yaml
```

配置文件示例：
```yaml
boe:  # 开发环境
  DB:
    host: localhost
    password: boe
    port: 3306
    user: root
    database: boe

  redis:
    host: localhost
    port: 6379
    password: ""
    db: 0

  test:
    base_dir: "/path/to/your/test/project"
    python_env: "python"
    report_dir: "/path/to/reports"

online:  # 生产环境配置
  # ... 生产环境配置
```

**4. 数据库初始化**
```bash
# 创建数据表
python -c "
from plant_srv.model.modelsbase import database
from plant_srv.model import *
database.create_tables([User, Goods, Project, CaseMoudle, CaseFunc, Suite, TestPlan, TestResult])
"

# 或运行初始化脚本
python scripts/init_db.py
```

### 第四步：启动开发服务器

**1. 启动后端服务**
```bash
# 开发模式启动
python manage.py

# 或使用Flask命令
export FLASK_APP=manage.py
export FLASK_ENV=development
flask run --host=0.0.0.0 --port=5000
```

**2. 启动Celery (异步任务)**
```bash
# 新开一个终端窗口
cd flask_plant_srv
poetry shell  # 激活虚拟环境

# 启动Celery Worker
celery -A plant_srv.utils.celery_util.make_celery:celery worker --loglevel=info

# 启动Celery Beat (定时任务，可选)
celery -A plant_srv.utils.celery_util.make_celery:celery beat --loglevel=info
```

**3. 验证安装**
```bash
# 检查API是否正常
curl http://localhost:5000/api/user/currentUser

# 应该返回401错误 (因为没有登录)，这说明服务正常运行
```

## 🏗️ 项目结构详解

```
flask_plant_srv/
├── 📁 conf/                    # 配置文件目录
│   ├── config.py              # 配置加载器
│   ├── constants.py           # 常量定义
│   └── settings.yaml          # 主配置文件
├── 📁 plant_srv/              # 主应用目录
│   ├── 📁 api/                # API路由模块
│   │   ├── __init__.py        # 蓝图注册
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
│   │   ├── locust_test.py     # 性能测试模型
│   │   └── goods.py           # 商品模型 (示例)
│   ├── 📁 utils/              # 工具类目录
│   │   ├── 📁 celery_util/    # Celery相关工具
│   │   ├── 📁 apscheduler_util/ # 定时任务工具
│   │   ├── flask_util.py      # Flask工具函数
│   │   ├── json_response.py   # JSON响应封装
│   │   ├── log_moudle.py      # 日志模块
│   │   └── middlewares.py     # 中间件
│   └── __init__.py            # 应用工厂函数
├── 📁 test/                   # 测试目录
├── 📁 logs/                   # 日志目录
├── 📁 docs/                   # 文档目录 (本文档)
├── manage.py                  # 应用启动入口
├── pyproject.toml            # Poetry配置文件
├── requirements.txt          # pip依赖文件
└── README.md                 # 项目说明
```

## 🔧 开发工具配置

### IDE配置

**VS Code 推荐插件**
```json
{
  "recommendations": [
    "ms-python.python",
    "ms-python.black-formatter",
    "ms-python.flake8",
    "ms-python.pylint",
    "bradlc.vscode-tailwindcss",
    "esbenp.prettier-vscode"
  ]
}
```

**PyCharm配置**
- 设置Python解释器为Poetry虚拟环境
- 配置代码格式化工具为Black
- 启用类型检查和代码提示

### Git钩子配置

```bash
# 安装pre-commit
pip install pre-commit

# 安装Git钩子
pre-commit install

# 手动运行检查
pre-commit run --all-files
```

`.pre-commit-config.yaml` 配置：
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.3.0
    hooks:
      - id: black
        language_version: python3.8

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: [--max-line-length=88]

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: [--profile=black]
```

## 🧪 测试环境配置

### 单元测试

```bash
# 运行所有测试
pytest

# 运行特定测试文件
pytest test/test_user.py

# 运行测试并生成覆盖率报告
pytest --cov=plant_srv --cov-report=html
```

### 集成测试

```bash
# 启动测试数据库
docker run -d --name mysql-test \
  -e MYSQL_ROOT_PASSWORD=test \
  -e MYSQL_DATABASE=test \
  -p 3307:3306 \
  mysql:8.0

# 运行集成测试
ENV_FOR_DYNACONF=test pytest test/integration/
```

## 🐛 调试技巧

### 日志配置

```python
# 在开发环境中启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)

# 查看SQL查询
import peewee
logger = logging.getLogger('peewee')
logger.addHandler(logging.StreamHandler())
logger.setLevel(logging.DEBUG)
```

### 断点调试

```python
# 使用pdb进行调试
import pdb; pdb.set_trace()

# 使用ipdb (更友好的调试器)
import ipdb; ipdb.set_trace()
```

### API测试

```bash
# 使用httpie测试API
pip install httpie

# 测试用户注册
http POST localhost:5000/api/user/register \
  username=testuser \
  password=testpass \
  email=test@example.com

# 测试用户登录
http POST localhost:5000/api/user/login \
  username=testuser \
  password=testpass
```

## 🚨 常见问题解决

### 数据库连接问题

```bash
# 检查MySQL是否运行
brew services list | grep mysql  # macOS
sudo systemctl status mysql      # Linux

# 检查端口是否被占用
lsof -i :3306

# 重置MySQL密码
mysql -u root -p
ALTER USER 'root'@'localhost' IDENTIFIED BY 'new_password';
```

### Redis连接问题

```bash
# 检查Redis是否运行
redis-cli ping

# 查看Redis配置
redis-cli config get "*"
```

### 依赖安装问题

```bash
# 清理Poetry缓存
poetry cache clear pypi --all

# 重新安装依赖
poetry install --no-cache

# 更新依赖
poetry update
```

---

*开发环境就像花园的土壤，只有准备得足够好，才能种出美丽的代码之花 🌸*
