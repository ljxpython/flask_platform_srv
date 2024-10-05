"""
    Initialize any app extensions.
    参考文档: https://viniciuschiele.github.io/flask-apscheduler/rst/examples.html
    官方代码: https://github.com/viniciuschiele/flask-apscheduler/blob/master/examples/application_factory/__init__.py
    """

from flask_apscheduler import APScheduler

scheduler = APScheduler()

# ... any other stuff.. db, caching, sessions, etc.