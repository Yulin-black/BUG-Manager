from functools import wraps
from django_redis import get_redis_connection
from django.http import HttpResponse
from SAAS.settings import GLOBAL_VARIABLE

def is_allowd_to_register(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        conn = get_redis_connection()
        email = conn.get("register")

        # value = conn.get(email) if email else None

        # if value and (GLOBAL_VARIABLE['register'] == value.decode("utf-8")):
        #     print("+"*100)
        #     # print(GLOBAL_VARIABLE['register'], value.decode("utf-8"))
        #     return func(request, email.decode('utf-8'), *args, **kwargs)
        if email and GLOBAL_VARIABLE['register']:

            print("+"*100)
            # print(GLOBAL_VARIABLE['register'], value.decode("utf-8"))
            return func(request, email.decode('utf-8'), *args, **kwargs)
        else:
            print("-" * 100)
            return HttpResponse("token失效，请返回上级网页，重试。")  # 如果不是从 route_two 访问，则重定向到其他页面
    return wrapper