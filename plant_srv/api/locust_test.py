import os
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from subprocess import PIPE, Popen

from apscheduler.triggers.cron import CronTrigger
from flask import (
    Blueprint,
    g,
    jsonify,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
    url_for,
)
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    get_jwt_identity,
    jwt_required,
)
from playhouse.shortcuts import model_to_dict

from conf.config import settings
from plant_srv.model.locust_test import (
    LocustFunc,
    LocustShape,
    LocustSuite,
    LocustTestResult,
)
from plant_srv.utils.anlaysis import get_classes_methods_and_module_doc
from plant_srv.utils.apscheduler_util.extensions import scheduler
from plant_srv.utils.apscheduler_util.tasks import run_openapi_test_by_apschedule, task2
from plant_srv.utils.celery_util.check_task import task_result
from plant_srv.utils.flask_util import flask_util
from plant_srv.utils.json_response import JsonResponse
from plant_srv.utils.log_moudle import logger

locust_test = Blueprint("locust_test", __name__, url_prefix="/locust_test")


# 同步locust测试case
@locust_test.route("/sync_locust_case", methods=["POST"])
def sync_locust_case():
    """
    同步测试用例
        1. 遍历目标文件夹,获取Case名称
    """
    logger.info(settings.locust_stress.base_dir)
    test_dir = os.path.join(settings.locust_stress.base_dir, "locustfiles")
    # 遍历测试目录,获取该目录下所有文件夹的
    path = Path(test_dir)
    moudle_list = [x.name for x in path.iterdir() if x.is_dir()]
    # 如果存在__pycache__,则去除
    if "__pycache__" in moudle_list:
        moudle_list.remove("__pycache__")
    logger.info(moudle_list)
    for moudle_name in moudle_list:
        moudle_dir = path.joinpath(moudle_name)
        logger.info(moudle_dir)
        # 寻到该目录下py文件除去__init__.py
        test_case_list = [
            x.name
            for x in moudle_dir.iterdir()
            if x.is_file()
            and x.suffix == ".py"
            and "__init__" not in x.name
            and x.name.startswith("test")
        ]
        logger.info(test_case_list)
        for test_case_name in test_case_list:
            test_py = moudle_dir.joinpath(test_case_name)
            logger.info(test_py.stem)
            result = get_classes_methods_and_module_doc(test_py)
            if result["module_docstring"]:
                path_desc = result["module_docstring"]
                logger.info(f"Module Docstring: {result['module_docstring']}")
                # 同步数据库中
                if not LocustFunc().get_or_none(case_path=test_py):
                    LocustFunc.create(
                        moudle=moudle_name,
                        case_path=test_py,
                        case_sence=test_py.stem,
                        path_desc=path_desc,
                    )
                else:
                    # 如果存在,则更新
                    case_func = LocustFunc().get(
                        LocustFunc.case_path == test_py,
                    )
                    case_func.moudle = moudle_name
                    case_func.case_sence = test_py.stem
                    case_func.path_desc = path_desc
                    case_func.save()

        ##TODO 这部分的逻辑也不严谨,如果有废弃的case,应该删除这条数据,这部分的逻辑没有完成,未来有时间 进行这部分的优化吧
    return JsonResponse.success_response(
        data={"moudle_list": moudle_list}, msg="同步压测测试模块成功,所有模块列表如上"
    )


# 根据条件查找locustcase
@locust_test.route("/get_locust_case", methods=["GET"])
def get_locust_case():
    """
    根据条件查找locustcase
    """
    cases = LocustFunc().select()
    if request.args.get("moudle"):
        cases = cases.where(LocustFunc.moudle == request.args.get("moudle"))
    if request.args.get("case_sence"):
        cases = cases.where(LocustFunc.case_sence == request.args.get("case_sence"))
    if request.args.get("tags"):
        cases = cases.where(LocustFunc.tags == request.args.get("tags"))
    # 分页 limit offset
    start = 0
    per_page_nums = 10
    if request.args.get("pageSize"):
        per_page_nums = int(request.args.get("pageSize"))
    if request.args.get("current"):
        start = per_page_nums * (int(request.args.get("current")) - 1)
    total = cases.count()
    cases = cases.limit(per_page_nums).offset(start)
    logger.info(cases.count())
    case_list = []
    # logger.info(cases.dicts())
    for case in cases:
        logger.info(case)
        logger.info(model_to_dict(case))
        case_list.append(
            model_to_dict(case, exclude=[LocustFunc.add_time, LocustFunc.case_path])
        )
    return JsonResponse.list_response(
        list_data=case_list,
        current_page=start + 1,
        total=total,
        page_size=per_page_nums,
    )


# 删除测试case
@locust_test.route("/delete_locust_case", methods=["POST"])
def delete_locust_case():
    resp = flask_util.delete_api(
        LocustFunc,
    )
    return resp


