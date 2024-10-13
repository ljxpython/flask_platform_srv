import os
import uuid
from datetime import datetime, timedelta
from pathlib import Path
import subprocess
import signal
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
from subprocess import Popen

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
    case_sences:list = data.get("case_sences")
    if not id_:
        return JsonResponse.error_response(data="测试套件id不能为空")
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
    suite.case_sences = " ".join(case_sences)
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
        suite_list.append(model_to_dict(suite, exclude=[LocustSuite.is_deleted,LocustSuite.case_ids]))
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

# 运行压测
@locust_test.route("/run_locust_test", methods=["POST"])
def run_locust_test():
    data = request.get_json()
    force = data.get("force",False)
    # 执行测试前,先check是否有locustfiles的进程,如果有则需要根据传入是否强制终止上一次压测的参数,先杀掉进程
    locust_pids = get_locust_pids()
    if locust_pids:
        if force:
            # 强制终止
            stop_locust_process()
        else:
            return JsonResponse.error_response(data="当前有locust进程在运行,请先终止")
    # 创建一个压测result,后续存储相关测试进度
    resp = flask_util.create_model_instance(LocustTestResult)
    logger.info(resp.response)
    if not g.get("id"):
        byte_list = resp.response
        # 将字节串转换为字符串
        str_list = [byte.decode('utf-8') for byte in byte_list]
        # 然后连接它们
        result = ''.join(str_list)
        return JsonResponse.error_response(data=f"创建测试结果失败:{result}")
    # 获取创建的id
    id_ = g.id
    logger.info(f"创建测试结果成功,id为:{id_}")
    task_id = data.get("task_id",None)
    if not task_id:
        task_id = str(uuid.uuid4())
    locust_task = LocustTestResult().get(id=id_)
    locust_task.task_id = task_id
    locust_task.status = 2 # 2代表运行中 TODO 这些状态应该由util里面enum模块管理的,时间紧急,待后续优化
    locust_task.result = "Running"
    locust_task.save()
    task = scheduler.add_job(
        func=locust_test_,
        id=task_id,
        args=(id_,),
        trigger="date",
        run_date=datetime.now() + timedelta(seconds=1),
        replace_existing=True,
    )
    # TODO 给任务添加监听事件,这块暂时不想做,有点费时间,逻辑很简单,因为一般都是Ctrl键+C的方式停止测试脚本,这样的逻辑,我们不能再locust的main.py文件中动态的修改代码,这部分在2024年10月13日的locust_framework的git代码提交中,实现了,而不是通过装饰器的方式实现
    # task.add_listener()
    return JsonResponse.success_response(data={"id": id_}, msg="压测任务开始执行")


# 强制停止locust测试进行,无HTML报告生成
@locust_test.route("/force_stop_locust_test", methods=["POST"])
def force_stop_locust_test():
    resp = stop_locust_process()
    if resp:
        return JsonResponse.success_response(msg="强制停止locust测试进程成功")
    return JsonResponse.error_response(data="当前无正在运行的locust进程")


# 软停止locust测试进程
@locust_test.route("/stop_locust_test", methods=["POST"])
def stop_locust_test():
    result = LocustTestResult().get_or_none(status=2)
    if not result:
        return JsonResponse.error_response(data="当前无正在运行的locust进程")
    stop_locust_process()
    result.status = 1
    result.result = "Done"
    result.save()
    return JsonResponse.success_response(msg="停止locust测试进程成功",data={"id": result.id})

# 获取当前正在进行运行的locust测试详情
@locust_test.route("/get_locust_test_detail", methods=["GET"])
def get_locust_test_detail():
    # 查询是否有存在正在运行中的locust进程,如果没有则返回当前无测试
    locust_pids = get_locust_pids()
    if not locust_pids:
        return JsonResponse.success_response(data="当前无正在运行的locust进程")
    result = LocustTestResult().get_or_none(status=2)
    if not result:
        return JsonResponse.success_response(data="locust进程出错,请结束locust进程后重新运行")
    return JsonResponse.success_response(data={
        "id": result.id,
        "title": result.title,
        "port": result.port,
        "url": f"{settings.nginx.host}:{result.port}"
    })

# 查看当前是否还有运行中的locust进程存在
@locust_test.route("/check_locust_process", methods=["GET"])
def check_locust_process():
    locust_pids = get_locust_pids()
    logger.info(locust_pids)
    if not locust_pids:
        return JsonResponse.success_response(data="当前无正在运行的locust进程")
    return JsonResponse.success_response(data="当前有正在运行的locust进程")



def stop_locust_process():
    # 查找 Locust 进程
    locust_pids = get_locust_pids()

    if not locust_pids:
        logger.warning("No Locust processes found.")
        return False

    for pid in locust_pids:
        try:
            os.kill(int(pid), signal.SIGINT)  # 发送 SIGINT 信号
            logger.info(f"Locust process with PID {pid} has been stopped.")
        except ProcessLookupError:
            logger.error(f"Process with PID {pid} does not exist.")
        except Exception as e:
            logger.error(f"Failed to stop process with PID {pid}: {e}")
    return True


def get_locust_pids():
    """查找所有 Locust 进程的 PID"""
    # try:
    #     # 使用 pgrep 查找进程
    #     result = subprocess.run(['pgrep', '-f', 'locustfiles'], capture_output=True, text=True)
    #     return result.stdout.splitlines()  # 返回 PID 列表
    # except Exception as e:
    #     logger.error(f"Failed to find Locust processes: {e}")
    #     return []
    try:
        # 使用 ps 查找进程
        command = "ps -ef | grep locustfiles | grep -v grep | awk '{print $2}'"
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        logger.info(result.stdout)
        return result.stdout.splitlines()  # 返回 PID 列表
    except Exception as e:
        logger.error(f"Failed to find Locust processes: {e}")
        return []

def locust_test_(id_:int,):
    # 获取属性的函数
    def get_attribute(instance, attr_name):
        # logger.info(f"获取属性{getattr(instance, attr_name)}")
        return getattr(instance, attr_name, None)
    # 根据id获取locust相关配置信息
    locust_result = LocustTestResult.get_or_none(id=id_)
    logger.info(model_to_dict(locust_result))
    test_env = get_attribute(locust_result, "test_env")
    # locustsuite = get_attribute(locust_result, "locustsuite")
    title = get_attribute(locust_result, "title")
    port = get_attribute(locust_result, "port")
    users = get_attribute(locust_result, "users")
    spawn_rate = get_attribute(locust_result, "spawn_rate")
    run_time = get_attribute(locust_result, "run_time")
    headless = get_attribute(locust_result, "headless")
    tags = get_attribute(locust_result, "tags")
    exclude_tags = get_attribute(locust_result, "exclude_tags")
    case_ids = locust_result.locustsuite.case_ids
    report_dir = settings.locust_stress.report_dir
    command = f"export ENV_FOR_DYNACONF={test_env} && {settings.locust_stress.python_env} main.py --title {title} --case_ids '{case_ids}' --report_dir {report_dir}  --port {port} --id {id_} "
    if users:
        command += f"--users {users} "
    if spawn_rate:
        command += f"--spawn-rate {spawn_rate} "
    if run_time:
        command += f"--run-time {run_time} "
    if headless:
        command += f"--headless "
    if tags:
        command += f"--tags {tags} "
    if exclude_tags:
        command += f"--exclude-tags {exclude_tags} "
    logger.info(f"压测命令：{command}")
    resp = Popen(command, shell=True, cwd=settings.locust_stress.base_dir)
    return