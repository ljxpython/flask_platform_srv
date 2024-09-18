"""

请求前和请求后的格式处理

"""

from urllib import request

from plant_srv.model.modelsbase import database
from plant_srv.utils.log_moudle import logger


def register_middlewares(app):
    @app.before_request
    def _db_connect():
        database.connect()
        logger.info("数据库连接成功")

    # @app.after_request
    # def after_request(response):
    #     # logger.info(response.status)
    #     # logger.info(response.headers)
    #     # logger.info(response.__dict__)  # 打印response的所有属性和放啊
    #     return response

    # This hook ensures that the connection is closed when we've finished
    # processing the request.
    @app.teardown_request
    def _db_close(exc):
        if not database.is_closed():
            database.close()
            logger.info("数据库连接关闭")
