from flask import Blueprint, g, jsonify, request, session
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    get_jwt_identity,
    jwt_required,
)
from passlib.hash import pbkdf2_sha256

from conf.config import settings
from conf.constants import Config
from plant_srv.model.goods import Goods
from plant_srv.utils.error_handle import UserException
from plant_srv.utils.flask_util import get_request_info
from plant_srv.utils.json_response import JsonResponse
from plant_srv.utils.log_moudle import logger

goods = Blueprint("goods", __name__)


# 增加商品信息
@goods.route("/add", methods=["POST"])
def add_good():
    # 获取body体中的内容
    data = request.get_json()
    # 将商品的内容存储到数据库中
    good = Goods()
    good.name = data.get("name", None)
    good.price = data.get("price", None)
    good.description = data.get("description", None)
    good.image = data.get("image", None)
    good.status = data.get("status", None)
    good.subtype = data.get("subtype", None)
    good.type = data.get("type", None)
    good.save()
    # 获取good的id
    good_dict = good_info(good=good)
    return JsonResponse.success_response(data=good_dict, msg="添加完成")


# 根据参数查询指定商品详情
@goods.route("/get/by", methods=["GET"])
def get_by_id():
    goods = Goods.select()
    if request.args.get("goodid"):
        goods = goods.where(Goods.goodid == request.args.get("goodid"))
    if request.args.get("name"):
        goods = goods.where(Goods.name == request.args.get("name"))
    if request.args.get("price"):
        goods = goods.where(Goods.price == request.args.get("price"))
    if request.args.get("description"):
        # 这块是模糊搜索
        goods = goods.where(Goods.description.contains(request.args.get("description")))
    # 分页 limit offset
    start = 0
    per_page_nums = 10
    if request.args.get("pageSize"):
        per_page_nums = int(request.args.get("pageSize"))
    if request.args.get("current"):
        start = per_page_nums * (int(request.args.get("current")) - 1)
    total = goods.count()
    goods = goods.limit(per_page_nums).offset(start)
    logger.info(goods.count())
    good_list = []
    for good in goods:
        logger.debug(good_info(good=good))
        good_list.append(good_info(good=good))
    return JsonResponse.list_response(
        list_data=good_list,
        current_page=start + 1,
        total=total,
        page_size=per_page_nums,
    )


# 更新商品信息
@goods.route("/update", methods=["POST"])
def update_good():
    data = request.get_json()
    good = Goods.get(Goods.goodid == data["goodid"])
    if data.get("price"):
        good.price = data["price"]
    if data.get("description"):
        good.description = data["description"]
    if data.get("name"):
        good.name = data["name"]
    if data.get("image"):
        good.image = data["image"]
    if data.get("type"):
        good.type = data["type"]
    if data.get("subtype"):
        good.subtype = data["subtype"]
    if data.get("status"):
        good.status = data["status"]
    good.save()
    # 把修改之后的信息输出到结果中
    good_dict = good_info(good=good)
    return JsonResponse.success_response(data=good_dict)


# 删除商品信息
@goods.route("/delete", methods=["POST"])
def delete_good():
    data = request.get_json()
    good = Goods.get(Goods.goodid == data["goodid"])
    good.delete_instance()
    return JsonResponse.success_response(data={"msg": "删除成功"})


# 单个商品详细信息
def good_info(good: Goods) -> dict:
    good_dict = {}
    good_dict["id"] = good.goodid
    good_dict["name"] = good.name
    good_dict["price"] = good.price
    good_dict["description"] = good.description
    good_dict["image"] = good.image
    good_dict["status"] = good.status
    good_dict["subtype"] = good.subtype
    good_dict["type"] = good.type
    return good_dict
