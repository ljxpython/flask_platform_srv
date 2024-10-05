'''




参数解析：
accept_content：允许的内容类型/序列化程序的白名单，如果收到不在此列表中的消息，则该消息将被丢弃并出现错误，默认只为json；
task_serializer：标识要使用的默认序列化方法的字符串，默认值为json；
result_serializer：结果序列化格式，默认值为json；
timezone：配置Celery以使用自定义时区；
enable_utc：启用消息中的日期和时间，将转换为使用 UTC 时区，与timezone连用，当设置为 false 时，将使用系统本地时区。
result_expires： 异步任务结果存活时长
beat_schedule：设置定时任务
'''

from datetime import timedelta
from conf.config import settings


# 手动注册celery的异步任务：将所有celery异步任务所在的模块找到，写成字符串
# 所有任务均放在plant_srv/utils/celery_util/task/下面
task_module = [
    'plant_srv.utils.celery_util.task.async_task',  # 写任务模块导入路径，该模块主要写异步任务的方法
    'plant_srv.utils.celery_util.task.scheduler_task',  # 写任务模块导入路径，该模块主要写定时任务的方法
]


# celery 配置文件
celery_config = {
    "broker_url":  f"redis://:{settings.redis.password}@{settings.redis.host}:{settings.redis.port}/2",
    "result_backend": f"redis://:{settings.redis.password}@{settings.redis.host}:{settings.redis.port}/3",
    "task_ignore_result" : False,
    "result_expires" : 1*60*60,
    "task_serializer": 'json',
    "result_serializer": 'json',
    "accept_content": ['json'],
    "timezone": 'Asia/Shanghai',
    "enable_utc": False,
    "beat_schedule":{
        # "test":{
        #
        #     "task": 'plant_srv.utils.celery_util.task.task_demo.add_together',  # 任务名称
        #     "schedule": timedelta(seconds=30),  # 定时任务时间
        #     "args": (5, 6),  # 传递参数
        # }
    },
    "broker_connection_retry": True,
}