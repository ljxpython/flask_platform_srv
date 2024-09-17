"""

错误的请求处理
用法:
    1. 导入
    def create_app():
        app = Flask(__name__)
        init_error_exception(app)
        return app

    2. 使用
        raise UserException(msg="手动测试error", http_code=417)
        raise HTTPException("xxxxxx")
文献:
    https://juejin.cn/post/7302371147977785398
"""

from http import HTTPStatus

from flask import jsonify
from werkzeug.exceptions import HTTPException

from plant_srv.utils.log_moudle import logger

ERROR_HTTP_CODE = HTTPStatus.EXPECTATION_FAILED


class UserException(Exception):
    def __init__(self, code=-1, msg="error", http_code=ERROR_HTTP_CODE):
        self.code = code
        self.msg = msg
        self.http_code = http_code


def init_error_exception(app):
    @app.errorhandler(HTTPException)
    def handler_http_exception(exception):
        logger.info(exception)
        return jsonify({"code": -1, "msg": exception.description}), exception.code

    @app.errorhandler(Exception)
    def server_exception(exception):
        logger.info(exception)
        return jsonify({"code": -1, "msg": f"内部错误:{exception}"}), ERROR_HTTP_CODE

    @app.errorhandler(UserException)
    def user_exception(exception):
        logger.info(exception)
        return (
            jsonify({"code": exception.code, "msg": exception.msg}),
            exception.http_code,
        )
