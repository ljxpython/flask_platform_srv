import json
import os
import re
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
from conf.constants import Config, reports_dir, template_dir
from plant_srv.model.auto_pytest import (
    CaseFunc,
    CaseMoudle,
    CaseTag,
    Project,
    Suite,
    TestPlan,
    TestResult,
)
from plant_srv.utils.anlaysis import get_classes_methods_and_module_doc
from plant_srv.utils.apscheduler_util.extensions import scheduler
from plant_srv.utils.apscheduler_util.tasks import run_openapi_test_by_apschedule, task2
from plant_srv.utils.celery_util.task.task_demo import add_together
from plant_srv.utils.error_handle import UserException
from plant_srv.utils.flask_util import flask_util
from plant_srv.utils.json_response import JsonResponse
from plant_srv.utils.log_moudle import logger

"""
TODO:
    已经完成了分页查询的封装
    其实增删改查接口都是可以实现封装的,这个可以留到后面封装优化

"""

auto_pytest = Blueprint(
    "auto_pytest", __name__, url_prefix="/auto_pytest", template_folder=reports_dir
)


# 展示测试报告
@auto_pytest.route("/show_report", methods=["GET"])
def show_report():
    # 跳转到报告页面
    return redirect("http://www.coder-ljx.cn:8080/html")


# 同步测试模块
@auto_pytest.route("/sync_test_moudle", methods=["POST"])
def sync_test_moudle():
    """
    同步测试模块
        1. 遍历目标文件夹,获取Moudle名称
    """
    logger.info(settings.test.base_dir)
    test_dir = os.path.join(settings.test.base_dir, "tests")
    # 遍历测试目录,获取该目录下所有文件夹的
    path = Path(test_dir)
    moudle_list = [x.name for x in path.iterdir() if x.is_dir()]
    # 如果存在__pycache__,则去除
    if "__pycache__" in moudle_list:
        moudle_list.remove("__pycache__")
    logger.info(moudle_list)
    # 添加到CaseMoudle表中
    for moudle_name in moudle_list:
        # 查询数据库中是否存在该Moudle,如果存在跳过,如果不存在,则存入到数据库中
        istrue = CaseMoudle().get_or_none(moudle=moudle_name)
        if not istrue:
            c = CaseMoudle.create(moudle=moudle_name)
            logger.info(c)
    ##TODO 这边逻辑其实不严谨,如果有的模块已经失效,应该删除,但是并未做这部分的逻辑处理,待时间富裕,可以优化这部分内容

    return JsonResponse.success_response(
        data={"moudle_list": moudle_list}, msg="同步测试模块成功,所有模块列表如上"
    )


# 更新测试模块
@auto_pytest.route("/update_test_moudle", methods=["POST"])
def update_test_moudle():
    """
    给测试模块添加相应的描述
    """
    resp = flask_util.update_api(CaseMoudle)
    return resp
    # data = request.get_json()
    # id_ = data.get("id")
    # moudle_name = data.get("moudle")  # 测试模块名称
    # moudle_desc = data.get("desc")  # 测试模块描述
    # logger.info(f"moudle_name:{moudle_name},moudle_desc:{moudle_desc}")
    # # 查询数据库中是否存在该Moudle,如果存在,则更新,如果不存在,则返回错误
    # c = CaseMoudle().get_or_none(id=id_)
    # logger.info(c)
    # if c:  # 如果存在,则更新
    #     logger.info(f"该模块存在,进行更新操作")
    #     casemoudle = CaseMoudle().get(id=id_)
    #     casemoudle.moudle_name = moudle_name
    #     casemoudle.moudle_desc = moudle_desc
    #     casemoudle.save()
    # else:
    #     return JsonResponse.error_response(error_message="该模块不存在数据库中,请先同步测试模块")
    # return JsonResponse.success_response(
    #     data={"moudle_name": moudle_name, "moudle_desc": moudle_desc},
    #     msg="更新测试模块成功",
    # )


# 查询测试模块
@auto_pytest.route("/query_test_moudle", methods=["GET"])
def query_test_moudle():
    """
    查询测试模块
    """
    id_ = request.args.get("id")
    moudle_list = CaseMoudle().select()
    if id_:
        moudle_list = moudle_list.where(CaseMoudle.id == id_)
    # 分页 limit offset
    start = 0
    per_page_nums = 10
    if request.args.get("pageSize"):
        per_page_nums = int(request.args.get("pageSize"))
    if request.args.get("current"):
        start = per_page_nums * (int(request.args.get("current")) - 1)
    total = moudle_list.count()
    cases = moudle_list.limit(per_page_nums).offset(start)
    logger.info(cases.count())
    case_list = []
    # logger.info(cases.dicts())
    for case in cases:
        logger.info(case)
        logger.info(model_to_dict(case))
        case_list.append(
            model_to_dict(case, exclude=[CaseMoudle.add_time, CaseMoudle.is_deleted])
        )
    return JsonResponse.list_response(
        list_data=case_list,
        current_page=start + 1,
        total=total,
        page_size=per_page_nums,
    )


