import datetime
import json
# 签名 SHA256WithRSA (对应sign_type为RSA2 )
# 导入RSA模块，提供了RSA加密和解密的功能
from Crypto.PublicKey import RSA
# 导入PKCS1_v1_5模块，实现了PKCS#1 v1.5标准中定义的数字签名算法
from Crypto.Signature import PKCS1_v1_5
# 导入SHA256模块，提供了SHA-256哈希算法的实现
from Crypto.Hash import SHA256
# 导入base64模块中的decodebytes和encodebytes函数，用于对字节数据进行Base64编码和解码
from base64 import decodebytes, encodebytes
# 把生成的签名赋值给 sign 参数 ，拼接到请求参数中
from urllib.parse import quote_plus


class AliPay(object):

    def __init__(self, APP_ID, NOTIFI_URL, RETURN_URL, ALIPAY_SECRET, ALIPAY_PUBLIC):
        self.APP_ID = APP_ID
        self.RETURN_URL = RETURN_URL
        self.NOTIFI_URL = NOTIFI_URL
        self.ALIPAY_SECRET = ALIPAY_SECRET
        self.ALIPAY_PUBLIC = ALIPAY_PUBLIC

    def run(self, order_id, total_price, title):
        params = self.init_params(order_id, total_price, title)
        keys = self.generateKeys(params)
        return self.montageKeys(params,keys)

    def init_params(self, order_id, total_price, title):
        params = {
            'app_id': self.APP_ID,  # 支付宝分配给开发者的应用ID
            'method': "alipay.trade.page.pay",  # 接口名称
            'format': "JSON",
            'return_url': self.RETURN_URL,  # HTTP/HTTPS开头字符串
            'notify_url': self.NOTIFI_URL,  # 支付宝服务器主动通知商户服务器里指定的页面http/https路径。
            'charset': "utf-8",
            'sign_type': "RSA2",
            'timestamp': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),  # 发送请求的时间，格式"yyyy-MM-dd HH:mm:ss"
            'version': '1.0',
            'biz_content': {  # 业务请求参数放此下面
                'out_trade_no': str(order_id),  # 销售产品码，与支付宝签约的产品码名称。注：目前电脑支付场景下仅支持FAST_INSTANT_TRADE_PAY
                'product_code': "FAST_INSTANT_TRADE_PAY",
                'total_amount': total_price,  # 订单总金额，单位为元，精确到小数点后两位，取值范围为 [0.01,100000000]。金额不能为0。
                'subject': title,
            },
        }
        return params

    def generateKeys(self, params):
        unsigned_string = "&".join([f"{k}={v}" for k,v in self.ordered_data(params)])
        # 从文件中读取支付宝应用的私钥，并将其解析为RSA私钥对象
        private_key = RSA.importKey(open(self.ALIPAY_SECRET).read())
        # 使用私钥创建PKCS1_v1_5签名对象
        signer = PKCS1_v1_5.new(private_key)
        # 对待签名的字符串进行摘要计算，使用SHA256哈希算法，然后使用私钥对摘要进行签名，生成签名数据
        signature = signer.sign(SHA256.new(unsigned_string.encode("utf-8")))
        # 对签名之后进行 base64 编码 ，转化为字符串
        sign_string = encodebytes(signature).decode("utf-8").replace("\n", "")
        return sign_string


    def montageKeys(self, params, sign_string):
        # 生成签名后在 添加到原 params
        result = "&".join([f"{k}={params[k]}" for k in sorted(params)])
        result += "&sign=" + quote_plus(sign_string)
        return  result

    def ordered_data(self, data):
        # 初始化一个列表，用于存储字典类型的键
        complex_keys = []
        # 遍历数据字典的键值对
        for key, value in data.items():
            # 如果值是字典类型，则将键添加到 complex_keys 列表中
            if isinstance(value, dict):
                complex_keys.append(key)
        # 将字典类型的值转换为 JSON 字符串
        for key in complex_keys:
            data[key] = json.dumps(data[key], separators=(',', ':'))
        # 对字典的键值对按照键的顺序排序，并返回结果
        return sorted([(k, v) for k, v in data.items()])

    # 参数校验
    def verify(self, params, sign):
        # 从参数中移除 sign_type 键
        params.pop('sign_type', None)

        # 将参数按照键的顺序进行排序，并连接成字符串
        message = "&".join([f"{k}={v}" for k, v in self.ordered_data(params)])

        # 导入支付宝公钥并创建签名对象
        key = RSA.importKey(open(self.ALIPAY_PUBLIC).read())
        signer = PKCS1_v1_5.new(key)

        # 使用 SHA256 哈希算法计算消息摘要
        digest = SHA256.new()
        digest.update(message.encode('utf-8'))

        # 验证签名
        if signer.verify(digest, decodebytes(sign.encode('utf-8'))):
            return True
        return False



if __name__ == '__main__':
    from SAAS import settings
    alipay = AliPay(
        APP_ID = settings.ALIPAY_APP_ID,
        NOTIFI_URL= settings.NOTIFI_URL,
        RETURN_URL= settings.RETURN_URL,
        ALIPAY_SECRET= settings.ALIPAY_SECRET,
        ALIPAY_PUBLIC= settings.ALIPAY_PUBLIC
    )
    # keys = alipay.run(
    #     order_id="000115244ghj",
    #     total_price=1000,
    #     title="测试"
    # )
    # print(f"{settings.ALIPAY_GATEWAY}?{keys}")
    dic = {'charset': 'utf-8',
           'out_trade_no': '257ca866-40d8-41f3-91fd-4d74eb0fa5b2',
           'method': 'alipay.trade.page.pay.return',
           'total_amount': '112.90',
           'sign': 'opIWCm6BCHzG9IgXNhZD55fGZoWw1GuCYa8EBEyd+jkU+p8VpjtJfdbKAhWjYh1BfcjJKXQpBRC9jNExbsBsQYENOw1+BupAQg/P+loLmYppsHdDnmNUJS39B5uykzYS0wPjc99Ze7m3w054NfGU+X4i51SxejOh45gARUSjbCJzGVztFMUXE0SkePwuI/q46kUlWiJDDOdNpRxNuynZRV6b34f1NEH+BD9Zsli1UV+lx5AYNGzsGW0UFrJdH8Tv4cyjG9r749QQnEqDe0cGEMXzYPI33Fy0fKPbm5Hm7LbwK355h+LdzcQ3ovLiNhDbC4OruFE7Dmm+ogEMuIJxbQ==',
           'trade_no': '2024022322001413480502286807',
           'auth_app_id': '9021000134674758',
           'version': '1.0',
           'app_id': '9021000134674758',
           'sign_type': 'RSA2',
           'seller_id': '2088721030582415',
           'timestamp': '2024-02-23 16:08:50'}
    sign = dic.pop('sign')

    print(alipay.verify(dic,sign))