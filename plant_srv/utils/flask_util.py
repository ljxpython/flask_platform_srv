"""

flask中常用的工具添加

"""

from sqlalchemy import False_

from plant_srv.model.modelsbase import BaseModel, database
from playhouse.shortcuts import model_to_dict
from plant_srv.utils.json_response import JsonResponse
from plant_srv.utils.log_moudle import logger
from peewee import *
from playhouse.shortcuts import model_to_dict


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



class FlaskUtil():

    def extracted_data(self,data:dict,keys_to_extract:list):
        return {key: data[key] for key in keys_to_extract if key in data}


    def data_filter(self,moudle:BaseModel,filter:dict|None):
        m = moudle.select()
        if not filter:
            return m
        for key,value in filter.items():
            m = m.where(getattr(moudle,key) == value)
        return m

    def list_pagenation(self,moudle:BaseModel,exclude:list,recurse:bool=True,**kwargs):
        # filter = self.extracted_data(data=data,keys_to_extract=keys_to_extract)
        # m = self.data_filter(moudle,filter=filter)
        data = request.args
        query = moudle.select()  # 创建基础查询
        # 根据传入的过滤条件动态添加查询
        for key, value in data.items():
            if hasattr(moudle, key):  # 检查字段是否存在
                query = query.where(getattr(moudle, key) == value)


        # 分页 limit offset
        start = 0
        per_page_nums = 10
        if data.get('pageSize'):
            per_page_nums = int(data.get('pageSize'))
        if data.get('current'):
            start = per_page_nums * (int(data.get('current')) - 1)
        total = query.count()
        cases = query.limit(per_page_nums).offset(start)
        logger.info(cases.count())
        case_list = []
        # logger.info(cases.dicts())
        for case in cases:
            # logger.info(case)
            # logger.info(model_to_dict(case))
            case_list.append(
                model_to_dict(
                    case,
                    exclude=exclude,
                    recurse=recurse, **kwargs
                )
            )
        return JsonResponse.list_response(
            list_data=case_list,
            current_page=start + 1,
            total=total,
            page_size=per_page_nums,
        )


    # 删除接口封装
    def delete_api(self,moudle:BaseModel):
        data = request.get_json()
        id_ = data.get("id")
        if not id_:
            return JsonResponse.error_response(data=f"{moudle} id不能为空")
        m = moudle.get_or_none(id=id_)
        if not m:
            return JsonResponse.error_response(data=f"{moudle} id:{id_}不存在")
        m.delete_instance(permanently=True)
        return JsonResponse.success_response(msg=f"删除{moudle} id:{id_}成功")

    # 更新属性接口封装
    def update_api(self,moudle:BaseModel):
        data = request.get_json()
        id_ = data.get("id")
        if not id_:
            return JsonResponse.error_response(data=f"{moudle} id不能为空")
        m = moudle.get_or_none(id=id_)
        if not m:
            return JsonResponse.error_response(data=f"{moudle} id:{id_}不存在")
        del data["id"]
        try:
            self.update_model(instance=m,updates=data)
        except Exception as e:
            return JsonResponse.error_response(data={
                "msg":f"更新{moudle} id:{id_}失败",
                "error":str(e)
            })
        return JsonResponse.success_response(msg=f"更新{moudle} id:{id_}成功")

    def update_model(self,instance:BaseModel, updates:dict):
        for key, value in updates.items():
            if hasattr(instance, key):
                setattr(instance, key, value)
        instance.save()

    # 根据传入的字典创建模型实例的函数
    def create_model_instance(self,model:BaseModel,):
        data = request.get_json()
        # 获取模型的字段
        fields = model._meta.fields
        # 筛选出存在的字段
        filtered_data = {key: value for key, value in data.items() if key in fields}

        # 创建模型实例
        try:
            instance = model.create(**filtered_data)
        except Exception as e:
            return JsonResponse.error_response(data={
                "msg": f"创建{model} 失败",
                "error": str(e)
            })

        return JsonResponse.success_response(data=model_to_dict(instance,exclude=[model.is_deleted],recurse=False),msg=f"创建{model} 成功")



flask_util = FlaskUtil()