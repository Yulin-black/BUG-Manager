# -*- coding=utf-8
import time

from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client
import sys
import os
import logging

# 正常情况日志级别使用 INFO，需要定位时可以修改为 DEBUG，此时 SDK 会打印和服务端的通信信息
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

# 1. 设置用户属性, 包括 secret_id, secret_key, region等。Appid 已在 CosConfig 中移除，请在参数 Bucket 中带上 Appid。Bucket 由 BucketName-Appid 组成
# 用户的 SecretId，建议使用子账号密钥，授权遵循最小权限指引，降低使用风险。子账号密钥获取可参见 https://cloud.tencent.com/document/product/598/37140
secret_id = "AKIDst3B7oHWYMdheNs9dw1vd8ZxBF9ueKx3"
# 用户的 SecretKey，建议使用子账号密钥，授权遵循最小权限指引，降低使用风险。子账号密钥获取可参见 https://cloud.tencent.com/document/product/598/37140
secret_key = "5FIApGagYCbmjR0LSKsBF5h5HFNL6dwu"
# 替换为用户的 region，已创建桶归属的 region 可以在控制台查看，https://console.cloud.tencent.com/cos5/bucket
region = 'ap-chengdu'
# COS 支持的所有 region 列表参见 https://cloud.tencent.com/document/product/436/6224
# 如果使用永久密钥不需要填入 token，如果使用临时密钥需要填入，临时密钥生成和使用指引参见 https://cloud.tencent.com/document/product/436/14048
token = None
# 指定使用 http/https 协议来访问 COS，默认为 https，可不填
scheme = 'https'

config = CosConfig(
    Region=region,
    SecretId=secret_id,
    SecretKey=secret_key,
    Token=token,
    Scheme=scheme
)
client = CosS3Client(config)


def create_bucket(username):
    # print("模拟网络请求开始！")
    # time.sleep(6)
    # print("模拟网络请求结束！")

    # 创建桶
    print("创建桶-请求开始！")
    response = client.create_bucket(
        Bucket=f'{username}-1317168927',
        ACL="public-read",  # private / public-read / public-read-write
    )
    print("创建桶-请求结束！")

def upload_file():
    " 创建文件 "
    response = client.upload_file(
        Bucket='test-1317168927',
        LocalFilePath='ttf.ttf',
        Key='test1/test2/test3/ttf.ttf',
        PartSize=1,
        MAXThread=10,
        EnableMD5=False
    )
    print(response['ETag'])


if __name__ == '__main__':
    create_bucket("a")