# 📡 API接口文档

> 完整的API接口说明，让前后端对接如丝般顺滑 🚀

## 🎯 API概览

### 基础信息

- **Base URL**: `http://localhost:5000/api`
- **认证方式**: JWT Bearer Token
- **数据格式**: JSON
- **字符编码**: UTF-8

### 通用响应格式

所有API接口都遵循统一的响应格式：

```json
{
  "success": true,
  "data": {},
  "message": "操作成功",
  "error_code": null,
  "timestamp": "2023-12-01T10:00:00Z"
}
```

**响应字段说明：**
- `success` (boolean): 请求是否成功
- `data` (object): 响应数据，成功时包含具体数据
- `message` (string): 响应消息，用于用户提示
- `error_code` (string): 错误代码，失败时提供具体错误类型
- `timestamp` (string): 响应时间戳

### 状态码说明

| 状态码 | 说明 | 示例场景 |
|--------|------|----------|
| 200 | 成功 | 正常的GET、POST请求 |
| 201 | 创建成功 | 创建资源成功 |
| 400 | 请求参数错误 | 参数验证失败 |
| 401 | 未认证 | 缺少或无效的Token |
| 403 | 权限不足 | 用户权限不够 |
| 404 | 资源不存在 | 请求的资源未找到 |
| 500 | 服务器错误 | 系统内部错误 |

## 👤 用户管理API

### 用户注册

**接口地址**: `POST /api/user/register`

**请求参数**:
```json
{
  "username": "testuser",
  "password": "password123",
  "email": "test@example.com",
  "avatar": "https://example.com/avatar.jpg"  // 可选
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "user_id": 123,
    "username": "testuser",
    "email": "test@example.com",
    "avatar": "https://example.com/avatar.jpg",
    "access": 0,
    "created_at": "2023-12-01T10:00:00Z"
  },
  "message": "用户注册成功"
}
```

### 用户登录

**接口地址**: `POST /api/user/login`

**请求参数**:
```json
{
  "username": "testuser",
  "password": "password123"
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "user": {
      "user_id": 123,
      "username": "testuser",
      "email": "test@example.com",
      "avatar": "https://example.com/avatar.jpg",
      "access": 0
    }
  },
  "message": "登录成功"
}
```

### 获取当前用户信息

**接口地址**: `GET /api/user/currentUser`

**请求头**:
```
Authorization: Bearer <token>
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "user_id": 123,
    "username": "testuser",
    "email": "test@example.com",
    "avatar": "https://example.com/avatar.jpg",
    "access": 0,
    "last_login": "2023-12-01T09:30:00Z"
  }
}
```

### 用户退出

**接口地址**: `POST /api/user/logout`

**请求头**:
```
Authorization: Bearer <token>
```

**响应示例**:
```json
{
  "success": true,
  "message": "退出成功"
}
```

## 🧪 自动化测试API

### 项目管理

#### 创建项目

**接口地址**: `POST /api/auto_pytest/create_project`

**请求参数**:
```json
{
  "project_name": "用户管理系统",
  "project_desc": "用户注册、登录、权限管理等功能的测试项目",
  "project_owners": "张三,李四"
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "project_name": "用户管理系统",
    "project_desc": "用户注册、登录、权限管理等功能的测试项目",
    "project_owners": "张三,李四",
    "created_at": "2023-12-01T10:00:00Z"
  },
  "message": "项目创建成功"
}
```

#### 获取项目列表

**接口地址**: `GET /api/auto_pytest/get_project_list`

**查询参数**:
- `current` (int): 当前页码，默认1
- `pageSize` (int): 每页数量，默认10
- `project_name` (string): 项目名称筛选
- `project_owners` (string): 项目负责人筛选

**响应示例**:
```json
{
  "success": true,
  "data": {
    "list": [
      {
        "id": 1,
        "project_name": "用户管理系统",
        "project_desc": "用户注册、登录、权限管理等功能的测试项目",
        "project_owners": "张三,李四",
        "created_at": "2023-12-01T10:00:00Z"
      }
    ],
    "total": 1,
    "current": 1,
    "pageSize": 10
  }
}
```

