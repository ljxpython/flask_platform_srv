# 🎨 开发最佳实践

> 优雅的代码就像精心修剪的花园，每一行都有其存在的意义 ✨

## 🏗️ 代码架构原则

### 分层架构设计

我们采用**经典的三层架构**，确保代码的清晰性和可维护性：

```
🎨 API层 (plant_srv/api/)
    ↓ 处理HTTP请求，参数验证，响应格式化
🧠 业务逻辑层 (plant_srv/services/)
    ↓ 核心业务逻辑，数据处理，业务规则
💾 数据访问层 (plant_srv/model/)
    ↓ 数据库操作，数据模型定义
```

### 设计原则

**1. 单一职责原则 (SRP)**
```python
# ❌ 不好的例子 - 一个类承担太多责任
class UserManager:
    def create_user(self, data):
        # 验证数据
        # 发送邮件
        # 记录日志
        # 保存数据库
        pass

# ✅ 好的例子 - 职责分离
class UserValidator:
    def validate(self, data): pass

class EmailService:
    def send_welcome_email(self, user): pass

class UserRepository:
    def save(self, user): pass

class UserService:
    def __init__(self, validator, email_service, repository):
        self.validator = validator
        self.email_service = email_service
        self.repository = repository
```

**2. 开闭原则 (OCP)**
```python
# 使用策略模式支持不同的测试执行策略
from abc import ABC, abstractmethod

class TestExecutor(ABC):
    @abstractmethod
    def execute(self, test_suite): pass

class PytestExecutor(TestExecutor):
    def execute(self, test_suite):
        # pytest执行逻辑
        pass

class LocustExecutor(TestExecutor):
    def execute(self, test_suite):
        # locust执行逻辑
        pass
```

## 📝 代码规范

### 命名规范

**1. 变量和函数命名**
```python
# ✅ 使用有意义的名称
def get_active_test_cases_by_project(project_id):
    active_cases = []
    return active_cases

# ❌ 避免无意义的名称
def get_data(id):
    result = []
    return result
```

**2. 类命名**
```python
# ✅ 使用PascalCase，名称要描述性强
class TestResultAnalyzer:
    pass

class UserAuthenticationService:
    pass

# ❌ 避免缩写和模糊名称
class TRA:
    pass

class Service:
    pass
```

**3. 常量命名**
```python
# ✅ 使用UPPER_SNAKE_CASE
MAX_RETRY_ATTEMPTS = 3
DEFAULT_TIMEOUT_SECONDS = 30
TEST_STATUS_RUNNING = "running"

# 在constants.py中集中管理
class TestStatus:
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
```

### 文档字符串规范

**1. 模块文档**
```python
"""
用户管理API模块

本模块提供用户注册、登录、权限管理等功能的API接口。
支持JWT认证和基于角色的访问控制。

作者: JiaXin Li
创建时间: 2023-12-01
最后修改: 2023-12-15
"""
```

**2. 函数文档**
```python
def create_test_suite(project_id: int, suite_name: str, case_ids: List[int]) -> Dict:
    """
    创建测试套件

    将指定的测试用例组合成一个测试套件，用于批量执行测试。

    Args:
        project_id (int): 项目ID，必须是有效的项目
        suite_name (str): 套件名称，在项目内必须唯一
        case_ids (List[int]): 测试用例ID列表，至少包含一个用例

    Returns:
        Dict: 包含创建的套件信息
            {
                "id": 123,
                "name": "用户模块测试套件",
                "case_count": 5,
                "created_at": "2023-12-01T10:00:00Z"
            }

    Raises:
        ValueError: 当project_id无效或suite_name重复时
        ValidationError: 当case_ids为空或包含无效ID时

    Example:
        >>> suite = create_test_suite(1, "登录测试套件", [1, 2, 3])
        >>> print(suite["id"])
        123
    """
```

