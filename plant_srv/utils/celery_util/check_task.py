from celery.result import AsyncResult

from plant_srv.utils.log_moudle import logger


def task_result(id: str) -> dict[str, object]:
    result = AsyncResult(id)
    dic = {
        "task_id": id,
        'type': result.status,
        'msg': '',
        'data': str(result.result) if result.ready() else None,
        # 'code': result.,
        "ready": result.ready(),
        "successful": result.successful(),
        # "value": result.result if result.ready() else None,
    }
    logger.info(result)
    if result.status == 'PENDING':
        dic['msg'] = '任务等待中'
    elif result.status == 'STARTED':
        dic['msg'] = '任务开始执行'
    elif result.status == 'RETRY':
        dic['msg'] = '任务重新尝试执行'
    elif result.status == 'FAILURE':
        dic['msg'] = '任务执行失败了'
    elif result.status == 'SUCCESS':
        result = result.get()
        dic['msg'] = '任务执行成功'
        dic['data'] = result
        dic['code'] = 200
        # result.forget() # 将结果删除
        # async.revoke(terminate=True)  # 无论现在是什么时候，都要终止
        # async.revoke(terminate=False) # 如果任务还没有开始执行呢，那么就可以终止。
    return dic