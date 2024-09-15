"""

请求前和请求后的格式处理

"""

from urllib import request

from plant_srv.utils.log_moudle import logger


def register_middlewares(app):

    @app.before_request
    def before_request():
        pass

    @app.after_request
    def after_request(response):
        # logger.info(response.status)
        # logger.info(response.headers)
        # logger.info(response.__dict__)  # 打印response的所有属性和放啊
        return response
