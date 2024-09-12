from peewee import *
from plant_srv.model.modelsbase import BaseModel
from plant_srv.utils.log_moudle import logger

class User(BaseModel):
    name = CharField(unique=True)
    password = CharField()
    # 权限，0为普通用户，1为管理员
    permission = IntegerField(default=0)

if __name__ == '__main__':
    # User.create_table()
    # u = User(name='admin', password='123456', permission=1)
    # u.save()
    # u = User(name='user', password='123456', permission=0)
    # u.save()
    users = User.select().dicts()
    logger.info(list(users))