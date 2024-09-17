"""
 Created by JiaXin Li
"""

from flask import Blueprint

from plant_srv.api import goods, user

__author__ = "JiaXin Li"


def creat_blueprint():
    api = Blueprint("api", __name__)
    api.register_blueprint(user.admin, url_prefix="/user")
    api.register_blueprint(goods.goods, url_prefix="/goods")
    return api
