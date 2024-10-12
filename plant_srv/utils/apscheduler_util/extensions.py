"""
    Initialize any app extensions.
    参考文档: https://viniciuschiele.github.io/flask-apscheduler/rst/examples.html
    官方代码: https://github.com/viniciuschiele/flask-apscheduler/blob/master/examples/application_factory/__init__.py
    他人时间比较好的代码: https://sinhub.cn/2018/11/apscheduler-user-guide/
    """

from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore
from flask_apscheduler import APScheduler

scheduler = APScheduler()

# ... any other stuff.. db, caching, sessions, etc.

# 添加数据库存储,这部分配置放到了conf/constants.py中
# jobstores = {
#     'default': SQLAlchemyJobStore(url='sqlite:///jobs.sqlite')
# }