# 同步测试用例
@auto_pytest.route("/sync_test_case", methods=["POST"])
def sync_test_case():
    """
    同步测试用例
        1. 遍历目标文件夹,获取Case名称
    """
    logger.info(settings.test.base_dir)
    test_dir = os.path.join(settings.test.base_dir, "tests")
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
            path_desc = ""
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
                    # 同步数据库中
                    if not CaseFunc().get_or_none(
                        case_func=case_func, case_path=test_py
                    ):
                        logger.info(f"{moudle_name}")
                        # casemoudl
                        case_moudle = CaseMoudle().get_or_none(moudle=moudle_name)
                        logger.info(case_moudle)
                        case_func = CaseFunc.create(
                            casemoudle=case_moudle,
                            case_path=test_py,
                            case_sence=test_py.stem,
                            path_desc=path_desc,
                            case_func=case_func,
                            case_func_desc=case_func_desc,
                        )
                    else:
                        # 如果存在,则更新
                        case_func = CaseFunc().get(
                            CaseFunc.case_func == case_func,
                            CaseFunc.case_path == test_py,
                        )
                        case_moudle = CaseMoudle().get_or_none(moudle=moudle_name)
                        logger.info(case_moudle)
                        case_func.case_func_desc = case_func_desc
                        case_func.casemoudle = case_moudle
                        case_func.case_sence = test_py.stem
                        case_func.path_desc = path_desc
                        case_func.save()
                    ##TODO 这部分的逻辑也不严谨,如果有废弃的case,应该删除这条数据,这部分的逻辑没有完成,未来有时间 进行这部分的优化吧

    return JsonResponse.success_response(
        data={"moudle_list": moudle_list}, msg="同步测试模块成功,所有模块列表如上"
    )


# 根据条件查找测试case
@auto_pytest.route("/get_case", methods=["POST"])
def get_case():
    cases = CaseFunc.select()
    data = request.get_json()
    if data.get("id"):
        logger.info(data.get("id"))
        cases = cases.where(CaseFunc.id == data.get("id"))
    if data.get("casemoudle"):
        cases = cases.where(CaseFunc.casemoudle.in_(data.get("casemoudle")))
    if data.get("case_func"):
        cases = cases.where(CaseFunc.case_func == data.get("case_func"))
    if data.get("case_sence"):
        # def extract_case_sence(case_sence):
        #     # 检查是否包含中文字符或中文逗号
        #     if re.search(r'[\u4e00-\u9fff]', case_sence) or '，' in case_sence or ' ' in case_sence:
        #         # 使用中文逗号分割字符串，并去掉每个元素的前后空白字符
        #         elements = [elem.strip() for elem in re.split(r'，|,', case_sence)]
        #         return elements
        #     return [case_sence]
        # # 根据 case_sence中的中文或者应逗号对其分割,之后元素存放到列表中
        # case_sence_list = extract_case_sence(data.get("case_sence"))
        # logger.info(f"case_sence_list: {case_sence_list}")
        cases = cases.where(CaseFunc.case_sence.in_(data.get("case_sence")))
    if data.get("tags"):
        cases = cases.where(CaseFunc.tags.in_(data.get("tags")))
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
            model_to_dict(
                case,
                exclude=[CaseFunc.add_time, CaseFunc.case_path, CaseFunc.is_deleted],
                backrefs=True,
            )
        )
    return JsonResponse.list_response(
        list_data=case_list,
        current_page=start + 1,
        total=total,
        page_size=per_page_nums,
    )


# 获取所有测试场景
@auto_pytest.route("/get_case_sence", methods=["POST"])
def get_case_sence():
    cases = CaseFunc.select()
    case_sence_list = []
    for case in cases:
        case_sence_list.append(case.case_sence)
    # 去重
    case_sence_list = list(set(case_sence_list))
    return JsonResponse.success_response(
        data={"case_sence_list": case_sence_list}, msg="获取所有测试场景成功"
    )


# 创建测试项目
@auto_pytest.route("/create_project", methods=["POST"])
def create_project():
    data = request.get_json()
    project_name = data.get("project_name")
    project_desc = data.get("project_desc")
    project_owners = data.get("project_owners")

    if not project_name:
        return JsonResponse.error_response(error_message="项目名称不能为空")
    if Project().get_or_none(project_name=project_name):
        return JsonResponse.error_response(error_message="项目名称已经存在")
    if not project_desc:
        return JsonResponse.error_response(error_message="项目描述不能为空")
    if not project_owners:
        return JsonResponse.error_response(error_message="项目负责人不能为空")
    project = Project.create(
        project_name=project_name,
        project_desc=project_desc,
        project_owners=project_owners,
    )
    return JsonResponse.success_response(
        data={"project": model_to_dict(project, exclude=[Project.is_deleted])},
        msg="创建项目成功",
    )


# 修改测试项目
@auto_pytest.route("/update_project", methods=["POST"])
def update_project():
    data = request.get_json()
    id_ = data.get("id")
    project_name = data.get("project_name")
    project_desc = data.get("project_desc")
    project_owners = data.get("project_owners")
    if not id_:
        return JsonResponse.error_response(error_message="项目id不能为空")
    project = Project().get_or_none(id=id_)
    if not project:
        return JsonResponse.error_response(error_message="项目不存在")
    project = Project().get(id=id_)
    if project_name:
        project.project_name = project_name
    if project_desc:
        project.project_desc = project_desc
    if project_owners:
        project.project_owners = project_owners
    project.save()
    return JsonResponse.success_response(
        data={"project": model_to_dict(project, exclude=[Project.is_deleted])},
        msg="修改项目成功",
    )


# 删除测试项目
@auto_pytest.route("/delete_project", methods=["POST"])
def delete_project():
    data = request.get_json()
    id_ = data.get("id")
    logger.info(id_)
    if not id_:
        return JsonResponse.error_response(error_message="项目id不能为空")
    project = Project().get_or_none(id=id_)
    if not project:
        return JsonResponse.error_response(error_message="项目不存在")
    else:
        logger.info(model_to_dict(project))
    project.delete_instance(permanently=True)
    return JsonResponse.success_response(msg="删除项目成功")


