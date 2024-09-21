"""
这个模块将常量固定
框架项目的顶层目录
一定要注意，所有功能最好不好耦合，各个模块单独运行，有利于系统的良好运行
只有该模块，对相关环境的路径进行明确，与其他模块进行必要的联系
"""

import os
from datetime import timedelta
from pathlib import Path

from conf.config import settings

# dirname(path) 是返回path的父路径
testpath = Path(__file__).absolute()

script_dir = testpath.parent.parent.parent
## 调试模式
base_dir = testpath.parent.parent
# ## 线上版本
# base_dir = os.getcwd()


conf_dir = os.path.join(base_dir, "conf")
settings_yaml = os.path.join(conf_dir, "settings.yaml")

common_dir = os.path.join(base_dir, "common")

utils_dir = os.path.join(base_dir, "cube_test", "utils")
template_dir = os.path.join(utils_dir, "create_test_template")

data_dir = os.path.join(base_dir, "data")

demo_dir = os.path.join(base_dir, "demo")

logs_dir = os.path.join(base_dir, "logs")

output_dir = os.path.join(base_dir, "output")

# 需要的配置
import redis

redis_store = redis.Redis(host="127.0.0.1", port=6379, db=1)  # 操作的redis配置


##### 常量
ADMIN_USERNAME = "夹心巧克力"
ADMIN_PASSWORD = "ljxpaasword"
ADMIN_POWER = "超级管理员"
ADMIN_PHONE = "13525468134"


class Config:
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # flask-session配置 使用随机的字符串
    SECRET_KEY = 'ljx-test-palnt-srv'
    # flask-session配置
    SESSION_TYPE = "redis"
    SESSION_USE_SIGNER = True  # 对cookie中session_id进行隐藏处理 加密混淆
    PERMANENT_SESSION_LIFETIME = 200  # session数据的有效期，单位秒
    # JWT配置秘钥
    JWT_SECRET_KEY = 'ljx-test-palnt-srv'  # 加密
    # JWT配置过期时间
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=6)  # 1小时
    UPLOAD_FOLDER = "./logs"
    ALLOWED_EXTENSIONS = {"txt", "pdf", "png", "jpg", "jpeg", "gif"}
    MAX_CONTENT_PATH = 16 * 1024 * 1024  # 限制上传文件大小为16M


# 开发环境
class DevelopmentConfig(Config):
    """开发模式的配置信息"""

    # SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:123456@127.0.0.1:3306/test_plant'  # 使用peewee来进行测试
    SESSION_REDIS = redis.Redis(host="127.0.0.1", port=6379, db=2)  # 操作的redis配置
    DEBUG = True


# 线上环境
class ProductionConfig(Config):
    """生产环境配置信息"""

    # SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root:jamkung@pukgai.com:3306/caiji_pro'
    SESSION_REDIS = redis.Redis(
        host=settings.redis.host,
        port=settings.redis.port,
        password=settings.redis.password,
        db=settings.redis.db,
    )  # 操作的redis配置
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)  # 配置7天有效


config_map = {"develop": DevelopmentConfig, "product": ProductionConfig}


if __name__ == "__main__":
    print(os.path.abspath(""))
    print(base_dir)
