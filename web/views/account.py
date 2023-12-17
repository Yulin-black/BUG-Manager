"""
用户注册相关功能：注册、短信、登录、注销
"""
from django_redis import get_redis_connection
from django.core.exceptions import ValidationError
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from web.forms import account
from utils.email_send import send_email, random_str
from web.register_decorator import is_allowd_to_register
from SAAS import settings


def index(request):
    return render(request, "index.html")

# 只能从 verify 中跳转过来 有bug
@is_allowd_to_register
def register(request, email):
    if request.method == 'POST':
        print(request.POST)
        form = account.RegisterModelForm(request.POST)
        if form.is_valid():
            form.save()
            print("asdasdasdsa")
            settings.GLOBAL_VARIABLE['register'] = False
            return JsonResponse({"status": True})
        else:
            return JsonResponse({"status":False, "error":form.errors})
    else:
        form = account.RegisterModelForm(initial={'email':email})
    # print(email)
    return render(request, "register.html", {"form": form})

def verify(request):
    if request.method == 'POST':
        # 校验 邮箱 和 验证码
        form = account.VerifyForm(request.POST)
        if form.is_valid():
            conn = get_redis_connection()

            email = form.cleaned_data["email"]
            code = form.cleaned_data['code']
            # print(email, code)
            conn.set(email, code, ex=120)
            ran_str = random_str(4)
            settings.GLOBAL_VARIABLE['register'] = True
            # conn.set("register", email, ex=600)
            # conn.set(email, ran_str, ex=600)

            # 验证通过就跳转到 注册页面
            return redirect('web:register')
            # return HttpResponseRedirect(reverse('register'))
        else:
            print("code数据校验失败", form.errors)
    else:
        # 获取用户上传的邮箱，向验证邮箱，向邮箱发送验证码
        if request.GET.get('email') and request.GET.get('tpl'):
            print("ajax获取到了邮箱:", request.GET.get('email'),
                  "类型为：",request.GET.get('tpl'))
            # print(request.GET)
            # 没用 code 值则为获取验证码 request.is_ajax()
            form = account.EmailForm(data=request.GET)
            if form.is_valid():
                email = form.cleaned_data['email']
                tpl_id = form.cleaned_data['tpl']
                data, code = send_email(email, tpl_id)
                if data['data'] == 1001 :
                    raise ValidationError(f"邮件发送失败{data['error']}")

                conn = get_redis_connection("default")
                conn.set(email, code, ex=120)

                return HttpResponse(data['data'])
            else:
                print("数据校验失败", form.errors)
        else:
            form = account.VerifyForm()
    return render(request, "verify.html", {"form":form})


