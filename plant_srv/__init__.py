import redis
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_session import Session

from conf.config import settings
from conf.constants import config_map, redis_store
from plant_srv.api import creat_blueprint
from plant_srv.api.user import admin
from plant_srv.utils.error_handle import init_error_exception
from plant_srv.utils.log_moudle import logger
from plant_srv.utils.middlewares import register_middlewares


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_map[settings.node])  # 从类中读取需要的信息
    JWTManager(app)
    Session(app)  # 初始化session,利用flask-session，将session数据保存到redis中
    CORS(
        app, resources={r"": {"origins": "*"}}, supports_credentials=True
    )  # 允许跨域请求
    init_error_exception(app)
    register_middlewares(app)
    # 注册蓝图
    # app.register_blueprint(admin, url_prefix="/")
    app.register_blueprint(creat_blueprint(), url_prefix="/api")
    return app
