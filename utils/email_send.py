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

def send_email(email, tpl):
    code = random_str()
    if tpl ==  50001 :
        title = "邮箱登录"
        email_body = f"<h1>您使用邮箱登录的验证码为：</br>{code}</h1>"
    elif tpl == 50002:
        title = "邮箱注册"
        email_body = f"<h1>您使用邮箱注册的验证码为：</br>{code}</h1>"
    else:
        title = "密码找回"
        email_body = f"<h1>您使用邮箱找回密码的验证码为：</br>{code}</h1>"
    from_email = EMAIL_HOST_USER        # 拿到配置文件中
    # print(from_email)
    send_status = send_mail(subject=title, message='', html_message=email_body, from_email=from_email,recipient_list=[email, ])
    if send_status:
        data = {"data":200}
    else:
        data =  {"data":1001, "error":"网络异常！" }
    return data, code
