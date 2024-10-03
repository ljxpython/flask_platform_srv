'''

执行接口的自动化测试


'''

from celery import shared_task
import time
from flask import g,request
from conf.config import settings
from plant_srv.utils.log_moudle import logger
import subprocess
from subprocess import Popen, PIPE

@shared_task(ignore_result=False)
def run_openapi_test(cases,project_name,suite_name,test_type,test_env,start_time):
    # 文件命名方式
    # project+suite+type+time
    logger.info('start run_openapi_test')
    comand = f"export ENV_FOR_DYNACONF={test_env} && {settings.test.python_env} main.py --cases 'tests/test_goods/test_good_add_del.py tests/test_goods/test_update_good.py'  --allure_dir {settings.test.report_dir}/{project_name}/{suite_name}/{test_type}/{start_time} "
    logger.info(comand)
    # time.sleep(10)
    resp = Popen(comand,shell=True, cwd=settings.test.base_dir)
    # logger.info(resp.stdout)
    return {"result": "success"}


def test_sleep():
    time.sleep(100)