# 获取测试项目列表
@auto_pytest.route("/get_project_list", methods=["GET"])
def get_project_list():
    projects = Project.select()
    # data = request.get_json()
    id_ = request.args.get("id")
    project_name = request.args.get("project_name")
    project_desc = request.args.get("project_desc")
    project_owners = request.args.get("project_owners")
    if id_:
        projects = projects.where(Project.id == id_)
    if project_name:
        projects = projects.where(Project.project_name == project_name)
    if project_desc:
        projects = projects.where(Project.project_desc == project_desc)
    if project_owners:
        projects = projects.where(Project.project_owners == project_owners)
    # 分页 limit offset
    start = 0
    per_page_nums = 10
    if request.args.get("pageSize"):
        per_page_nums = int(request.args.get("pageSize"))
    if request.args.get("current"):
        start = per_page_nums * (int(request.args.get("current")) - 1)
    total = projects.count()
    projects = projects.limit(per_page_nums).offset(start)
    project_list = []
    for project in projects:
        logger.info(model_to_dict(project, exclude=[Project.is_deleted]))
        project_list.append(model_to_dict(project, exclude=[Project.is_deleted]))
    return JsonResponse.list_response(
        list_data=project_list,
        total=total,
        page_size=per_page_nums,
        current_page=start + 1,
    )


# 创建测试标签
@auto_pytest.route("/create_tag", methods=["POST"])
def create_tag():
    data = request.get_json()
    tag = data.get("tag")
    if not tag:
        return JsonResponse.error_response(msg="标签不能为空")
    if CaseTag().get_or_none(tag=tag):
        return JsonResponse.error_response(msg="标签已经存在")
    CaseTag.create(tag=tag)
    return JsonResponse.success_response(msg="创建标签成功")


# 获取测试标签列表
@auto_pytest.route("/get_tag_list", methods=["GET"])
def get_tag_list():
    tags = CaseTag.select()
    tag_list = []
    for tag in tags:
        tag_list.append(model_to_dict(tag, exclude=[CaseTag.is_deleted]))
    return JsonResponse.success_response(
        data={"tag_list": tag_list}, msg="获取标签列表成功"
    )


# 删除测试标签
@auto_pytest.route("/delete_tag", methods=["POST"])
def delete_tag():
    data = request.get_json()
    tag = data.get("tag")
    case_tag = CaseTag().get_or_none(tag=tag)
    if not case_tag:
        return JsonResponse.error_response(msg="标签不存在")
    case_tag.delete_instance(permanently=True)
    return JsonResponse.success_response(msg="删除标签成功")


# 创建测试套件
@auto_pytest.route("/create_suite", methods=["POST"])
def create_suite():
    data = request.get_json()
    suite_name = data.get("suite_name")
    project = data.get("project")
    describe = data.get("describe", "无")
    case_sences = data.get("case_sences")

    if not suite_name:
        return JsonResponse.error_response(error_message="测试套件名称不能为空")
    if not project:
        return JsonResponse.error_response(error_message="测试项目id不能为空")
    # if not case_ids:
    #     return JsonResponse.error_response(error_message="测试用例不能为空")
    project = Project().get_or_none(id=project)
    if not project:
        return JsonResponse.error_response(error_message="测试项目不存在")
    if Suite().get_or_none(suite_name=suite_name):
        return JsonResponse.error_response(error_message="测试套件已经存在")
    logger.info(f"创建测试套件: {suite_name}")
    if not case_sences:
        return JsonResponse.error_response(error_message="测试场景不能为空")
    # 根据case_sences查找case集合
    cases = CaseFunc.select().where(CaseFunc.case_sence.in_(case_sences))
    # 如果为空,则抛出异常
    count = cases.count()
    if count == 0:
        return JsonResponse.error_response(error_message="测试场景不存在,请重新确认")
    suite = Suite.create(
        suite_name=suite_name,
        project=project,
        describe=describe,
    )
    # suite.case_ids = case_ids
    suite.save()
    sync_suite_sences_to_caseids(id_=suite.id, case_sences=case_sences)
    return JsonResponse.success_response(
        data={
            "suite": model_to_dict(suite, exclude=[Suite.is_deleted, Suite.case_ids])
        },
        msg="创建测试套件成功",
    )


# 获取case_sence,存放在列表中,接口重复了,这个暂废弃
@auto_pytest.route("/get_case_sences", methods=["GET"])
def get_case_sences():
    cases = CaseFunc.select(CaseFunc.case_sence).distinct()
    case_sences = []
    for case in cases:
        case_sences.append(case.case_sence)
    return JsonResponse.success_response(
        data={"case_sences": case_sences}, msg="获取测试场景成功"
    )


# 根据case_sence同步测试套件中的case_ids
@auto_pytest.route("/sync_suite_by_case_ids", methods=["POST"])
def sync_suite_by_case_ids():
    data = request.get_json()
    id_ = data.get("id")
    case_sences = data.get("case_sences")
    suite_name = data.get("suite_name")
    project = data.get("project")
    describe = data.get("describe")

    if not id_:
        return JsonResponse.error_response(error_message="测试套件id不能为空")
    if not case_sences:
        return JsonResponse.error_response(error_message="测试场景不能为空")
    suite = sync_suite_sences_to_caseids(id_=id_, case_sences=case_sences)
    if suite_name:
        suite.suite_name = suite_name
    if project:
        suite.project = project
    if describe:
        suite.describe = describe
    suite.save()

    # # 根据case_sences查找case集合
    # cases = CaseFunc.select().where(CaseFunc.case_sence.in_(case_sences))
    # # 如果为空,则抛出异常
    # count = cases.count()
    # case_ids = []
    # if count == 0:
    #     return JsonResponse.error_response(error_message="测试场景不存在")
    # for case in cases:
    #     logger.info(case.case_path)
    #     case_ids.append(case.case_path)
    # # 对case_ids进行去重
    # case_ids = list(set(case_ids))
    # # 根据suite_name查找测试套件
    # suite = Suite().get_or_none(id=id_)
    # if not suite:
    #     return JsonResponse.error_response(error_message="测试套件不存在")
    # suite.case_sences = " ".join(case_sences)
    # suite.save()
    # suite.case_ids = " ".join(case_ids)
    # logger.info(suite.case_ids)
    # suite.save()
    return JsonResponse.success_response(
        data={
            "suite": model_to_dict(suite, exclude=[Suite.is_deleted, Suite.case_ids])
        },
        msg="同步测试套件成功",
    )


