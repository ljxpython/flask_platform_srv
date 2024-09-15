from functools import wraps

import jwt
from flask import Blueprint, g, jsonify, request, session
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    get_jwt_identity,
    jwt_required,
)
from passlib.hash import pbkdf2_sha256

from conf.constants import Config
from plant_srv.model.user import User
from plant_srv.utils.error_handle import UserException
from plant_srv.utils.json_response import JsonResponse
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
    return JsonResponse(data=list(users)).response()


# 用户注册
@admin.route("/register", methods=["POST"])
def register_user():
    data = request.get_json()
    # 获取需要注册的用户名
    user_name = data.get("username")
    logger.info(f"user_name: {user_name}")
    # 获取需要注册的用户密码
    password = data.get("password")
    logger.info(f"password: {password}")
    # 确认用户名与数据库中的不重复,如果重复则报错
    res = User().get_or_none(name=user_name)
    logger.info(f"res: {res}")
    # 如果res == None ,则代表不存在
    if res is None:
        # 对密码进行加密,存入到数据库中
        hash = pbkdf2_sha256.hash(password)
        # 存储到数据库中
        user = User.create(name=user_name, password=hash)
        user.save()
    else:
        # 抛出用户名重复的错误
        raise UserException("User already exists")
    return JsonResponse(data={"success": True}).response()


# 注册路由
# Create a route to authenticate your users and return JWTs. The
# create_access_token() function is used to actually generate the JWT.
@admin.route("/login", methods=["POST"])
def login():
    username = request.json.get("username", None)
    password = request.json.get("password", None)
    # 首先判断是否存在该用户
    res = User().get_or_none(name=username)
    logger.info(f"res: {res}")
    if res is None:
        # 如果不存在则抛出异常
        raise UserException("User does not exist")
    # 从数据库中,读取该用户的密码
    s_user_password = User.get(name=username).password
    logger.info(f"s_user_password: {s_user_password}")
    # 确认密码一致
    res = pbkdf2_sha256.verify(password, s_user_password)
    if res is False:
        raise UserException("Invalid password")
    # 之后把用户数据存储到session中
    session["user"] = username
    access_token = create_access_token(identity=username)
    logger.info(access_token)
    # return jsonify(access_token=access_token)
    return JsonResponse(data={"success": True}).response(
        add_haders={"Authorization": f"Bearer {access_token}"}
    )


# 用户退出
@admin.route("/logout", methods=["POST"])
def logout():
    # 这里面登出还应该做一步,把jwt的鉴权放入黑名单中,但是测试我暂时先不做这部分处理,相关方法我放到自己的文档中,待未来优化
    session.clear()
    return JsonResponse(data={"success": True}).response()


@admin.route("/user/<user>")
def set(user):
    session["user"] = user
    return {"user": user}, 200


@admin.route("/getuser")
def getuser():
    return {"user": session.get("user")}, 200


@admin.route("/deluser")
def deluser():
    # session.pop("user",None)
    session.clear()
    return {"user": session.get("user")}, 200


# 打印cookies
@admin.route("/cookie")
def cookie():
    logger.info(request.cookies)
    return {"cookie": request.cookies}, 200


# 触发异常
@admin.route("/error", methods=["POST"])
def error():
    # raise UserException(msg="调试问题", http_code=417)
    raise Exception(f"服务端崩溃")


"""

下面是旧写法,未使用flask-jwt,自己实现的,暂时不用了,使用第三方库的鉴权方式

"""

# # 身份验证装饰器
# def token_required(f):
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         token = request.args.get("token")
#
#         if not token:
#             return jsonify({"message": "Token is missing!"}), 403
#
#         try:
#             data = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
#         except:
#             return jsonify({"message": "Token is invalid!"}), 403
#
#         return f(*args, **kwargs)
#
#     return decorated

# @admin.before_request
# def before_request():
#     # 有了jwt这种鉴权方式后,就不太需要前置request中做限制了,我们反而需要后置中,把格式考虑好
#     # logger.info(f"admin bedore request")
#     pass

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
@admin.route("/protected")
@jwt_required()
def protected():
    logger.info(get_jwt_identity())
    return jsonify({"message": "Protected resource!"})
