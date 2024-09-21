'''
参阅文档:
    flask官方文档:
        https://flask.palletsprojects.com/en/3.0.x/patterns/celery/
    一个博客:
        https://blog.csdn.net/weixin_46371752/article/details/133790591

执行命令:
    python3 manage.py
    celery -A plant_srv.utils.celery_util.make_celery worker --loglevel=INFO

'''


from celery import Celery, Task
from flask import Flask
from plant_srv.utils.celery_util.celery_config import celery_config
from plant_srv.utils.log_moudle import logger

def celery_init_app(app: Flask) -> Celery:
    class FlaskTask(Task):
        def __call__(self, *args: object, **kwargs: object) -> object:
            with app.app_context():
                return self.run(*args, **kwargs)

    celery_app = Celery(app.name, task_cls=FlaskTask)
    # logger.info(f"{app.config['CELERY']}")
    app.config.from_mapping(CELERY=celery_config)
    celery_app.config_from_object(app.config["CELERY"])
    celery_app.set_default()
    app.extensions["celery"] = celery_app
    return celery_app