import asyncio
from utils.tenxun_cos import create_bucket

async def async_create_bucket(bucket):
    print("执行协程-创建桶。")
    await create_bucket(bucket)
    print("创建桶-协程执行完成。")