**3. 类文档**
```python
class TestResultAnalyzer:
    """
    测试结果分析器

    负责分析测试执行结果，生成统计报告和趋势分析。
    支持多种测试框架的结果格式。

    Attributes:
        result_parser (ResultParser): 结果解析器
        report_generator (ReportGenerator): 报告生成器

    Example:
        >>> analyzer = TestResultAnalyzer()
        >>> report = analyzer.analyze_test_results(test_results)
        >>> print(report.success_rate)
        0.95
    """
```

## 🛡️ 错误处理

### 异常处理策略

**1. 自定义异常类**
```python
class PlantTestException(Exception):
    """平台基础异常类"""
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)

class ValidationError(PlantTestException):
    """数据验证异常"""
    pass

class ResourceNotFoundError(PlantTestException):
    """资源不存在异常"""
    pass

class AuthenticationError(PlantTestException):
    """认证失败异常"""
    pass
```

**2. 统一错误处理**
```python
from functools import wraps
from flask import jsonify

def handle_exceptions(f):
    """统一异常处理装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except ValidationError as e:
            return jsonify({
                "success": False,
                "error_code": "VALIDATION_ERROR",
                "message": str(e)
            }), 400
        except ResourceNotFoundError as e:
            return jsonify({
                "success": False,
                "error_code": "RESOURCE_NOT_FOUND",
                "message": str(e)
            }), 404
        except Exception as e:
            logger.exception("Unexpected error occurred")
            return jsonify({
                "success": False,
                "error_code": "INTERNAL_ERROR",
                "message": "Internal server error"
            }), 500
    return decorated_function

# 使用示例
@auto_pytest.route("/create_suite", methods=["POST"])
@handle_exceptions
def create_suite():
    # 业务逻辑
    pass
```

### 日志记录最佳实践

**1. 结构化日志**
```python
import logging
import json
from datetime import datetime

class StructuredLogger:
    def __init__(self, name):
        self.logger = logging.getLogger(name)

    def log_api_request(self, method, path, user_id=None, **kwargs):
        """记录API请求日志"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": "api_request",
            "method": method,
            "path": path,
            "user_id": user_id,
            **kwargs
        }
        self.logger.info(json.dumps(log_data))

    def log_test_execution(self, test_id, status, duration=None, **kwargs):
        """记录测试执行日志"""
        log_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "type": "test_execution",
            "test_id": test_id,
            "status": status,
            "duration": duration,
            **kwargs
        }
        self.logger.info(json.dumps(log_data))

# 使用示例
logger = StructuredLogger(__name__)

@auto_pytest.route("/run_test", methods=["POST"])
def run_test():
    logger.log_api_request("POST", "/run_test", user_id=get_current_user_id())
    # 执行测试逻辑
    logger.log_test_execution(test_id=123, status="success", duration=45.2)
```

## 🔒 安全最佳实践

### 输入验证

**1. 使用Marshmallow进行数据验证**
```python
from marshmallow import Schema, fields, validate, ValidationError

class CreateSuiteSchema(Schema):
    """创建测试套件的数据验证模式"""
    suite_name = fields.Str(
        required=True,
        validate=validate.Length(min=1, max=100),
        error_messages={"required": "套件名称不能为空"}
    )
    project_id = fields.Int(
        required=True,
        validate=validate.Range(min=1),
        error_messages={"required": "项目ID不能为空"}
    )
    case_ids = fields.List(
        fields.Int(validate=validate.Range(min=1)),
        required=True,
        validate=validate.Length(min=1),
        error_messages={"required": "至少选择一个测试用例"}
    )

def validate_request_data(schema_class):
    """请求数据验证装饰器"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            schema = schema_class()
            try:
                data = schema.load(request.get_json())
                return f(data, *args, **kwargs)
            except ValidationError as err:
                return jsonify({
                    "success": False,
                    "errors": err.messages
                }), 400
        return decorated_function
    return decorator

# 使用示例
@auto_pytest.route("/create_suite", methods=["POST"])
@validate_request_data(CreateSuiteSchema)
def create_suite(validated_data):
    # validated_data已经通过验证
    pass
```