### 测试模块管理

#### 同步测试模块

**接口地址**: `POST /api/auto_pytest/sync_test_moudle`

**功能说明**: 自动扫描测试目录，发现新的测试模块

**响应示例**:
```json
{
  "success": true,
  "data": {
    "moudle_list": ["user_management", "order_system", "payment"]
  },
  "message": "同步测试模块成功,所有模块列表如上"
}
```

#### 查询测试模块

**接口地址**: `GET /api/auto_pytest/query_test_moudle`

**查询参数**:
- `current` (int): 当前页码
- `pageSize` (int): 每页数量
- `id` (int): 模块ID筛选

**响应示例**:
```json
{
  "success": true,
  "data": {
    "list": [
      {
        "id": 1,
        "moudle": "user_management",
        "moudle_desc": "用户管理模块测试",
        "created_at": "2023-12-01T10:00:00Z"
      }
    ],
    "total": 1
  }
}
```

### 测试用例管理

#### 同步测试用例

**接口地址**: `POST /api/auto_pytest/sync_test_case`

**请求参数**:
```json
{
  "moudle_name": "user_management"
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "moudle_list": ["user_management"]
  },
  "message": "同步测试模块成功,所有模块列表如上"
}
```

#### 获取测试用例

**接口地址**: `GET /api/auto_pytest/get_case_func`

**查询参数**:
- `current` (int): 当前页码
- `pageSize` (int): 每页数量
- `moudle_id` (int): 模块ID筛选
- `case_func` (string): 用例名称筛选

**响应示例**:
```json
{
  "success": true,
  "data": {
    "list": [
      {
        "id": 1,
        "case_func": "test_user_login",
        "case_func_desc": "测试用户登录功能",
        "case_sence": "test_login",
        "case_path": "/path/to/test_login.py",
        "casemoudle": {
          "id": 1,
          "moudle": "user_management"
        }
      }
    ],
    "total": 1
  }
}
```

### 测试套件管理

#### 创建测试套件

**接口地址**: `POST /api/auto_pytest/create_suite`

**请求参数**:
```json
{
  "suite_name": "用户模块冒烟测试",
  "project_id": 1,
  "case_ids": "1,2,3,5",
  "suite_desc": "包含用户注册、登录、信息修改等核心功能"
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "suite_name": "用户模块冒烟测试",
    "project_id": 1,
    "case_ids": "1,2,3,5",
    "suite_desc": "包含用户注册、登录、信息修改等核心功能",
    "created_at": "2023-12-01T10:00:00Z"
  },
  "message": "测试套件创建成功"
}
```

#### 获取测试套件

**接口地址**: `GET /api/auto_pytest/get_suite`

**查询参数**:
- `current` (int): 当前页码
- `pageSize` (int): 每页数量
- `project_id` (int): 项目ID筛选
- `suite_name` (string): 套件名称筛选

**响应示例**:
```json
{
  "success": true,
  "data": {
    "list": [
      {
        "id": 1,
        "suite_name": "用户模块冒烟测试",
        "project": {
          "id": 1,
          "project_name": "用户管理系统"
        },
        "case_ids": "1,2,3,5",
        "suite_desc": "包含用户注册、登录、信息修改等核心功能",
        "created_at": "2023-12-01T10:00:00Z"
      }
    ],
    "total": 1
  }
}
```

### 测试执行

#### 执行测试套件

**接口地址**: `POST /api/auto_pytest/run_test`

**请求参数**:
```json
{
  "suite_id": 1,
  "title": "用户模块冒烟测试-20231201",
  "test_type": "auto",
  "test_env": "test"
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "id": 123,
    "title": "用户模块冒烟测试-20231201",
    "suite_name": "用户模块冒烟测试",
    "test_type": "auto",
    "test_env": "test",
    "start_time": "20231201_143022",
    "status": "running"
  },
  "message": "测试开始执行"
}
```

