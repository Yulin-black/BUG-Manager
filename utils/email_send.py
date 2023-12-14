from django.core.mail import send_mail
import random
import string
from SAAS.settings import EMAIL_HOST_USER


def random_str(randomlen=8):
    # abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789
    chars = string.ascii_letters + string.digits
    # 从 chars 中随机抽取 8 个字符
    strcode = ''.join(random.sample(chars, randomlen))
    # print(strcode)
    return strcode

def send_email(email):
    code = random_str()
    email_body = f"邮箱验证码{code}"
    from_email = EMAIL_HOST_USER        # 拿到配置文件中
    # print(from_email)
    send_status = send_mail("Yulin", email_body, from_email, [email, ])
    if send_status:
        data = {"data":200}
    else:
        data =  {"data":101}
    return data, code
