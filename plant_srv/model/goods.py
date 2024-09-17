from peewee import *

from plant_srv.model.modelsbase import BaseModel
from plant_srv.utils.log_moudle import logger


class Goods(BaseModel):
    goodid = AutoField(primary_key=True)
    name = CharField()
    description = TextField(null=True)
    type = CharField()
    subtype = CharField()
    price = IntegerField(verbose_name="商品价格")
    # 商品图片,是一个url
    image = CharField(null=True)
    status = CharField(default=0, verbose_name="0:审核中;1:上架中;2:下架")


if __name__ == "__main__":
    Goods.create_table()
    # Goods.drop_table()
