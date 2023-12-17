"""
用户注册相关功能：注册、短信、登录、注销
"""
from django_redis import get_redis_connection
from django.core.exceptions import ValidationError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from web.forms import account
from utils.email_send import send_email, random_str


def index(request):
    return render(request, "index.html")

def register(request):
    if request.method == 'POST':
        print(request.POST)
        form = account.RegisterModelForm(request.POST)
        if form.is_valid():
            form.save()
            return JsonResponse({"status": True})
        else:
            return JsonResponse({"status":False, "error":form.errors})
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
        return JsonResponse({"status":True})
    else:
        return JsonResponse({"status": False, "error": form.errors})