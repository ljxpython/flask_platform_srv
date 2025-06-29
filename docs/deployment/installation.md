# 🚀 部署安装指南

> 从开发环境到生产环境，让您的测试平台稳定运行 🏭

## 🎯 部署概览

### 部署架构

```
Internet
    ↓
[Nginx负载均衡器]
    ↓
[Flask应用服务器集群]
    ↓
[MySQL主从数据库] + [Redis集群] + [Celery工作节点]
```

### 环境要求

**硬件要求**:
- **CPU**: 4核心以上 (推荐8核心)
- **内存**: 8GB以上 (推荐16GB)
- **存储**: 100GB以上SSD
- **网络**: 100Mbps以上带宽

**软件要求**:
- **操作系统**: Ubuntu 20.04+ / CentOS 8+ / RHEL 8+
- **Python**: 3.8+
- **MySQL**: 8.0+
- **Redis**: 6.0+
- **Nginx**: 1.18+
- **Docker**: 20.10+ (可选)

## 🐳 Docker部署 (推荐)

### 快速开始

**1. 准备Docker环境**
```bash
# 安装Docker和Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

**2. 克隆项目**
```bash
git clone <your-repo-url>
cd flask_plant_srv
```

**3. 配置环境变量**
```bash
# 复制环境变量模板
cp .env.example .env

# 编辑环境变量
vim .env
```

`.env` 文件示例：
```bash
# 应用配置
FLASK_ENV=production
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-key

# 数据库配置
MYSQL_ROOT_PASSWORD=your-mysql-root-password
MYSQL_DATABASE=plant_test_platform
MYSQL_USER=plant_user
MYSQL_PASSWORD=your-mysql-password

# Redis配置
REDIS_PASSWORD=your-redis-password

# Celery配置
CELERY_BROKER_URL=redis://:your-redis-password@redis:6379/2
CELERY_RESULT_BACKEND=redis://:your-redis-password@redis:6379/3
```

**4. 启动服务**
```bash
# 构建并启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f web
```

### Docker Compose配置

```yaml
# docker-compose.yml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=mysql://plant_user:${MYSQL_PASSWORD}@mysql:3306/${MYSQL_DATABASE}
      - REDIS_URL=redis://:${REDIS_PASSWORD}@redis:6379/0
    depends_on:
      - mysql
      - redis
    volumes:
      - ./logs:/app/logs
      - ./reports:/app/reports
    restart: unless-stopped

  worker:
    build: .
    command: celery -A plant_srv.utils.celery_util.make_celery:celery worker --loglevel=info
    environment:
      - DATABASE_URL=mysql://plant_user:${MYSQL_PASSWORD}@mysql:3306/${MYSQL_DATABASE}
      - CELERY_BROKER_URL=${CELERY_BROKER_URL}
      - CELERY_RESULT_BACKEND=${CELERY_RESULT_BACKEND}
    depends_on:
      - mysql
      - redis
    volumes:
      - ./logs:/app/logs
      - ./reports:/app/reports
    restart: unless-stopped

  beat:
    build: .
    command: celery -A plant_srv.utils.celery_util.make_celery:celery beat --loglevel=info
    environment:
      - DATABASE_URL=mysql://plant_user:${MYSQL_PASSWORD}@mysql:3306/${MYSQL_DATABASE}
      - CELERY_BROKER_URL=${CELERY_BROKER_URL}
      - CELERY_RESULT_BACKEND=${CELERY_RESULT_BACKEND}
    depends_on:
      - mysql
      - redis
    volumes:
      - ./logs:/app/logs
    restart: unless-stopped

  mysql:
    image: mysql:8.0
    environment:
      - MYSQL_ROOT_PASSWORD=${MYSQL_ROOT_PASSWORD}
      - MYSQL_DATABASE=${MYSQL_DATABASE}
      - MYSQL_USER=${MYSQL_USER}
      - MYSQL_PASSWORD=${MYSQL_PASSWORD}
    ports:
      - "3306:3306"
    volumes:
      - mysql_data:/var/lib/mysql
      - ./scripts/init.sql:/docker-entrypoint-initdb.d/init.sql
    restart: unless-stopped

  redis:
    image: redis:6-alpine
    command: redis-server --requirepass ${REDIS_PASSWORD}
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/ssl:/etc/nginx/ssl
    depends_on:
      - web
    restart: unless-stopped

