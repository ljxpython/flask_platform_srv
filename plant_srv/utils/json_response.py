"""

统一回调的格式及内容
    包含字段:
        1. code字段:code状态码主要用于表示错误类型区间状态码。如果设计比较简单，可以直接使用HTTP的状态码。如果是一个大型系统，也可以设计一套自定义的状态码。
        2. message字段: message 字段是对当前 code 状态码错误明细的补充说明。通常不同的code状态码会有不同的message描述信息。
        3. data字段: data 值通常代表返回的响应体内容。

阿里推荐的接口规范:
        {
    "success": true,
    "data": {},
    "errorCode": "1001",
    "errorMessage": "error message",
    "showType": 2,
    "traceId": "someid",
    "host": "10.1.1.1"
    }

对于简单的可以如下：
        {
    "success": true,
    "data": {},
    "errorMessage": "error message"
    }

对于查询类的接口可以如下:
        {
     list: [
     ],
     current?: number,
     pageSize?: number,
     total?: number,
    }

最后,我个人使用简单的表述方式:
E.g:
    1. 登录成功的返回
        {
        "success": true,
        "data": {
            "token": "<PASSWORD>",
            },
        }
    2. 退出登录
        {
        "success": true,
        "data": {
            "msg": "user: {username} is logout"
            },
        }
    3. 登录异常返回
        {
        "success": false,
        "data": {},
        "errorMessage": "error message"
        }
    4. 执行某个接口
        {
        "success": true,
        "data": {},
        }
    5. 查询某个接口
        {
        list: [
        ],
        current?: number,
        pageSize?: number,
        total?: number,
        }

因此,具体的代码实现如下:
    增加代码的灵活性,使用*arg,**kwg支持将传入参数都放入body中返回
    指定接口必须传入的参数:
        1. 成功接口:
        2. 失败接口:
        3. 查询接口:
"""

from http import HTTPStatus

from flask import Flask, jsonify, make_response, request


class JsonResponse:
    """A class to represent a JSON response."""

    code = HTTPStatus.OK

    # def __init__(
    #     self, code: HTTPStatus = HTTPStatus.OK, msg: str = "success", data=None,pageSize:int=None,total:int=None,current_page:int=None
    # ):
    #     self.code = code
    #     self.msg = msg
    #     self.data = data
    def __init__(
        self,
    ):
        self.success = True
        self.data = {}
        self.errorMessage = None
        self.errorCode = None
        self.traceId = None
        self.host = None
        self.list = None
        self.pageSize = None
        self.total = None
        self.current = None
        # self.code = HTTPStatus.OK

    # def to_dict(self):
    #     return {
    #         "code": self.code.value,
    #         "msg": self.msg,
    #         "data": self.data,
    #     }

    # def to_json(self):
    #     return jsonify(self.to_dict())

    # 增加headers及data参数的修改
    # def response(self, add_haders: dict = None):
    #     response = make_response(self.to_json(), self.code.value)
    #     if add_haders is not None:
    #         response.headers.update(add_haders)
    #     # 如果response的请求的方式是post,增加Content-Type = "application/json"
    #     # response.headers["Content-Type"] = "application/json"
    #     return response

    @classmethod
    def response(
        cls, data: dict | list = None, code: int = None, headers: dict = None, **kwargs
    ):
        if code is None:
            code = cls.code.value
        res = make_response(jsonify(data), code)
        if headers:
            res.headers.update(headers)
        return res

    # 添加一个常用的成功返回
    @classmethod
    def success_response(cls, headers: dict = None, data: dict | list = None, **kwargs):
        # data及**kwargs中的数据存到到一个字典中
        respose_dict = {"data": data}
        respose_dict.update(**kwargs)
        respose_dict.update({"success": True})
        return cls.response(data=respose_dict, headers=headers, **kwargs)

    # 一个常用的失败的返回
    @classmethod
    def error_response(cls, headers: dict | list = None, data: dict = None, **kwargs):
        data = {
            "data": data,
            "success": False,
        }
        return cls.response(data=data, headers=headers, **kwargs)

    # 查询分页类接口
    @classmethod
    def list_response(
        cls,
        list_data: list,
        current_page: int = None,
        total: int = None,
        page_size: int = None,
        header: dict = None,
        **kwargs
    ):
        data = {
            "data": list_data,
            "current": current_page,
            "pageSize": page_size,
            "total": total,
        }
        return cls.response(data=data, headers=header, **kwargs)

    # 一般常用的是成功的返回,因为,把他用Python的魔法函数__call__来表示,这样更加简洁
    def __call__(
        cls, data: dict = None, code: int = None, headers: dict = None, **kwargs
    ):
        respose_dict = {"data": data}
        respose_dict.update(**kwargs)
        respose_dict.update({"success": True})
        return cls.response(data=respose_dict, headers=headers, **kwargs)