### SQL注入防护

```python
# ✅ 使用ORM参数化查询
def get_user_by_name(username):
    return User.select().where(User.name == username).first()

# ✅ 使用参数化原生SQL
def get_complex_data(user_id, status):
    query = """
        SELECT * FROM test_results
        WHERE user_id = %s AND status = %s
        ORDER BY created_at DESC
    """
    return database.execute_sql(query, (user_id, status))

# ❌ 避免字符串拼接
def bad_query(username):
    # 这样做容易受到SQL注入攻击
    query = f"SELECT * FROM users WHERE name = '{username}'"
    return database.execute_sql(query)
```

## 🧪 测试最佳实践

### 单元测试

**1. 测试结构**
```python
import pytest
from unittest.mock import Mock, patch
from plant_srv.api.auto_pytest import create_suite
from plant_srv.model.auto_pytest import Suite

class TestCreateSuite:
    """测试套件创建功能的测试类"""

    def setup_method(self):
        """每个测试方法执行前的设置"""
        self.mock_project = Mock()
        self.mock_project.id = 1
        self.mock_project.name = "测试项目"

    def test_create_suite_success(self):
        """测试成功创建套件"""
        # Arrange
        suite_data = {
            "suite_name": "测试套件",
            "project_id": 1,
            "case_ids": [1, 2, 3]
        }

        # Act
        with patch('plant_srv.model.auto_pytest.Project.get') as mock_get:
            mock_get.return_value = self.mock_project
            result = create_suite(suite_data)

        # Assert
        assert result["success"] is True
        assert "id" in result["data"]

    def test_create_suite_invalid_project(self):
        """测试无效项目ID"""
        # Arrange
        suite_data = {
            "suite_name": "测试套件",
            "project_id": 999,  # 不存在的项目ID
            "case_ids": [1, 2, 3]
        }

        # Act & Assert
        with pytest.raises(ResourceNotFoundError):
            create_suite(suite_data)
```

**2. 测试数据管理**
```python
# conftest.py - pytest配置文件
import pytest
from plant_srv.model.modelsbase import database
from plant_srv.model.user import User

@pytest.fixture(scope="function")
def test_database():
    """测试数据库fixture"""
    # 使用内存数据库进行测试
    test_db = SqliteDatabase(':memory:')
    database.initialize(test_db)

    # 创建表
    with test_db:
        test_db.create_tables([User, Project, Suite])

    yield test_db

    # 清理
    test_db.close()

@pytest.fixture
def sample_user():
    """创建示例用户"""
    return User.create(
        name="testuser",
        password="hashed_password",
        email="test@example.com"
    )
```

### 集成测试

```python
import pytest
from flask import Flask
from plant_srv import create_app

@pytest.fixture
def app():
    """创建测试应用"""
    app = create_app()
    app.config.update({
        "TESTING": True,
        "DATABASE_URL": "sqlite:///:memory:"
    })
    return app

@pytest.fixture
def client(app):
    """创建测试客户端"""
    return app.test_client()

def test_user_registration_flow(client):
    """测试用户注册流程"""
    # 注册用户
    response = client.post('/api/user/register', json={
        "username": "newuser",
        "password": "password123",
        "email": "newuser@example.com"
    })
    assert response.status_code == 200

    # 登录用户
    response = client.post('/api/user/login', json={
        "username": "newuser",
        "password": "password123"
    })
    assert response.status_code == 200
    assert "token" in response.get_json()["data"]
```

## 🚀 性能优化

### 数据库优化

**1. 查询优化**
```python
# ✅ 使用select_related避免N+1查询
def get_suites_with_project():
    return Suite.select(Suite, Project).join(Project)

# ✅ 使用索引字段进行查询
def get_active_tests():
    return TestResult.select().where(
        TestResult.status == "running"
    ).order_by(TestResult.created_at.desc())

# ✅ 分页查询
def get_paginated_results(page=1, per_page=20):
    offset = (page - 1) * per_page
    return TestResult.select().limit(per_page).offset(offset)
```