def sync_suite_sences_to_caseids(id_, case_sences):
    # 根据case_sences查找case集合
    cases = CaseFunc.select().where(CaseFunc.case_sence.in_(case_sences))
    # 如果为空,则抛出异常
    count = cases.count()
    case_ids = []
    if count == 0:
        return JsonResponse.error_response(error_message="测试场景不存在")
    for case in cases:
        logger.info(case.case_path)
        case_ids.append(case.case_path)
    # 对case_ids进行去重
    case_ids = list(set(case_ids))
    # 根据suite_name查找测试套件
    suite = Suite().get_or_none(id=id_)
    if not suite:
        return JsonResponse.error_response(error_message="测试套件不存在")
    # suite.case_sences = " ".join(case_sences)
    suite.case_sences = json.dumps(case_sences)
    suite.save()
    suite.case_ids = " ".join(case_ids)
    logger.info(suite.case_ids)
    suite.save()
    return suite


# 根据指定条件查找测试套件,条件有:project_name, suite_name, test_type, test_env
@auto_pytest.route("/get_suite_list", methods=["GET"])
def get_suite_list():
    # data = request.get_json()
    id_ = request.args.get("id")
    project = request.args.get("project_id")
    suite_name = request.args.get("suite_name")
    # test_type = request.args.get("test_type")
    # test_env = request.args.get("test_env")
    suites = Suite.select()
    if id_:
        suites = suites.where(Suite.id == id_)
    if project:
        suites = suites.where(Suite.project == project)
    if suite_name:
        suites = suites.where(Suite.suite_name == suite_name)
    # if test_type:
    #     suites = suites.where(Suite.test_type == test_type)
    # if test_env:
    #     suites = suites.where(Suite.test_env == test_env)
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
        suite_list.append(
            model_to_dict(suite, exclude=[Suite.is_deleted, Suite.case_ids])
        )
    return JsonResponse.list_response(
        list_data=suite_list,
        total=total,
        current_page=start + 1,
        page_size=per_page_nums,
    )


# 跟新测试套件信息
@auto_pytest.route("/update_suite", methods=["POST"])
def update_suite():
    resp = flask_util.update_api(Suite)
    return resp
    # data = request.get_json()
    # id_ = data.get("id")
    # suite_name = data.get("suite_name")
    # project = data.get("project_id")
    # describe = data.get("describe")
    # case_ids = data.get("case_ids")
    # test_type = data.get("test_type")
    # test_env = data.get("test_env")
    # if not id_:
    #     return JsonResponse.error_response(error_message="测试套件id不能为空")
    # # if not suite_name:
    # #     return JsonResponse.error_response(error_message="测试套件名称不能为空")
    # suite = Suite().get_or_none(id=id_)
    # if not suite:
    #     return JsonResponse.error_response(error_message="测试套件不存在")
    # if project:
    #     p = Project().get_or_none(id=project)
    #     if not p:
    #         return JsonResponse.error_response(error_message="测试项目不存在")
    #     suite.project = project
    # if describe:
    #     suite.describe = describe
    # if case_ids:
    #     suite.case_ids = case_ids
    # if test_type:
    #     suite.test_type = test_type
    # if test_env:
    #     suite.test_env = test_env
    # suite.save()
    # return JsonResponse.success_response(
    #     data={"suite": model_to_dict(suite, exclude=[Suite.is_deleted])},
    #     msg="更新测试套件成功",
    # )


# 删除测试套件
@auto_pytest.route("/delete_suite", methods=["POST"])
def delete_suite():
    resp = flask_util.delete_api(Suite)
    return resp
    # data = request.get_json()
    # id_ = data.get("id")
    # suite_name = data.get("suite_name")
    # if not id_:
    #     return JsonResponse.error_response(error_message="测试套件id不能为空")
    # suite = Suite().get_or_none(id=id_)
    # if not suite:
    #     return JsonResponse.error_response(error_message="测试套件不存在")
    # suite.delete_instance(permanently=True)
    # return JsonResponse.success_response(msg="删除测试套件成功")


# 根据suite_name创建测试
@auto_pytest.route("/create_case_result", methods=["POST"])
def create_case_result():
    data = request.get_json()
    suite_id = data.get("suite_id")
    title = data.get("title")
    # suite = data.get("suite_id")
    status = data.get("status")
    result = data.get("result")
    report_link = data.get("report_link")
    report_download = data.get("report_download")
    last_report_id = data.get("last_report_id")
    test_type = data.get("test_type")
    test_env = data.get("test_env")
    if not suite_id:
        return JsonResponse.error_response(error_message="套件id不能为空")
    # if not suite:
    #     return JsonResponse.error_response(error_message="测试套件名称不能为空")
    # 如果测试套件不存在Suite表,报错
    suite = Suite().get_or_none(id=suite_id)
    if not suite:
        return JsonResponse.error_response(error_message="测试套件不存在")
    case = TestResult.create(
        title=title,
        suite=suite,
        status=status,
        result=result,
        report_link=report_link,
        report_download=report_download,
        last_report_id=last_report_id,
        test_type=test_type,
        test_env=test_env,
    )
    # 返回创建的id
    id_ = case.id
    g.id = id_
    return JsonResponse.success_response(data={"id": id_}, msg="创建测试成功")


