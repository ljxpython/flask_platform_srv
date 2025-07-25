# 🤖 自动化测试使用指南

> 让测试自动化像呼吸一样自然！这里是您的自动化测试宝典 📚

## 🎯 快速上手

### 第一步：理解测试层次结构

我们的自动化测试采用了**分层管理**的设计理念，就像建造一座测试金字塔：

```
🏗️ 项目 (Project) - 最高层，整个测试项目的容器
    └── 📁 模块 (Module) - 按功能划分的测试模块
        └── 🧪 用例 (Case Function) - 具体的测试方法
            └── 📦 套件 (Suite) - 用例的组合包
                └── ⏰ 计划 (Test Plan) - 定时执行策略
                    └── 📊 结果 (Test Result) - 执行结果和报告
```

### 第二步：创建您的第一个测试项目

1. **登录平台** - 使用您的账号登录
2. **创建项目** - 点击"新建项目"按钮
3. **填写信息** - 项目名称、描述、负责人等
4. **保存项目** - 确认创建

```json
{
  "project_name": "我的第一个测试项目",
  "project_desc": "这是一个示例项目，用于学习平台使用",
  "project_owners": "张三,李四"
}
```

## 📁 模块管理：测试的分类整理

### 自动同步测试模块

平台会**自动扫描**您的测试目录，发现新的测试模块：

1. **目录结构要求**
```
tests/
├── user_management/     # 用户管理模块
│   ├── test_login.py
│   └── test_register.py
├── order_system/        # 订单系统模块
│   ├── test_create_order.py
│   └── test_cancel_order.py
└── payment/            # 支付模块
    └── test_payment.py
```

2. **同步操作**
   - 点击"同步测试模块"按钮
   - 系统自动扫描`tests`目录
   - 发现新模块并添加到数据库

3. **模块信息完善**
   - 为每个模块添加描述信息
   - 设置模块的优先级和标签
   - 配置模块的执行环境

### 测试用例发现

系统会**智能解析**Python测试文件，提取测试信息：

```python
class TestUserLogin:
    """用户登录功能测试类"""

    def test_valid_login(self):
        """测试有效用户登录"""
        # 测试代码...
        pass

    def test_invalid_password(self):
        """测试无效密码登录"""
        # 测试代码...
        pass
```

系统会自动提取：
- **类名和描述** - `TestUserLogin: 用户登录功能测试类`
- **方法名和描述** - `test_valid_login: 测试有效用户登录`
- **文件路径** - 用于执行时定位

## 🧪 测试用例管理

### 用例查询和筛选

支持多维度的用例查询：

```bash
# 按模块筛选
GET /api/auto_pytest/get_case_func?moudle_id=1

# 按用例名称搜索
GET /api/auto_pytest/get_case_func?case_func=test_login

# 分页查询
GET /api/auto_pytest/get_case_func?current=1&pageSize=10
```

### 用例标签管理

为测试用例添加标签，便于分类和筛选：

- **功能标签** - `login`, `register`, `payment`
- **优先级标签** - `P0`, `P1`, `P2`
- **环境标签** - `smoke`, `regression`, `integration`

```json
{
  "tag_name": "P0",
  "tag_desc": "最高优先级测试用例",
  "tag_color": "#ff4d4f"
}
```

## 📦 测试套件：用例的艺术组合

### 创建测试套件

测试套件是测试用例的**有机组合**，就像调配一杯完美的鸡尾酒：

1. **选择项目** - 确定套件所属项目
2. **命名套件** - 给套件起个有意义的名字
3. **选择用例** - 从用例库中选择需要的用例
4. **配置参数** - 设置执行参数和环境变量

```json
{
  "suite_name": "用户模块冒烟测试",
  "project_id": 1,
  "case_ids": "1,2,3,5,8",
  "suite_desc": "包含用户注册、登录、信息修改等核心功能的快速验证"
}
```

### 套件执行策略

