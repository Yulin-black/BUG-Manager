import threading
from asgiref.sync import sync_to_async
from utils.tenxun_cos import create_bucket
# 导入 线程池 库
from concurrent.futures import ThreadPoolExecutor

# 创建 线程池，维护了 3 个线程
pool = ThreadPoolExecutor(3)
lock_object = threading.RLock()


def application_thread(bucket):
    with lock_object:
        pool.submit(create_bucket(bucket))

async def application_coroutines(bucket):
    # await create_bucket(bucket)
    # await create_bucket(bucket)
    await sync_to_async(create_bucket)(bucket)