# 根据id,suite_name,status,result,test_type,test_env获取测试
@auto_pytest.route("/get_case_result", methods=["GET"])
def get_case_result():
    resp = flask_util.list_pagenation(
        TestResult, exclude=[TestResult.is_deleted], backrefs=False, recurse=False
    )
    return resp
    # id_ = request.args.get("id")
    # cases = TestResult.select()
    # suite = request.args.get("suite_id")
    # status = request.args.get("status")
    # result = request.args.get("result")
    # test_type = request.args.get("test_type")
    # test_env = request.args.get("test_env")
    # if suite:
    #     cases = cases.where(TestResult.suite == suite)
    # if status:
    #     cases = cases.where(TestResult.status == status)
    # if result:
    #     cases = cases.where(TestResult.result == result)
    # if id_:
    #     cases = cases.where(TestResult.id == id_)
    # if test_type:
    #     cases = cases.where(TestResult.test_type == test_type)
    # if test_env:
    #     cases = cases.where(TestResult.test_env == test_env)
    # case_list = []
    # # 分页 limit offset
    # start = 0
    # per_page_nums = 10
    # if request.args.get("pageSize"):
    #     per_page_nums = int(request.args.get("pageSize"))
    # if request.args.get("current"):
    #     start = per_page_nums * (int(request.args.get("current")) - 1)
    # total = cases.count()
    # cases = cases.limit(per_page_nums).offset(start)
    # for case in cases:
    #     case_list.append(
    #         model_to_dict(
    #             case, exclude=[TestResult.is_deleted], backrefs=False, recurse=False
    #         )
    #     )
    # return JsonResponse.list_response(
    #     list_data=case_list,
    #     total=total,
    #     current_page=start + 1,
    #     page_size=per_page_nums,
    # )


# 更新测试
@auto_pytest.route("/update_case_result", methods=["POST"])
def update_case_result():
    data = request.get_json()
    id_ = data.get("id")
    suite = data.get("suite_id")
    status = data.get("status")
    result = data.get("result")
    report_link = data.get("report_link")
    report_download = data.get("report_download")
    last_report_id = data.get("last_report_id")
    test_type = data.get("test_type")
    test_env = data.get("test_env")
    if not id_:
        return JsonResponse.error_response(error_message="测试id不能为空")
    case = TestResult.get_or_none(id=id_)
    if not case:
        return JsonResponse.error_response(error_message="测试不存在")
    if suite:
        case.suite = suite
    if status:
        case.status = status
    if result:
        case.result = result
    if report_link:
        case.report_link = report_link
    if report_download:
        case.report_download = report_download
    if last_report_id:
        case.last_report_id = last_report_id
    if test_type:
        case.test_type = test_type
    if test_env:
        case.test_env = test_env
    case.save()
    return JsonResponse.success_response(msg="更新测试成功")


# 根据id删除测试
@auto_pytest.route("/delete_case_result", methods=["POST"])
def delete_case_result():
    data = request.get_json()
    id_ = data.get("id")
    if not id_:
        return JsonResponse.error_response(error_message="测试id不能为空")
    case = TestResult.get_or_none(id=id_)
    if not case:
        return JsonResponse.error_response(error_message="测试不存在")
    case.delete_instance(permanently=True)
    return JsonResponse.success_response(msg="删除测试成功")


# 执行自动化测试
@auto_pytest.route("/run_case_result", methods=["POST"])
def run_case_result():
    data = request.get_json()
    suite_id = data.get("suite_id")
    test_env = data.get("test_env")
    suite = Suite.get_or_none(id=suite_id)
    result = TestResult.get(id=g.id)
    logger.info(model_to_dict(result))
    task_id = str(uuid.uuid4())
    task = scheduler.add_job(
        func=create_run_case,
        id=f"run_case_{task_id}",
        name=f"run_case_{task_id}",
        trigger="date",
        run_date=datetime.now() + timedelta(seconds=5),
        kwargs={
            "suite": suite.id,
            "test_type": "manual",
            "test_env": test_env,
            "start_time": datetime.now().strftime("%Y-%m-%d_%H:%M:%S"),
            "task_id": task_id,
        },
    )
    return JsonResponse.success_response(
        msg="执行自动化测试成功", data={"task_id": task_id}
    )


# 根据设置的时间运行测试,不管是webhook还是手动调用还是指定时间调用,都可以通过该接口来进行,不同点在于,接口传参时test_type,test_env的不同
@auto_pytest.route("/run_case_result_by_time", methods=["POST"])
def run_case_result_by_time():
    data = request.get_json()
    id_ = data.get("id")
    run_time = data.get("run_time")
    test_env = data.get("test_env")
    test_user = data.get("test_user", "test")
    if not run_time:
        run_time = datetime.now()
    # 对时间进行转化https://docs.locust.io/en/stable/configuration.html#pick-user-classes-shapes-and-tasks-from-the-ui
    else:
        run_time = parse_datetime(date_string=run_time)
        # run_time = datetime.strptime(run_time, "%Y-%m-%d %H:%M:%S")
        # run_time = datetime.strptime(run_time, "%Y-%m-%d_%H-%M-%S")
    suite = Suite.get_or_none(id=id_)
    if not suite:
        return JsonResponse.error_response(error_message="测试套件不存在")
    if not test_env:
        return JsonResponse.error_response(error_message="测试环境不能为空")
    task_id = str(uuid.uuid4())
    task = scheduler.add_job(
        func=create_run_case,
        id=f"run_case_{task_id}",
        name=f"run_case_{task_id}",
        trigger="date",
        run_date=run_time + timedelta(seconds=5),
        kwargs={
            "suite": suite.id,
            "test_type": "manual",
            "test_env": test_env,
            "start_time": run_time.strftime("%Y-%m-%d_%H:%M:%S"),
            "task_id": task_id,
            "test_user": test_user,
        },
    )
    return JsonResponse.success_response(
        msg="执行自动化测试成功,如果设定了时间,任务未执行前可能查询不到该任务执行详情",
        data={"task_id": task_id},
    )


def parse_datetime(date_string):
    formats = ["%Y-%m-%d %H:%M:%S", "%Y-%m-%d_%H-%M-%S"]  # 格式 1  # 格式 2

    for fmt in formats:
        try:
            return datetime.strptime(date_string, fmt)
        except ValueError:
            continue  # 尝试下一个格式

    return JsonResponse.error_response(error_message="无法解析日期时间字符串")