- **顺序执行** - 按照用例顺序依次执行
- **并行执行** - 多个用例同时执行（需要用例间无依赖）
- **失败停止** - 遇到失败用例时停止执行
- **继续执行** - 忽略失败，执行所有用例

## ⏰ 测试计划：让测试自动发生

### 创建定时计划

使用**cron表达式**设置定时执行：

```json
{
  "plan_name": "每日回归测试",
  "suite_id": 1,
  "cron": "0 2 * * *",  // 每天凌晨2点执行
  "test_env": "test",
  "is_open": "on"
}
```

### 常用cron表达式

```bash
# 每天凌晨2点
0 2 * * *

# 每周一上午9点
0 9 * * 1

# 每小时执行一次
0 * * * *

# 工作日下午6点
0 18 * * 1-5
```

### 计划管理

- **启用/禁用** - 灵活控制计划的执行状态
- **执行历史** - 查看计划的执行记录
- **失败通知** - 执行失败时自动发送通知
- **结果统计** - 计划执行的成功率统计

## 🚀 测试执行：一键启动的魔法

### 手动执行

支持**即时执行**测试套件：

1. **选择套件** - 从套件列表中选择
2. **选择环境** - 开发/测试/生产环境
3. **设置参数** - 执行参数和标题
4. **启动执行** - 点击执行按钮

### 执行监控

实时监控测试执行状态：

- **运行状态** - `running`, `success`, `failed`
- **执行进度** - 当前执行的用例和进度
- **实时日志** - 查看执行过程中的日志输出
- **资源使用** - CPU、内存使用情况

### 执行环境

支持多环境测试执行：

```yaml
# 环境配置示例
boe:  # 测试环境
  api_base_url: "https://test-api.example.com"
  database_url: "mysql://test-db:3306/test"

online:  # 生产环境
  api_base_url: "https://api.example.com"
  database_url: "mysql://prod-db:3306/prod"
```

## 📊 测试报告：让数据说话

### Allure报告集成

自动生成**美观的Allure报告**：

- **测试概览** - 执行总数、成功率、失败率
- **用例详情** - 每个用例的执行详情和截图
- **趋势分析** - 历史执行趋势图表
- **失败分析** - 失败用例的分类和统计

### 报告访问

```bash
# 报告链接格式
https://your-domain.com/reports/{project_name}/{suite_name}-{test_type}-{test_env}-{timestamp}/

# 示例
https://test-platform.com/reports/user_system/smoke_test-auto-test-20231201_143022/
```

### 报告下载

支持多种格式的报告下载：

- **HTML报告** - 完整的交互式报告
- **PDF报告** - 适合打印和分享的静态报告
- **Excel报告** - 便于数据分析的表格格式

## 🎯 最佳实践

### 用例编写规范

1. **命名规范**
```python
def test_用户登录_有效用户名和密码_应该登录成功(self):
    """
    测试场景：用户使用有效的用户名和密码登录
    预期结果：登录成功，跳转到首页
    """
    pass
```

2. **文档字符串**
```python
class TestUserManagement:
    """
    用户管理功能测试套件

    包含用户注册、登录、信息修改、密码重置等功能的测试用例
    测试数据：使用测试环境的模拟数据
    依赖服务：用户服务、认证服务
    """
```

### 套件组织策略

- **按功能模块** - 将相关功能的用例组合在一起
- **按测试类型** - 冒烟测试、回归测试、集成测试
- **按执行频率** - 每日执行、每周执行、发版执行
- **按优先级** - P0核心功能、P1重要功能、P2一般功能

### 执行优化建议

1. **合理设置并发** - 根据系统性能调整并发数
2. **环境隔离** - 不同环境使用不同的测试数据
3. **失败重试** - 对不稳定的用例设置重试机制
4. **资源清理** - 测试后及时清理测试数据

---

*自动化测试就像种植自动浇水的花园，一旦设置好，就能持续为您带来美丽的测试结果 🌺*
