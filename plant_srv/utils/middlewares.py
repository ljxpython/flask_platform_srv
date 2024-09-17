"""

请求前和请求后的格式处理

"""

from urllib import request

from plant_srv.model.modelsbase import database
from plant_srv.utils.log_moudle import logger


def register_middlewares(app):

    @app.before_request
    def before_request():
        logger.info(f"连接数据库")
        database.connect()

    @app.after_request
    def after_request(response):
        # logger.info(response.status)
        # logger.info(response.headers)
        # logger.info(response.__dict__)  # 打印response的所有属性和放啊
        return response

    @app.teardown_request
    def _db_close(exc):
        if not database.is_closed():
            database.close()
            logger.info(f"与数据库断开连接")