# 创建测试计划
@auto_pytest.route("/create_case_plant", methods=["POST"])
def create_case_plant():
    resp = flask_util.create_model_instance(TestPlan)
    data = request.get_json()
    # 根据测试计划名称，查询创建成功的ID
    return resp
    # data = request.get_json()
    # plan_name = data.get("plan_name")
    # suite_id = data.get("suite_id")
    # cron = data.get("cron")
    # test_env = data.get("test_env")
    # is_open = data.get("is_open", "off")
    # logger.info(f"plan_name:{plan_name},{suite_id},{cron},{test_env},{is_open}")
    # if not plan_name:
    #     return JsonResponse.error_response(error_message="测试计划名称不能为空")
    # if not suite_id:
    #     return JsonResponse.error_response(error_message="测试套件id名称不能为空")
    # suite = Suite().get_or_none(id=suite_id)
    # if not suite:
    #     return JsonResponse.error_response(error_message="测试套件不存在")
    # if not cron:
    #     return JsonResponse.error_response(error_message="定时任务不能为空")
    # if not test_env:
    #     return JsonResponse.error_response(error_message="测试环境不能为空")
    # if not Suite.get_or_none(id=suite_id):
    #     return JsonResponse.error_response(error_message="测试套件不存在")
    # plan_ = TestPlan.get_or_none(plan_name=plan_name)
    # if plan_:
    #     return JsonResponse.error_response(error_message="测试计划名称已存在")
    # # suite = Suite.get_or_none(suite_name=suite_name)
    # # if not suite:
    # #     return JsonResponse.error_response(error_message="测试套件不存在")
    # if test_env not in ["dev", "test", "prod", "online", "boe"]:
    #     return JsonResponse.error_response(
    #         data="测试环境不正确,not in [dev,test,prod,online,boe]"
    #     )
    # paln = TestPlan.create(
    #     plan_name=plan_name,
    #     suite=suite,
    #     test_env=test_env,
    #     cron=cron,
    #     is_open=is_open,
    # )
    # return JsonResponse.success_response(
    #     data=model_to_dict(paln, exclude=[TestPlan.is_deleted], recurse=False),
    #     msg="创建测试计划成功",
    # )


# 删除测试计划
@auto_pytest.route("/del_case_plant", methods=["POST"])
def del_case_plant():
    # data = request.get_json()
    # id_ = data.get("id")
    # if not id_:
    #     return JsonResponse.error_response(error_message="测试计划id不能为空")
    # # plan_name = data.get("plan_name")
    # # if not plan_name:
    # #     return JsonResponse.error_response(error_message="测试计划名称不能为空")
    # plan_name = TestPlan.get_or_none(id=id_)
    # if not plan_name:
    #     return JsonResponse.error_response(error_message="测试计划不存在")
    # plan_name.delete_instance(permanently=True)
    # return JsonResponse.success_response(msg="删除测试计划成功")
    resp = flask_util.delete_api(TestPlan)
    return resp


# 修改测试计划
@auto_pytest.route("/update_case_plant", methods=["POST"])
def update_case_plant():
    resp = flask_util.update_api(
        TestPlan,
    )
    return resp
    # data = request.get_json()
    # id_ = data.get("id")
    # suite = data.get("suite_id")
    # cron = data.get("cron")
    # test_env = data.get("test_env")
    # if not id_:
    #     return JsonResponse.error_response(error_message="测试计划id不能为空")
    # # if not plan_name:
    # #     return JsonResponse.error_response(error_message="测试计划名称不能为空")
    # plan = TestPlan.get_or_none(id=id_)
    # if not plan:
    #     return JsonResponse.error_response(error_message="测试计划不存在")
    # # plan = TestPlan.get(plan_name=plan_name)
    # if suite:
    #     suite = Suite.get_or_none(id=suite)
    #     if not suite:
    #         return JsonResponse.error_response(error_message="测试套件不存在")
    #     plan.suite = suite
    #     plan.save()
    # if test_env:
    #     if test_env not in ["dev", "test", "prod", "online", "boe"]:
    #         return JsonResponse.error_response(error_message="测试环境不正确")
    #     plan.test_env = test_env
    #     plan.save()
    # if cron:
    #     plan.cron = cron
    #     plan.save()
    # return JsonResponse.success_response(msg="修改测试计划成功")


# 根据条件查询测试计划列表
@auto_pytest.route("/list_case_plant", methods=["GET"])
def list_case_plant():
    logger.info(TestPlan)
    resp = flask_util.list_pagenation(
        moudle=TestPlan,
        # data=request.args,
        # keys_to_extract=["id", "plan_name", "suite_id", "test_env"],
        exclude=[TestPlan.is_deleted],
        recurse=False,
    )
    return resp
    # plans = TestPlan.select()
    # if request.args.get("id"):
    #     plans = plans.where(TestPlan.id == request.args.get("id"))
    # if request.args.get("plan_name"):
    #     plans = plans.where(TestPlan.plan_name == request.args.get("plan_name"))
    # if request.args.get("suite_id"):
    #     plans = plans.where(TestPlan.suite == request.args.get("suite_id"))
    # if request.args.get("test_env"):
    #     plans = plans.where(TestPlan.test_env == request.args.get("test_env"))
    # # 分页 limit offset
    # start = 0
    # per_page_nums = 10
    # plan_list = []
    # if request.args.get("pageSize"):
    #     per_page_nums = int(request.args.get("pageSize"))
    # if request.args.get("current"):
    #     start = per_page_nums * (int(request.args.get("current")) - 1)
    # total = plans.count()
    # plans = plans.limit(per_page_nums).offset(start)
    # logger.info(plans.count())
    # for plan in plans:
    #     logger.info(plan)
    #     plan_list.append(
    #         model_to_dict(plan, exclude=[TestPlan.is_deleted], recurse=False)
    #     )
    # logger.info(plan_list)
    # return JsonResponse.list_response(
    #     list_data=plan_list,
    #     total=total,
    #     current_page=start + 1,
    #     page_size=per_page_nums,
    # )