volumes:
  mysql_data:
  redis_data:
```

### Dockerfile

```dockerfile
FROM python:3.8-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 安装Python依赖
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 创建必要的目录
RUN mkdir -p logs reports

# 设置环境变量
ENV PYTHONPATH=/app
ENV FLASK_APP=manage.py

# 暴露端口
EXPOSE 5000

# 启动命令
CMD ["python", "manage.py"]
```

## 🖥️ 传统部署

### 系统准备

**1. 更新系统**
```bash
# Ubuntu/Debian
sudo apt update && sudo apt upgrade -y

# CentOS/RHEL
sudo yum update -y
```

**2. 安装基础软件**
```bash
# Ubuntu/Debian
sudo apt install -y python3 python3-pip python3-venv git nginx mysql-server redis-server

# CentOS/RHEL
sudo yum install -y python3 python3-pip git nginx mysql-server redis
```

### 数据库配置

**1. MySQL配置**
```bash
# 启动MySQL服务
sudo systemctl start mysql
sudo systemctl enable mysql

# 安全配置
sudo mysql_secure_installation

# 创建数据库和用户
mysql -u root -p
```

```sql
-- 创建数据库
CREATE DATABASE plant_test_platform CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 创建用户
CREATE USER 'plant_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON plant_test_platform.* TO 'plant_user'@'localhost';
FLUSH PRIVILEGES;
```

**2. Redis配置**
```bash
# 启动Redis服务
sudo systemctl start redis
sudo systemctl enable redis

# 配置Redis密码
sudo vim /etc/redis/redis.conf
# 取消注释并设置密码
# requirepass your_redis_password

# 重启Redis
sudo systemctl restart redis
```

### 应用部署

**1. 创建应用用户**
```bash
sudo useradd -m -s /bin/bash plant
sudo su - plant
```

**2. 部署应用代码**
```bash
# 克隆代码
git clone <your-repo-url> /home/plant/flask_plant_srv
cd /home/plant/flask_plant_srv

# 创建虚拟环境
python3 -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

**3. 配置应用**
```bash
# 复制配置文件
cp conf/settings.yaml.example conf/settings.yaml

# 编辑配置
vim conf/settings.yaml
```

**4. 初始化数据库**
```bash
# 创建数据表
python -c "
from plant_srv.model.modelsbase import database
from plant_srv.model import *
database.create_tables([User, Goods, Project, CaseMoudle, CaseFunc, Suite, TestPlan, TestResult])
"
```

### 服务配置

**1. Systemd服务配置**

创建Web服务：
```bash
sudo vim /etc/systemd/system/plant-web.service
```

```ini
[Unit]
Description=Flask Plant Test Platform Web Server
After=network.target mysql.service redis.service

[Service]
Type=simple
User=plant
Group=plant
WorkingDirectory=/home/plant/flask_plant_srv
Environment=PATH=/home/plant/flask_plant_srv/venv/bin
ExecStart=/home/plant/flask_plant_srv/venv/bin/python manage.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

创建Celery Worker服务：
```bash
sudo vim /etc/systemd/system/plant-worker.service
```

```ini
[Unit]
Description=Flask Plant Test Platform Celery Worker
After=network.target mysql.service redis.service

[Service]
Type=simple
User=plant
Group=plant
WorkingDirectory=/home/plant/flask_plant_srv
Environment=PATH=/home/plant/flask_plant_srv/venv/bin
ExecStart=/home/plant/flask_plant_srv/venv/bin/celery -A plant_srv.utils.celery_util.make_celery:celery worker --loglevel=info
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

创建Celery Beat服务：
```bash
sudo vim /etc/systemd/system/plant-beat.service
```

