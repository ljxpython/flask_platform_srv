# from flasgger import LazyJSONEncoder, LazyString, Swagger
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_session import Session

from conf.config import settings
from conf.constants import config_map
from plant_srv.api import creat_blueprint
from plant_srv.api.user import admin
from plant_srv.utils.error_handle import init_error_exception
from plant_srv.utils.log_moudle import logger
from plant_srv.utils.middlewares import register_middlewares
from plant_srv.utils.celery_util.create_celery_app import celery_init_app


def create_app():
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_map[settings.node])  # 从类中读取需要的信息
    # app.config.from_prefixed_env()
    JWTManager(app)
    Session(app)  # 初始化session,利用flask-session，将session数据保存到redis中
    CORS(
        app, resources={r"": {"origins": "*"}}, supports_credentials=True
    )  # 允许跨域请求
    init_error_exception(app)
    register_middlewares(app)
    celery_init_app(app)
    # Set the custom Encoder (Inherit it if you need to customize)
    # app.json_encoder = LazyJSONEncoder
    # template = dict(
    #     info={
    #         "title": LazyString(lambda: "Lazy Title"),
    #         "version": LazyString(lambda: "99.9.9"),
    #         "description": LazyString(lambda: "Hello Lazy World"),
    #         "termsOfService": LazyString(lambda: "/there_is_no_tos"),
    #     },
    #     host=LazyString(lambda: request.host),
    #     schemes=[LazyString(lambda: "https" if request.is_secure else "http")],
    #     foo=LazyString(lambda: "Bar"),
    # )
    # Swagger(app, template=template)
    # 注册蓝图
    # app.register_blueprint(admin, url_prefix="/")
    app.register_blueprint(creat_blueprint(), url_prefix="/api")
    return app