# 动态设置定时任务,开启还是关闭,该方法暂时废弃,实现起来需要自己额外开发很多功能
@auto_pytest.route("/set_case_result_by_celery", methods=["POST"])
def set_case_result_by_celery():
    from plant_srv.utils.celery_util.make_celery import celery_app

    data = request.get_json()
    plan_name = data.get("plan_name")
    is_open = data.get("is_open")
    cron = data.get("cron")
    if not plan_name:
        return JsonResponse.error_response(error_message="测试计划名称不能为空")
    plan = TestPlan.get_or_none(plan_name=plan_name)
    if not plan:
        return JsonResponse.error_response(error_message="测试计划不存在")
    if not is_open:
        return JsonResponse.error_response(error_message="开启或关闭不能为空")
    if is_open not in ["on", "off"]:
        return JsonResponse.error_response(error_message="开启或关闭参数不正确")
    plan = TestPlan.get(plan_name=plan_name)
    if not cron:
        cron = plan.cron
    if plan.is_open == is_open:
        return JsonResponse.error_response(error_message="当前状态和设置状态一致")
    if is_open == "on":
        # 开启定时任务配置
        plan.is_open = is_open
        plan.save()
        # 开启定时任务
        celery_app.conf.beat_schedule["test_case_result"] = {
            "task": "plant_srv.utils.celery_util.task.task_demo.add_together",  # 任务名称
            "schedule": timedelta(seconds=30),  # 定时任务时间
            "args": (5, 6),  # 传递参数
        }

        # @celery_app.on_after_configure.connect
        # def setup_periodic_tasks(sender, **kwargs):
        #     # Calls test('hello') every 10 seconds.
        #     sender.add_periodic_task(10.0, test.s('hello'), name='add every 10')
        celery_app.add_periodic_task(
            schedule=timedelta(seconds=30),
            sig=add_together.s(10, 11),
            name="add every 10",
        )
        # celery_app.send_task("plant_srv.tasks.auto_pytest_task", args=[plan_name])
    else:
        # 关闭定时任务配置
        plan.is_open = is_open
        plan.save()
        # 关闭定时任务
        del celery_app.conf.beat_schedule["test_case_result"]
    # 读取celery中定时任务配置
    logger.info(celery_app.conf.beat_schedule)

    return JsonResponse.success_response(data="设置成功")


@auto_pytest.route("/job_test", methods=["POST"])
def job_test():
    job = scheduler.add_job(
        func=task2,
        # trigger="cron",
        # seconds=30,
        id="test2",
        name="test2",
        replace_existing=True,
        kwargs={"a": 1, "b": 2},
        trigger=CronTrigger.from_crontab("30 * * * *"),
    )
    logger.info(job)
    return JsonResponse.success_response(data="定时任务开启成功")


# 动态设置定时任务,开启\关闭\更新
@auto_pytest.route("/set_case_result_by_cron", methods=["POST"])
def set_case_result_by_cron():
    """
        https://apscheduler.readthedocs.io/en/3.x/py-modindex.html
        下面是支持cron的实现方式
    :param request:
    :return:
    trigger：指定触发器类型，可以是 interval（间隔触发）或 cron（定时触发）。
    corn：指定定时任务的 cron 表达式。
        详细参考:https://en.wikipedia.org/wiki/Cron
        minute：指定在每小时的哪一分钟触发，范围是 0-59 或 *（每分钟）。
        hour：指定在每天的哪个小时触发，范围是 0-23 或 *（每小时）。
        day：指定在每个月的哪一天触发，范围是 1-31 或 *（每天）。
        month：指定在每年的哪个月份触发，范围是 1-12 或 *（每月）。
        day_of_week：指定在每周的哪几天触发，可以使用 0-6（0 代表周日），或使用缩写如 mon、tue 等。例如，mon-fri 表示从周一到周五。
    interval：指定间隔触发的时间间隔，可以是 seconds（秒）、minutes（分钟）、hours（小时）、days（天）、weeks（周）或 months（月）。
        Parameters:
        weeks (int) – number of weeks to wait
        days (int) – number of days to wait
        hours (int) – number of hours to wait
        minutes (int) – number of minutes to wait
        seconds (int) – number of seconds to wait
        start_date (datetime|str) – starting point for the interval calculation
        end_date (datetime|str) – latest possible date/time to trigger on
    date：指定在某个具体的日期和时间触发。
        run_date：指定在某个具体的日期和时间触发。
    """
    data = request.get_json()
    id_ = data.get("id")
    plan_name = data.get("plan_name")
    is_open = data.get("is_open")
    # trigger = data.get("trigger", "cron")
    cron = data.get("cron")
    minute = data.get("minute", "*")
    hour = data.get("hour", "*")
    day = data.get("day", "*")
    month = data.get("month", "*")
    day_of_week = data.get("day_of_week", "0-6")
    run_once = data.get("run_once", False)
    update_corn = data.get("update_corn", False)
    test_user = data.get("test_user", "test")
    if not id_:
        return JsonResponse.error_response(error_message="id不能为空")
    # if not plan_name:
    #     return JsonResponse.error_response(error_message="测试计划名称不能为空")
    plan = TestPlan.get_or_none(id=id_)
    if not plan:
        return JsonResponse.error_response(error_message="测试计划不存在")
    if not is_open:
        return JsonResponse.error_response(error_message="开启或关闭不能为空")
    if is_open not in ["on", "off"]:
        return JsonResponse.error_response(error_message="开启或关闭参数不正确")
    plan = TestPlan.get(id=id_)
    # if not cron:
    #     cron = plan.cron
    # if plan.is_open == is_open:
    #     return JsonResponse.error_response(error_message="当前状态和设置状态一致")
    # 如果不存在taskid,随机生成一个task_id,写入到数据库中
    if not plan.plan_id:
        plan_id = str(uuid.uuid4())
        plan.plan_id = plan_id
        plan.save()
    if update_corn:
        # 更新定时任务配置
        plan.is_open = is_open
        if not cron:
            plan.cron = f"{minute} {hour} {day} {month} {day_of_week}"
        else:
            plan.cron = cron
        plan.save()
        # 更新定时任务
        scheduler.reschedule_job(
            id=plan.plan_id,
            trigger=CronTrigger.from_crontab(f"{plan.cron}"),
        )
        if run_once:
            scheduler.run_job(id=plan.plan_id)
        return JsonResponse.success_response(data="定时任务更新成功", msg=plan.plan_id)
    if is_open == "on":
        # 开启定时任务配置
        plan.is_open = is_open
        if not cron:
            plan.cron = f"{minute} {hour} {day} {month} {day_of_week}"
        else:
            plan.cron = cron
        plan.save()
        # # 开启定时任务,及是否直接触发一次
        task = scheduler.add_job(
            func=create_run_case,
            id=plan.plan_id,
            name=plan_name,
            replace_existing=True,
            trigger=CronTrigger.from_crontab(
                f"{minute} {hour} {day} {month} {day_of_week}"
            ),
            kwargs={
                "suite": plan.suite.id,
                "test_type": "cron",
                "test_env": plan.test_env,
                # "start_time": datetime.now().strftime("%Y-%m-%d_%H:%M:%S"),
                "plan_id": plan.id,
                "test_user": test_user,
            },
        )
        if run_once:
            scheduler.run_job(id=plan.plan_id)
        logger.info(task)
        return JsonResponse.success_response(data="定时任务开启成功", msg=plan.plan_id)
    # elif update_corn:
    #     # 更新定时任务配置
    #     plan.is_open = is_open
    #     plan.cron = f"{minute} {hour} {day} {month} {day_of_week}"
    #     plan.save()
    #     # 更新定时任务
    #     scheduler.reschedule_job(
    #         id=plan.plan_id,
    #         trigger=CronTrigger.from_crontab(
    #             f"{minute} {hour} {day} {month} {day_of_week}"
    #         ),
    #     )
    else:
        # 关闭定时任务配置
        plan.is_open = is_open
        plan.save()
        # 关闭定时任务
        try:
            scheduler.remove_job(id=plan.plan_id)
        except Exception as e:
            logger.error(e)
            pass
        return JsonResponse.success_response(
            data="设置成功,定时任务已关闭", msg=plan.plan_id
        )


