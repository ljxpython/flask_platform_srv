"""
 Created by JiaXin Li
"""

from flask import Blueprint

from plant_srv.api import async_task, auto_pytest, goods, locust_test, uploadfile, user

__author__ = "JiaXin Li"


def creat_blueprint():
    api = Blueprint("api", __name__)
    api.register_blueprint(user.admin, url_prefix="/user")
    api.register_blueprint(goods.goods, url_prefix="/goods")
    api.register_blueprint(uploadfile.file, url_prefix="/uploadfile")
    api.register_blueprint(async_task.async_task, url_prefix="/async_task")
    api.register_blueprint(auto_pytest.auto_pytest, url_prefix="/auto_pytest")
    api.register_blueprint(locust_test.locust_test, url_prefix="/locust_test")
    return api