# 创建locust测试套件
@locust_test.route("/create_locust_suite", methods=["POST"])
def create_locust_suite():
    """
    创建locust测试套件
    """
    data = request.get_json()
    suite_name = data.get("suite_name")
    describe = data.get("describe")
    case_ids = data.get("case_ids")
    logger.info(f"suite_name:{suite_name},project_name:{describe}")
    if not suite_name:
        return JsonResponse.error_response(data="suite_name不能为空")
    if LocustSuite().get_or_none(suite_name=suite_name):
        return JsonResponse.error_response(data="suite_name已经存在")
    suite = LocustSuite.create(
        suite_name=suite_name, describe=describe, case_ids=case_ids
    )
    return JsonResponse.success_response(
        data={"suite": model_to_dict(suite, exclude=[LocustSuite.is_deleted])},
        msg="创建测试套件成功",
    )


# 根据case_sence同步测试套件
@locust_test.route("/sync_locust_suite_by_case_ids", methods=["POST"])
def sync_locust_suite():
    """
        根据case_sence同步测试套件
        请求例子:
        {
        "suite_name":"good-test-1",
        "case_sences": ["test_good_add_del","test_update_good"]
    }
    """
    data = request.get_json()
    id_ = data.get("id")
    suite_name = data.get("suite_name")
    case_sences = data.get("case_sences")
    if not id_:
        return JsonResponse.error_response(data="测试套件id不能为空")
    # if not suite_name:
    #     return JsonResponse.error_response(data="测试套件名称不能为空")
    if not case_sences:
        return JsonResponse.error_response(data="测试场景不能为空")
    # 根据case_sences查找case集合
    cases = LocustFunc.select().where(LocustFunc.case_sence.in_(case_sences))
    # 如果为空,则抛出异常
    count = cases.count()
    case_ids = []
    if count == 0:
        return JsonResponse.error_response(data="测试场景不存在")
    for case in cases:
        logger.info(case.case_path)
        case_ids.append(case.case_path)
    # 对case_ids进行去重
    case_ids = list(set(case_ids))
    # 根据suite_name查找测试套件
    suite = LocustSuite().get_or_none(id=id_)
    if not suite:
        return JsonResponse.error_response(data="测试套件不存在")
    suite = LocustSuite.get(id=id_)
    suite.case_ids = " ".join(case_ids)
    logger.info(suite.case_ids)
    suite.save()
    return JsonResponse.success_response(
        data={
            "suite": model_to_dict(
                suite, exclude=[LocustSuite.is_deleted, LocustSuite.case_ids]
            )
        },
        msg="同步测试套件成功",
    )


# 查询locust测试套件
@locust_test.route("/query_locust_suite", methods=["GET"])
def query_locust_suite():
    suite_name = request.args.get("suite_name")
    id_ = request.args.get("id")
    suites = LocustSuite.select()
    if suite_name:
        suites = suites.where(LocustSuite.suite_name == suite_name)
    if id_:
        suites = suites.where(LocustSuite.id == id_)
    suite_list = []
    # 分页 limit offset
    start = 0
    per_page_nums = 10
    if request.args.get("pageSize"):
        per_page_nums = int(request.args.get("pageSize"))
    if request.args.get("current"):
        start = per_page_nums * (int(request.args.get("current")) - 1)
    total = suites.count()
    suites = suites.limit(per_page_nums).offset(start)
    for suite in suites:
        suite_list.append(model_to_dict(suite, exclude=[LocustSuite.is_deleted]))
    return JsonResponse.list_response(
        list_data=suite_list,
        total=total,
        current_page=start + 1,
        page_size=per_page_nums,
    )


# 删除测试套件
@locust_test.route("/delete_locust_suite", methods=["POST"])
def delete_locust_suite():
    data = request.get_json()
    id_ = data.get("id")
    if not id_:
        return JsonResponse.error_response(data="测试套件id不能为空")
    suite = LocustSuite().get_or_none(id=id_)
    if not suite:
        return JsonResponse.error_response(data="测试套件不存在")
    suite = LocustSuite().get(id=id_)
    suite.delete_instance(permanently=True)
    return JsonResponse.success_response(msg="删除测试套件成功")


# 创建测试结果
@locust_test.route("/create_locust_result", methods=["POST"])
def create_locust_result():
    resp = flask_util.create_model_instance(LocustTestResult)
    return resp


# 查询测试结果
@locust_test.route("/query_locust_result", methods=["GET"])
def query_locust_result():
    resp = flask_util.list_pagenation(
        LocustTestResult, exclude=[LocustTestResult.is_deleted], recurse=False
    )
    return resp


# 同步测试结果
@locust_test.route("/sync_locust_result", methods=["POST"])
def sync_locust_result():
    resp = flask_util.update_api(LocustTestResult)
    return resp


# 删除测试结果
@locust_test.route("/delete_locust_result", methods=["POST"])
def delete_locust_result():
    resp = flask_util.delete_api(LocustTestResult)
    return resp