# webhook触发执行测试
@auto_pytest.route("/webhook", methods=["POST", "GET"])
def webhook():
    # 获取请求中的数据
    key = request.args.get("key")
    data = request.get_json()
    logger.info(data)
    plan = TestPlan.get(plan_name=settings.test.webhook_plan)
    if key != settings.test.webhook_key:
        return JsonResponse.response(data={"msg": "key不正确"}, code=401)
    else:
        task_id = str(uuid.uuid4())
        task = scheduler.add_job(
            func=create_run_case,
            kwargs={
                "suite": plan.suite.id,
                "test_type": "webhook",
                "test_env": plan.test_env,
                "start_time": datetime.now().strftime("%Y-%m-%d_%H:%M:%S"),
                "task_id": task_id,
                "test_user": "webhook",
            },
            id=str(uuid.uuid4()),
            replace_existing=True,
        )
        return JsonResponse.response(
            data={"msg": "webhook任务开启成功", "task_id": task_id}, code=200
        )


# 需要封装执行自动化测试及把结果写入到case中的一个方法,或者,通过pytest框架的main.py来完成
def create_run_case(
    suite,
    test_type,
    test_env,
    start_time=None,
    task_id: str = None,
    plan_id=None,
    test_user=None,
):
    if not start_time:
        start_time = datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    # 创建一个测试计划等待执行
    suite = Suite().get_or_none(id=suite)
    if not suite:
        return JsonResponse.error_response(error_message="测试套件不存在")
    suite_name = suite.suite_name
    project_name = suite.project.project_name
    title = f"{project_name}-{suite_name}-{test_type}-{test_env}-{start_time}"
    logger.info(title)
    # 创建一个测试计划等待执行
    suite = Suite().get_or_none(id=suite)
    if not suite:
        return JsonResponse.error_response(error_message="测试套件不存在")
    suite_name = suite.suite_name
    project_name = suite.project.project_name
    title = f"{project_name}-{suite_name}-{test_type}-{test_env}-{start_time}"
    logger.info(title)
    case = TestResult.create(
        title=title,
        suite=suite,
        test_type=test_type,
        test_env=test_env,
        test_user=test_user,
    )
    # 返回创建的id
    if not task_id:
        task_id = str(uuid.uuid4())
    case.task_id = task_id
    case.save()
    if plan_id:
        case.plan_id = plan_id
        case.save()
    id_ = case.id
    case_ids = suite.case_ids
    # 需要suite(project_name,suite_name,) test_type test_env start_time
    comand = f"export ENV_FOR_DYNACONF={test_env} && {settings.test.python_env} main.py --cases '{case_ids}'  --allure_dir {settings.test.report_dir}/{project_name}/{suite_name}-{test_type}-{test_env}-{start_time} --result_id {id_}"
    logger.info(comand)
    resp = Popen(comand, shell=True, cwd=settings.test.base_dir)
    # 在测试中,补全status,result,report_link,report_download
    return {
        "id": id_,
        "title": title,
        "suite_name": suite_name,
        "test_type": test_type,
        "test_env": test_env,
        "start_time": start_time,
        "status": "running",
        "result": "running",
        "report_link": "",
        "report_download": "",
    }
