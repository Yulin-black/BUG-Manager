import datetime
import json
import uuid

from django.shortcuts import render, redirect
from django_redis import get_redis_connection
from django.http import JsonResponse, HttpResponse
from utils.ali_pay import AliPay
from SAAS import settings
from web import models


def index(request):
    return render(request, "index.html", )


def price(request):
    price_policy_list = models.PricePolicy.objects.filter(category=2).all()
    return render(request, "price.html", {"price_policy_list": price_policy_list})


def payment(request, policy_id):
    policy_object = models.PricePolicy.objects.filter(category=2, id=policy_id).first()
    number = request.GET.get('number', None)
    # 判断数据的有效性
    if (not policy_object) or (not number) or (not number.isdecimal()) or (int(number) < 1):
        return redirect('web:price')
    # 计算原价
    origin_price = int(number) * policy_object.price
    # 融合套餐
    balance = 0
    transaction_object = request.user.user.project_order
    #  当前以存在付费套餐
    if transaction_object:
        # 买了多少天
        total_timedate = transaction_object.end_datetime - transaction_object.start_datetime
        # 还剩多少天
        balance_timedate = transaction_object.end_datetime - datetime.datetime.now()
        balance = transaction_object.price / total_timedate.days * (
            balance_timedate.days - 1 if total_timedate == balance_timedate else balance_timedate).days

    if balance >= origin_price:
        return redirect('web:price')

    context = {
        "policy_id": policy_object.id,
        "number": number,
        "origin_price": origin_price,
        "balance": round(balance, 2),
        "total_price": round(origin_price - balance, 2)
    }
    print(context)

    conn = get_redis_connection("default")
    key = f"payment_{request.user.user.email}"
    # if conn.get(key):
    #     conn.delete(key)
    value = json.dumps(context)
    conn.set(key, value, ex=60 * 15)

    context['policy'] = policy_object

    return render(request, "payment.html", context)


def pay(request):
    conn = get_redis_connection("default")
    key = f"payment_{request.user.user.email}"
    context_string = conn.get(key)
    if not context_string:
        return redirect('web:price')

    context = json.loads(context_string.decode('utf8'))
    order_id = uuid.uuid4()
    models.Transaction.objects.create(
        status=1,
        order=order_id,
        count=context['number'],
        user=request.user.user,
        price_policy_id=context['policy_id'],
        price=context['total_price']
    )

    alipay = AliPay(
        APP_ID=settings.ALIPAY_APP_ID,
        NOTIFI_URL=settings.NOTIFI_URL,
        RETURN_URL=settings.RETURN_URL,
        ALIPAY_SECRET=settings.ALIPAY_SECRET,
        ALIPAY_PUBLIC=settings.ALIPAY_PUBLIC
    )
    keys = alipay.run(
        order_id=order_id,
        total_price=context['total_price'],
        title="tracer payment"
    )
    return redirect(f"{settings.ALIPAY_GATEWAY}?{keys}")


def pay_notify(request):
    alipay = AliPay(
        APP_ID=settings.ALIPAY_APP_ID,
        NOTIFI_URL=settings.NOTIFI_URL,
        RETURN_URL=settings.RETURN_URL,
        ALIPAY_SECRET=settings.ALIPAY_SECRET,
        ALIPAY_PUBLIC=settings.ALIPAY_PUBLIC
    )
    """ 支付成功的回调页面 """
    if request.method == "POST":
        # 状态更新
        from urllib.parse import parse_qs
        body_str = request.body.decode("utf-8")
        post_data = parse_qs(body_str)
        post_dict = {}
        for k, v in  post_data.items():
            post_dict[k] = v[0]

        sign = post_dict.pop('sign', None)

        if alipay.verify(post_dict, sign):
            # 获取订单号
            out_trade_no = post_dict['out_trade_no']
            # 根据订单号对数据库进行操作
            return HttpResponse("success")
        return HttpResponse("error")
    else:
        # 页面跳转，判断你是否支付成功
        # 支付宝会返回 订单 id
        params = request.GET.dict()
        sign = params.pop('sign',None)
        if alipay.verify(params, sign):
            return HttpResponse("支付完成")
        return HttpResponse("支付失败")


def error_404(request):
    return render(request, "404.html", )
