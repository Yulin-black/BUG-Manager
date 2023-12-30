"""
用户注册相关功能：注册、短信、登录、注销
"""
import datetime
import uuid
import asyncio
from asgiref.sync import sync_to_async
from io import BytesIO
from django_redis import get_redis_connection
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from web.forms import account
from utils.email_send import send_email, random_str
from utils.picture_verification_code import check_code
from utils.decorators.create_bucket_dec import create_buckret_d
from utils.tenxun_cos import create_bucket
from utils.ProCoroutine import async_create_bucket
from web import models



# import asyncio
# from concurrent.futures import ThreadPoolExecutor
#
# loop = asyncio.get_event_loop()
# executor = ThreadPoolExecutor()

# 导入 线程池 库
from concurrent.futures import ThreadPoolExecutor


# 创建 线程池，维护了 5 个线程
pool = ThreadPoolExecutor(5)


def register(request):
    if request.method == 'POST':
        print("register视图：", request.POST)
        form = account.RegisterModelForm(data=request.POST)
        if form.is_valid():
            bucket = str(random_str(12))
            form.instance.bucket = bucket
            # instance = form.save(), 在数据库中新增一条数据，并将新增的数据对象赋值
            form.save()  # 保存数据
            # 使用线程
            # pool.submit(create_bucket, bucket)

            # create_bucket(bucket)

            # 启动异步存储桶创建
            # 将异步函数提交到线程池中执行
            # loop.run_in_executor(executor, async_create_bucket, bucket)

            # 使用 sync_to_async 装饰器转换异步函数为同步函数
            # create_bucket = sync_to_async(async_create_bucket)

            # asyncio.create_task(async_create_bucket(bucket))
            return JsonResponse({"status": True, "data": "/login/"})
        else:
            return JsonResponse({"status": False, "error": form.errors})
    else:
        form = account.RegisterModelForm()
    return render(request, "register.html", {"form": form})

def send_email_info(request):
    # 获取用户上传的邮箱，向验证邮箱，向邮箱发送验证码
    print("ajax获取到了邮箱:", request.GET.get('email'),
          "类型为：", request.GET.get('tpl'))
    # print(request.GET)
    form = account.EmailForm(data=request.GET)
    if form.is_valid():
        email = form.cleaned_data['email']
        tpl_id = form.cleaned_data['tpl']
        data, code = send_email(email, tpl_id)
        if data['data'] == 1001:
            raise ValueError(f"邮件发送失败{data['error']}")
        conn = get_redis_connection("default")
        conn.set(email, code, ex=120)
        return JsonResponse({"status": True})
    else:
        return JsonResponse({"status": False, "error": form.errors})

def login_email(request):
    if request.method == "POST":
        print("ajax获取到了邮箱:", request.POST.get('email'),
              "验证码：", request.POST.get('code'))
        form = account.EmailLoginForm(data=request.POST)
        if form.is_valid():
            user = models.UserInfo.objects.filter(email=form.cleaned_data.get('email')).first()
            # 保存用户登录状态
            request.session['user_id'] = user.id
            request.session.set_expiry(60*60*24*14)

            return JsonResponse({"status": True, "data": "/"})
        else:
            return JsonResponse({"status": False, "error": form.errors})
    else:
        form = account.EmailLoginForm()

    return render(request, "login_email.html", {"form":form})

def login(request):
    if request.method == 'POST':
        print("ajax获取到了邮箱:", request.POST.get('email'),
              "密码：", request.POST.get('password'),
              "验证码：", request.POST.get('pic_code'))

        form = account.PicCodeLoginForm(data = request.POST, request=request)
        if form.is_valid():
            user = form.cleaned_data.get('email')
            request.session['user_id'] = user.id
            request.session.set_expiry(60*60*24*14)
            return redirect('web:index')
    else:
        form = account.PicCodeLoginForm()
    return render(request, "login.html",{"form":form})

def logout(request):
    request.session.flush()     # 清空当前用户的session
    return redirect("web:index")

def pic_code(request):
    img, code = check_code()
    print("code:", code)

    request.session['picCode'] = code       # 存入session中
    request.session.set_expiry(60)          # 设置验证码60秒失效
    # 创建一个 BytesIO 对象
    stream = BytesIO()
    img.save(stream,"png")      # 将图片存入内存中
    # 取出对象
    # stream.getvalue()
    return HttpResponse(stream.getvalue())
