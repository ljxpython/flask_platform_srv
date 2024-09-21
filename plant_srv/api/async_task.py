'''

一些耗时比较长的异步任务都存放到这个下面

'''

from flask import Blueprint, g, jsonify, request, session
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    get_jwt_identity,
    jwt_required,
)

from conf.config import settings
from conf.constants import Config
from plant_srv.model.async_task import AsyncTask
from plant_srv.utils.error_handle import UserException
from plant_srv.utils.json_response import JsonResponse
from plant_srv.utils.log_moudle import logger
from plant_srv.utils.celery_util.task.task_demo import add_together
from plant_srv.utils.celery_util.check_task import task_result

async_task = Blueprint('async_task', __name__, url_prefix='/async_task')


@async_task.route('/add', methods=['POST'])
def add_async_task():
    data = request.get_json()
    a = data.get('a')
    b = data.get('b')
    if not a or not b:
        raise UserException('参数错误')
    task = add_together.delay(a, b)
    # 一般case是存储到数据库中,这部分代码暂时没时间来做了,暂时先阻塞
    return JsonResponse.success_response(data={'task_id': task.id})

# 查询任务结果
@async_task.route('/result/', methods=['GET'])
def get_result():
    task_id = request.args.get('task_id')
    if not task_id:
        raise UserException('参数错误')
    data = task_result(task_id)
    return JsonResponse.success_response(data=data)

