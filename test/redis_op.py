import redis

redis_store = redis.Redis(host='127.0.0.1', port=6379,password='',db=1)  # 操作的redis配置
# redis_store.set('name', 'runoob')  # 设置 name 对应的值
print(redis_store.get('hello'))  # 取出键 name 对应的值