import os
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from subprocess import PIPE, Popen

from apscheduler.triggers.cron import CronTrigger
from celery.schedules import crontab
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
from conf.constants import Config, reports_dir, template_dir
from plant_srv.model.async_task import AsyncTask
from plant_srv.model.locust_test import LocustFunc, LocustSuite, LocustTestResult
from plant_srv.model.modelsbase import database
from plant_srv.utils.anlaysis import get_classes_methods_and_module_doc
from plant_srv.utils.apscheduler_util.extensions import scheduler
from plant_srv.utils.apscheduler_util.tasks import run_openapi_test_by_apschedule, task2
from plant_srv.utils.celery_util.check_task import task_result
from plant_srv.utils.celery_util.task.openapi_task import run_openapi_test
from plant_srv.utils.celery_util.task.task_demo import add_together
from plant_srv.utils.error_handle import UserException
from plant_srv.utils.file_operation import file_opreator
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
    logger.info(settings.test.base_dir)
    test_dir = os.path.join(settings.test.base_dir, "locustfiles")
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
        # 寻到该目录下test开头的文件
        test_case_list = [
            x.name
            for x in moudle_dir.iterdir()
            if x.is_file() and x.name.startswith("test")
        ]
        logger.info(test_case_list)
        for test_case_name in test_case_list:
            test_py = moudle_dir.joinpath(test_case_name)
            logger.info(test_py.stem)
            result = get_classes_methods_and_module_doc(test_py)
            if result["module_docstring"]:
                path_desc = result["module_docstring"]
                logger.info(f"Module Docstring: {result['module_docstring']}")

            for class_name, info in result["classes"].items():
                logger.info(f"Class: {class_name}")
                logger.info(f"  Docstring: {info['docstring']}")
                for method_name, method_doc in info["methods"].items():
                    logger.info(f"  Method: {method_name}")
                    logger.info(f"    Docstring: {method_doc}")
                    case_func = method_name
                    case_func_desc = method_doc
    return JsonResponse.success_response(data={"msg": "ok"})
