# -*- coding=utf-8
from qcloud_cos import CosConfig
from qcloud_cos import CosS3Client

from SAAS import settings
from SAAS.settings import COS_UID, SecretId, SecretKey, REGION
import sys
import logging
from sts.sts import Sts
import json

# 正常情况日志级别使用 INFO，需要定位时可以修改为 DEBUG，此时 SDK 会打印和服务端的通信信息
logging.basicConfig(level=logging.INFO, stream=sys.stdout)

# 1. 设置用户属性, 包括 secret_id, secret_key, region等。Appid 已在 CosConfig 中移除，请在参数 Bucket 中带上 Appid。Bucket 由 BucketName-Appid 组成
# 用户的 SecretId，建议使用子账号密钥，授权遵循最小权限指引，降低使用风险。子账号密钥获取可参见 https://cloud.tencent.com/document/product/598/37140
secret_id = SecretId
# 用户的 SecretKey，建议使用子账号密钥，授权遵循最小权限指引，降低使用风险。子账号密钥获取可参见 https://cloud.tencent.com/document/product/598/37140
secret_key = SecretKey
# 替换为用户的 region，已创建桶归属的 region 可以在控制台查看，https://console.cloud.tencent.com/cos5/bucket
region = REGION
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
    print("创建桶-请求开始！")
    bucket = f'{username}-{COS_UID}'
    try:
        # 创建桶
        res = client.create_bucket(
            Bucket= bucket,
            ACL="public-read",  # private / public-read / public-read-write
        )
        # 添加 cors策略
        client.put_bucket_cors(
            Bucket= bucket,
            CORSConfiguration={
                'CORSRule': [
                    {
                        'AllowedOrigin': [
                            '*',
                        ],
                        'AllowedMethod': [
                            'GET', 'PUT', 'HEAD',
                            'DELETE', 'POST',
                        ],
                        'AllowedHeader': [
                            '*',
                        ],
                        'ExposeHeader': [
                            '*',
                        ],
                        'MaxAgeSeconds': 500,
                    }
                ]
            }
        )
    except:
        print("创建桶-请求结束-异常！")
        return "创建桶-请求结束-异常！"
    print("创建桶-请求结束！",res)
    return "创建桶-请求结束！"

def upload_file(bucket_name, path, file):
    """ 上传文件 """
    Bucket = f'{bucket_name}-{COS_UID}'
    key = path
    """ 创建文件 """
    response = client.upload_file_from_buffer(
        Bucket= Bucket,
        Body= file,
        Key= key,
        PartSize=10,
        MAXThread=10,
        EnableMD5=False
    )
    # print(response['ETag'])
    return f"https://{Bucket}.cos.{region}.myqcloud.com{key}"

# 删除单个文件
def delete_file(bucket_name, path, file):
    """ 删除单个文件 """
    Bucket = f'{bucket_name}-{COS_UID}'
    key = path+file
    print("key",key)
    """ 创建文件 """
    response = client.delete_object(
        Bucket=Bucket,
        Key=key,
    )
    print(response)
    return f"https://{Bucket}.cos.{region}.myqcloud.com{key}"

def delete_file_list(bucket_name, list):
    # 批量删除文件
    Bucket = f'{bucket_name}-{COS_UID}'
    # for i in list:
    #     print(i)
    re = client.delete_objects(
        Bucket=Bucket,
        Delete={
             "Object": list,
            # [
            #     {
            #         "Key": "齐奥斯威/齐奥斯威/顺丰速递/test/3.gif"
            #     },
            # ],
            "Quiet": "true",
        }
    )
    print("Re",re)

# def upload_ssfile(bucket_name, path, file):
#     Bucket = f'{bucket_name}-{COS_UID}'
#     key = path
#     """ 创建文件 """
#     response = client.upload_file(
#         Bucket= Bucket,
#         Key=key,
#         LocalFilePath=file,
#         PartSize=10,
#         MAXThread=10,
#     )
#     # print(response['ETag'])
#     return f"https://{Bucket}.cos.{region}.myqcloud.com{key}"

def get_credential(example, ):
    """ 获取 COS 密钥 """
    config = {
        # 请求URL，域名部分必须和domain保持一致
        # 使用外网域名时：https://sts.tencentcloudapi.com/
        # 使用内网域名时：https://sts.internal.tencentcloudapi.com/
        'url': 'https://sts.tencentcloudapi.com/',
        # 域名，非必须，默认为 sts.tencentcloudapi.com
        # 内网域名：sts.internal.tencentcloudapi.com
        'domain': 'sts.tencentcloudapi.com',
        # 临时密钥有效时长，单位是秒
        'duration_seconds': 1800,
        'secret_id': settings.SecretId,
        # 固定密钥
        'secret_key': settings.SecretKey,
        # 设置网络代理
        # 'proxy': {
        #     'http': 'xx',
        #     'https': 'xx'
        # },
        # 换成你的 bucket
        'bucket': f'{example}-{settings.COS_UID}',
        # 换成 bucket 所在地区
        'region': settings.REGION,
        # 这里改成允许的路径前缀，可以根据自己网站的用户登录态判断允许上传的具体路径
        # 例子： a.jpg 或者 a/* 或者 * (使用通配符*存在重大安全风险, 请谨慎评估使用)
        'allow_prefix': '*',
        # 密钥的权限列表。简单上传和分片需要以下的权限，其他权限列表请看 https://cloud.tencent.com/document/product/436/31923
        'allow_actions': [
            # 简单上传
            'name/cos:PutObject',
            'name/cos:GetObject'
            # 'name/cos:PostObject',
            # # 分片上传
            # 'name/cos:InitiateMultipartUpload',
            # 'name/cos:ListMultipartUploads',
            # 'name/cos:ListParts',
            # 'name/cos:UploadPart',
            # 'name/cos:CompleteMultipartUpload'
        ],
        # 临时密钥生效条件，关于condition的详细设置规则和COS支持的condition类型可以参考 https://cloud.tencent.com/document/product/436/71306

    }
    try:
        sts = Sts(config)
        response = sts.get_credential()
        print('get data : ' + json.dumps(dict(response), indent=4))
        return response
    except Exception as e:
        print(e)


def check_file(bucket_name, key):
    Bucket = f'{bucket_name}-{COS_UID}'
    data = client.head_object(
        Bucket = Bucket,
        Key = key
    )
    return data



if __name__ == '__main__':
    # create_bucket("a")
    name = "ztgkrthwb5oj"
    file = ""
    path = "齐奥斯威/齐奥斯威/顺丰速递/"
    list = [
        {
            "Key": "迷你版/现在才222/"
        },
    ]
    # upload_ssfile(name, path, file)
    # delete_file(name,path,file)
    delete_file_list(name, list)