```ini
[Unit]
Description=Flask Plant Test Platform Celery Beat
After=network.target mysql.service redis.service

[Service]
Type=simple
User=plant
Group=plant
WorkingDirectory=/home/plant/flask_plant_srv
Environment=PATH=/home/plant/flask_plant_srv/venv/bin
ExecStart=/home/plant/flask_plant_srv/venv/bin/celery -A plant_srv.utils.celery_util.make_celery:celery beat --loglevel=info
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**2. 启动服务**
```bash
# 重新加载systemd配置
sudo systemctl daemon-reload

# 启动并启用服务
sudo systemctl start plant-web plant-worker plant-beat
sudo systemctl enable plant-web plant-worker plant-beat

# 检查服务状态
sudo systemctl status plant-web plant-worker plant-beat
```

### Nginx配置

**1. 创建Nginx配置**
```bash
sudo vim /etc/nginx/sites-available/plant-test-platform
```

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 重定向到HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    # SSL配置
    ssl_certificate /etc/nginx/ssl/cert.pem;
    ssl_certificate_key /etc/nginx/ssl/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # 安全头
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";

    # 静态文件
    location /static/ {
        alias /home/plant/flask_plant_srv/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # 报告文件
    location /reports/ {
        alias /home/plant/flask_plant_srv/reports/;
        expires 1d;
    }

    # API代理
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # 超时配置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;

        # 缓冲配置
        proxy_buffering on;
        proxy_buffer_size 4k;
        proxy_buffers 8 4k;
    }

    # 文件上传大小限制
    client_max_body_size 100M;
}
```

**2. 启用配置**
```bash
# 创建软链接
sudo ln -s /etc/nginx/sites-available/plant-test-platform /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启Nginx
sudo systemctl restart nginx
sudo systemctl enable nginx
```

## 🔒 SSL证书配置

### 使用Let's Encrypt

```bash
# 安装Certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo crontab -e
# 添加以下行
0 12 * * * /usr/bin/certbot renew --quiet
```

## 📊 监控配置

### 系统监控

**1. 安装监控工具**
```bash
# 安装htop和iotop
sudo apt install htop iotop

# 安装Prometheus Node Exporter (可选)
wget https://github.com/prometheus/node_exporter/releases/download/v1.6.0/node_exporter-1.6.0.linux-amd64.tar.gz
tar xvfz node_exporter-1.6.0.linux-amd64.tar.gz
sudo mv node_exporter-1.6.0.linux-amd64/node_exporter /usr/local/bin/
```

**2. 日志轮转配置**
```bash
sudo vim /etc/logrotate.d/plant-test-platform
```

```
/home/plant/flask_plant_srv/logs/*.log {
    daily
    missingok
    rotate 30
    compress
    delaycompress
    notifempty
    create 644 plant plant
    postrotate
        systemctl reload plant-web plant-worker plant-beat
    endscript
}
```

## 🔧 维护和备份

### 数据库备份

```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/home/plant/backups"
DATE=$(date +%Y%m%d_%H%M%S)
DB_NAME="plant_test_platform"

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份数据库
mysqldump -u plant_user -p$MYSQL_PASSWORD $DB_NAME > $BACKUP_DIR/db_backup_$DATE.sql

# 压缩备份文件
gzip $BACKUP_DIR/db_backup_$DATE.sql

# 删除7天前的备份
find $BACKUP_DIR -name "db_backup_*.sql.gz" -mtime +7 -delete

echo "Database backup completed: db_backup_$DATE.sql.gz"
```

### 应用更新

```bash
#!/bin/bash
# update.sh

cd /home/plant/flask_plant_srv

# 拉取最新代码
git pull origin main

# 激活虚拟环境
source venv/bin/activate

# 更新依赖
pip install -r requirements.txt

# 重启服务
sudo systemctl restart plant-web plant-worker plant-beat

echo "Application updated successfully"
```

---

*部署就像为花园选择最适合的土壤和环境，只有精心准备，植物才能茁壮成长 🌱*
