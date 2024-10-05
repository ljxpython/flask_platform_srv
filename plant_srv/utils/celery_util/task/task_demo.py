from celery import shared_task
import time

from nodeenv import logger


@shared_task(ignore_result=False)
def add_together(a: int, b: int) -> dict:
    time.sleep(1)
    logger.info(f"add_together task start, a: {a}, b: {b}")
    # 这一步缺任务完成后,把回调内容update到数据库的操作,暂时先不写入
    return {"result": a + b, "status": "success"}