import redis
from flask import Flask
from flask_cors import CORS
from flask_session import Session
from flask_jwt_extended import JWTManager

from conf.config import settings
from conf.constants import config_map,redis_store
from plant_srv.utils.log_moudle import logger
from plant_srv.api.user import admin


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_map[settings.node])  # 从类中读取需要的信息
    JWTManager(app)
    Session(app)  # 初始化session,利用flask-session，将session数据保存到redis中
    CORS(app,resources={r"": {"origins": "*"}}, supports_credentials=True)  # 允许跨域请求
    # 注册蓝图
    app.register_blueprint(admin, url_prefix='/')
    return app
