from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse
from django_redis import get_redis_connection

from utils.email_send import send_email
from . import forms


def Send_eamil(request):
    data = send_email("1875916498@qq.com")
    return HttpResponse(data)


def register(request):
    form = forms.RegisterModelForm()
    # print(form)
    return render(request, "app01/register.html", {"form":form})


def verify(request):
    if request.method == 'POST':
        # 校验 邮箱 和 验证码
        form = forms.VerifyModelForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            code = form.cleaned_data['code']
            print(email, code)

            # 验证通过就跳转到 注册页面
            return redirect('app01:register')
            # return HttpResponseRedirect(reverse('register'))
        else:
            print("code数据校验失败", form.errors)
    else:
        # 获取用户上传的邮箱，向验证邮箱，向邮箱发送验证码
        if request.GET.get('email'):
            print("ajax获取到了邮箱:", request.GET.get('email'))

            # 没用 code 值则为获取验证码 request.is_ajax()
            form = forms.EmailForm(request.GET)
            if form.is_valid():
                eamil = form.cleaned_data['email']
                data, code = send_email(eamil)
                # print(data)

                return HttpResponse(data['data'])
            else:
                print("email数据校验失败", form.errors)
        else:
            form = forms.VerifyModelForm()
    return render(request, "app01/verify.html", {"form":form})

def testredis(request):
    # 从连接池中获取一个连接
    # 选择从哪个redis中获取，不写默认default
    conn = get_redis_connection("default")

    conn.set("test", "测试django-redis。", ex=120 )

    value = conn.get('test')
    return HttpResponse(value.decode('utf-8'))







