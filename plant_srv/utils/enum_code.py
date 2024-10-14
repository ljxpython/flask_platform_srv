"""

回调的状态码

参考文档:
    https://www.cnblogs.com/XY-Heruo/p/18257354

"""

from enum import Enum


class StatusCode(Enum):
    OK = 200
    BAD_REQUEST = 4001  # 客户端的参数错误
    BAD_AUTH = 4002  # 客户端鉴权错误
    BAD_CLIENT = 4003  #


class ErrorShowType(Enum):
    SILENT = 0
    WARN_MESSAGE = 1
    ERROR_MESSAGE = 2
    NOTIFICATION = 3
    REDIRECT = 9


class ErrorCode(Enum):
    OK = 0
    ERROR = 1  # 代表用户使用错误
    ERROR_HTTP_CODE = 500