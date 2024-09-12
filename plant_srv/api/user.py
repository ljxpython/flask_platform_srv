from flask import Blueprint, request, jsonify,g,session
from plant_srv.model.user import User
from plant_srv.utils.log_moudle import logger

# 创建蓝图对象
admin = Blueprint("admin", __name__)


# 获取当前用户信息
@admin.route("/user/info", methods=["GET"])
def get_user_info():
    # 获取当前用户
    users = User.select().dicts()
    logger.info(users)
    # return jsonify({"Result":list(users)}, status=200)
    return list(users)

@admin.route("/<user>")
def set(user):
    session["user"] = user
    return {"user":user},200

@admin.route("/getuser")
def getuser():
    return {"user":session.get("user")},200

