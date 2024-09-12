from flask import Blueprint, request, jsonify,g,session
import jwt
from functools import wraps

from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager

from plant_srv.model.user import User
from plant_srv.utils.log_moudle import logger
from conf.constants import Config

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

@admin.route("/user/<user>")
def set(user):
    session["user"] = user
    return {"user":user},200

@admin.route("/getuser")
def getuser():
    return {"user":session.get("user")},200

@admin.route("/deluser")
def deluser():
    # session.pop("user",None)
    session.clear()
    return {"user":session.get("user")},200

# 打印cookies
@admin.route("/cookie")
def cookie():
    logger.info(request.cookies)
    return {"cookie":request.cookies},200

# 身份验证装饰器
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token')

        if not token:
            return jsonify({'message': 'Token is missing!'}), 403

        try:
            data = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
        except:
            return jsonify({'message': 'Token is invalid!'}), 403

        return f(*args, **kwargs)

    return decorated

# 注册路由
# Create a route to authenticate your users and return JWTs. The
# create_access_token() function is used to actually generate the JWT.
@admin.route("/login", methods=["POST"])
def login():
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    if username != "test" or password != "test":
        return jsonify({"msg": "Bad username or password"}), 401

    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token)

# # 登录路由
# @admin.route('/login')
# def login():
#     auth = request.authorization
#
#     logging.info(f"Login attempt with username: {auth.username}")
#
#     if auth and auth.username in users and users[auth.username]['password'] == auth.password:
#         token = jwt.encode({'username': auth.username}, app.config['SECRET_KEY'])
#         logging.info(f"Login successful for username: {auth.username}")
#         return jsonify({'token': token.decode('UTF-8')})
#
#     logging.info(f"Login failed for username: {auth.username}")
#     return jsonify({'message': 'Authentication failed!'}), 401
#
# # 令牌刷新路由
# @admin.route('/refresh_token', methods=['POST'])
# @token_required
# def refresh_token():
#     token = request.args.get('token')
#
#     try:
#         data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=['HS256'], options={'verify_exp': False})
#         new_token = jwt.encode({'username': data['username']}, app.config['SECRET_KEY'])
#         return jsonify({'token': new_token.decode('UTF-8')})
#     except:
#         return jsonify({'message': 'Token is invalid!'}), 403

# 受保护的路由
@admin.route('/protected')
@jwt_required()
def protected():
    return jsonify({'message': 'Protected resource!'})





