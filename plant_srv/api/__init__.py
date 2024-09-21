"""
 Created by JiaXin Li
"""

from flask import Blueprint

from plant_srv.api import goods, uploadfile, user,async_task

__author__ = "JiaXin Li"


def creat_blueprint():
    api = Blueprint("api", __name__)
    api.register_blueprint(user.admin, url_prefix="/user")
    api.register_blueprint(goods.goods, url_prefix="/goods")
    api.register_blueprint(uploadfile.file, url_prefix="/uploadfile")
    api.register_blueprint(async_task.async_task, url_prefix="/async_task")
    return api