#### 获取测试结果

**接口地址**: `GET /api/auto_pytest/get_case_result`

**查询参数**:
- `current` (int): 当前页码
- `pageSize` (int): 每页数量
- `id` (int): 结果ID筛选
- `status` (string): 状态筛选 (running/success/failed)
- `test_type` (string): 测试类型筛选
- `test_env` (string): 测试环境筛选

**响应示例**:
```json
{
  "success": true,
  "data": {
    "list": [
      {
        "id": 123,
        "title": "用户模块冒烟测试-20231201",
        "suite": {
          "id": 1,
          "suite_name": "用户模块冒烟测试"
        },
        "status": "success",
        "result": "passed: 8, failed: 0, error: 0",
        "report_link": "http://example.com/reports/123/",
        "report_download": "http://example.com/reports/123/download",
        "test_type": "auto",
        "test_env": "test",
        "start_time": "2023-12-01T14:30:22Z",
        "end_time": "2023-12-01T14:35:45Z",
        "duration": 323
      }
    ],
    "total": 1
  }
}
```

### 测试计划管理

#### 创建测试计划

**接口地址**: `POST /api/auto_pytest/create_case_plant`

**请求参数**:
```json
{
  "plan_name": "每日回归测试",
  "suite_id": 1,
  "cron": "0 2 * * *",
  "test_env": "test",
  "is_open": "on"
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "id": 1,
    "plan_name": "每日回归测试",
    "suite_id": 1,
    "cron": "0 2 * * *",
    "test_env": "test",
    "is_open": "on",
    "plan_id": "schedule_123456",
    "created_at": "2023-12-01T10:00:00Z"
  },
  "message": "测试计划创建成功"
}
```

## 🚀 性能测试API

### Locust测试管理

#### 同步Locust模块

**接口地址**: `POST /api/locust_test/sync_locust_moudle`

**响应示例**:
```json
{
  "success": true,
  "data": {
    "moudle_list": ["api_performance", "user_load_test"]
  },
  "message": "同步压测测试模块成功,所有模块列表如上"
}
```

#### 获取Locust用例

**接口地址**: `GET /api/locust_test/get_locust_case`

**查询参数**:
- `current` (int): 当前页码
- `pageSize` (int): 每页数量
- `moudle` (string): 模块名称筛选

**响应示例**:
```json
{
  "success": true,
  "data": {
    "list": [
      {
        "id": 1,
        "moudle": "api_performance",
        "case_sence": "user_api_test",
        "path_desc": "用户API性能测试场景"
      }
    ],
    "total": 1
  }
}
```

#### 执行性能测试

**接口地址**: `POST /api/locust_test/run_locust_test`

**请求参数**:
```json
{
  "suite_id": 1,
  "title": "用户API压力测试",
  "users": 100,
  "spawn_rate": 10,
  "run_time": "10m",
  "host": "https://api.example.com"
}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "test_id": 456,
    "title": "用户API压力测试",
    "status": "running",
    "users": 100,
    "spawn_rate": 10,
    "run_time": "10m",
    "start_time": "2023-12-01T15:00:00Z"
  },
  "message": "性能测试开始执行"
}
```

## 📁 文件管理API

### 文件上传

**接口地址**: `POST /api/uploadfile/upload`

**请求格式**: `multipart/form-data`

**请求参数**:
- `file`: 上传的文件

**响应示例**:
```json
{
  "success": true,
  "data": {
    "filename": "test_report.pdf",
    "file_path": "/uploads/test_report.pdf",
    "file_size": 1024000,
    "upload_time": "2023-12-01T10:00:00Z"
  },
  "message": "文件上传成功"
}
```

---

*API文档就像测试平台的说明书，让每个接口都清晰明了，使用起来得心应手 📖*
