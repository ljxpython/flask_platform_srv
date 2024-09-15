"""

统一回调的格式及内容
    包含字段:
        1. code字段:code状态码主要用于表示错误类型区间状态码。如果设计比较简单，可以直接使用HTTP的状态码。如果是一个大型系统，也可以设计一套自定义的状态码。
        2. message字段: message 字段是对当前 code 状态码错误明细的补充说明。通常不同的code状态码会有不同的message描述信息。
        3. data字段: data 值通常代表返回的响应体内容。
"""

from http import HTTPStatus

from flask import Flask, jsonify, make_response, request


class JsonResponse:
    """A class to represent a JSON response."""

    def __init__(
        self, code: HTTPStatus = HTTPStatus.OK, msg: str = "success", data=None
    ):
        self.code = code
        self.msg = msg
        self.data = data

    def to_dict(self):
        return {
            "code": self.code.value,
            "msg": self.msg,
            "data": self.data,
        }

    def to_json(self):
        return jsonify(self.to_dict())

    # 增加headers及data参数的修改
    def response(self, add_haders: dict = None):
        response = make_response(self.to_json(), self.code.value)
        if add_haders is not None:
            response.headers.update(add_haders)
        # 如果response的请求的方式是post,增加Content-Type = "application/json"
        # response.headers["Content-Type"] = "application/json"
        return response

    # 添加一个常用的成功返回
    def sucess(self):
        return self.response()
