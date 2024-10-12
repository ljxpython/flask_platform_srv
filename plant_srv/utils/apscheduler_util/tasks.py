"""Example of adding tasks on app startup."""

import subprocess
import time
from datetime import datetime
from subprocess import PIPE, Popen

from celery import shared_task
from flask import g, request

from conf.config import settings
from plant_srv.utils.log_moudle import logger

from .extensions import scheduler

# TODO,当每次重启任务时,定时任务需要自动的吊起来,这部分目前没有一个自动化的手段来进行处理
# 未来可以看下,scheduler如何持久化存储任务

# @scheduler.task(
#     "interval",
#     id="job_sync",
#     seconds=1000,
#     max_instances=1,
#     start_date="2000-01-01 12:19:00",
# )
# def task1():
#     """Sample task 1.
#
#     Added when app starts.
#     """
#     print("running task 1!")  # noqa: T001

# oh, do you need something from config?
# with scheduler.app.app_context():
#     print(scheduler.app.config)  # noqa: T001


def task2(a, b):
    """Sample task 2.

    Added when /add url is visited.
    """
    time.sleep(10)
    logger.info("running task 2!")  # noqa: T001
    logger.info(a + b)
    return {"result": a + b, "taskid": "task2"}


# 方法废弃
def run_openapi_test_by_apschedule(
    cases,
    project_name,
    suite_name,
    test_type,
    test_env,
    start_time: str = datetime.now().strftime("%Y-%m-%d_%H:%M:%S"),
):
    # 文件命名方式
    # project+suite+type+test_env+start_time
    logger.info("start run_openapi_test")
    comand = f"export ENV_FOR_DYNACONF={test_env} && {settings.test.python_env} main.py --cases 'tests/test_goods/test_good_add_del.py tests/test_goods/test_update_good.py'  --allure_dir {settings.test.report_dir}/{project_name}/{suite_name}/{test_type}/{test_env}/{start_time} "
    logger.info(comand)
    # time.sleep(10)
    resp = Popen(comand, shell=True, cwd=settings.test.base_dir)
    return {"result": "success", "taskid": "task2"}