**2. 缓存策略**
```python
from functools import lru_cache
import redis

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def cache_result(expire_time=300):
    """Redis缓存装饰器"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # 生成缓存键
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"

            # 尝试从缓存获取
            cached_result = redis_client.get(cache_key)
            if cached_result:
                return json.loads(cached_result)

            # 执行函数并缓存结果
            result = func(*args, **kwargs)
            redis_client.setex(
                cache_key,
                expire_time,
                json.dumps(result, default=str)
            )
            return result
        return wrapper
    return decorator

@cache_result(expire_time=600)  # 缓存10分钟
def get_project_statistics(project_id):
    """获取项目统计信息（缓存版本）"""
    # 复杂的统计查询
    pass
```

### 异步处理

```python
from celery import Celery
from plant_srv.utils.celery_util.create_celery_app import celery

@celery.task(bind=True, max_retries=3)
def execute_test_suite_async(self, suite_id, test_env):
    """异步执行测试套件"""
    try:
        # 执行测试逻辑
        result = execute_test_suite(suite_id, test_env)
        return result
    except Exception as exc:
        # 重试机制
        if self.request.retries < self.max_retries:
            raise self.retry(countdown=60, exc=exc)
        else:
            # 记录失败日志
            logger.error(f"Test suite {suite_id} failed after {self.max_retries} retries")
            raise
```

## 📊 监控和观测

### 应用监控

```python
import time
from functools import wraps

def monitor_performance(func):
    """性能监控装饰器"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = func(*args, **kwargs)
            status = "success"
            return result
        except Exception as e:
            status = "error"
            raise
        finally:
            duration = time.time() - start_time
            # 记录性能指标
            logger.info(f"Function {func.__name__} executed in {duration:.2f}s with status {status}")
    return wrapper

@monitor_performance
def complex_business_logic():
    # 复杂的业务逻辑
    pass
```

### 健康检查

```python
@app.route("/health")
def health_check():
    """健康检查端点"""
    checks = {
        "database": check_database_connection(),
        "redis": check_redis_connection(),
        "celery": check_celery_workers(),
        "disk_space": check_disk_space()
    }

    all_healthy = all(checks.values())
    status_code = 200 if all_healthy else 503

    return jsonify({
        "status": "healthy" if all_healthy else "unhealthy",
        "checks": checks,
        "timestamp": datetime.utcnow().isoformat()
    }), status_code
```

## 🔄 持续集成/持续部署 (CI/CD)

### GitHub Actions配置

```yaml
# .github/workflows/test.yml
name: Test and Deploy

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      mysql:
        image: mysql:8.0
        env:
          MYSQL_ROOT_PASSWORD: test
          MYSQL_DATABASE: test
        ports:
          - 3306:3306
        options: --health-cmd="mysqladmin ping" --health-interval=10s --health-timeout=5s --health-retries=3

      redis:
        image: redis:6-alpine
        ports:
          - 6379:6379
        options: --health-cmd="redis-cli ping" --health-interval=10s --health-timeout=5s --health-retries=3

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.8'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install poetry
        poetry install

    - name: Run tests
      run: |
        poetry run pytest --cov=plant_srv --cov-report=xml

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v3
```

### 代码质量检查

```yaml
# .github/workflows/quality.yml
name: Code Quality

on: [push, pull_request]

jobs:
  quality:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.8'

    - name: Install dependencies
      run: |
        pip install black flake8 mypy

    - name: Check code formatting
      run: black --check .

    - name: Lint with flake8
      run: flake8 plant_srv/

    - name: Type checking
      run: mypy plant_srv/
```

---

*优秀的代码就像精心照料的花园，需要持续的关注和改进才能保持美丽 🌺*
