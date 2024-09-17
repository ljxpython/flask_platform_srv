"""

flask中常用的工具添加

"""

from flask import g, jsonify, request, session


# 将body中和param中的参数放到一起
def get_request_info():
    class RequestInfo(object):
        params = request.args.to_dict()
        body = request.get_json()

    return RequestInfo()
