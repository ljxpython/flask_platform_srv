# from flasgger import LazyJSONEncoder, LazyString, Swagger
import logging
import os

from flask import Flask
from flask_apscheduler import APScheduler
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_session import Session

from conf.config import settings
from conf.constants import config_map
from plant_srv.api import creat_blueprint
from plant_srv.api.user import admin
from plant_srv.utils.apscheduler_util.extensions import scheduler
from plant_srv.utils.celery_util.create_celery_app import celery_init_app
from plant_srv.utils.error_handle import init_error_exception
from plant_srv.utils.log_moudle import logger
from plant_srv.utils.middlewares import register_middlewares


def create_app():
    def is_debug_mode():
        """Get app debug status."""
        debug = os.environ.get("FLASK_DEBUG")
        if not debug:
            return os.environ.get("FLASK_ENV") == "development"
        return debug.lower() not in ("0", "false", "no")

    def is_werkzeug_reloader_process():
        """Get werkzeug status."""
        return os.environ.get("WERKZEUG_RUN_MAIN") == "true"

    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(config_map[settings.node])  # 从类中读取需要的信息
    # app.config.from_prefixed_env()
    JWTManager(app)
    Session(app)  # 初始化session,利用flask-session，将session数据保存到redis中
    CORS(
        app, resources={r"": {"origins": "*"}}, supports_credentials=True
    )  # 允许跨域请求
    # 线上环境开启异常

    if settings.env == "online":
        init_error_exception(app)
    register_middlewares(app)
    # celery_init_app(app)

    scheduler.init_app(app)
    logging.getLogger("apscheduler").setLevel(logging.INFO)
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
    # app.register_blueprint(creat_blueprint(), url_prefix="/api")
    # pylint: disable=C0415, W0611
    with app.app_context():
        # pylint: disable=W0611
        if is_debug_mode() and not is_werkzeug_reloader_process():
            pass
        else:
            from plant_srv.utils.apscheduler_util import tasks

            scheduler.start()

        from plant_srv.utils.apscheduler_util import events

        app.register_blueprint(creat_blueprint(), url_prefix="/api")

        return app

    # return app
