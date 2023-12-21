import datetime

from django.utils.deprecation import MiddlewareMixin
from SAAS.settings import WHITE_URL_LIST
from django.shortcuts import redirect
from web import models


class User:
    def __init__(self):
        self.user = None
        self.price_policy = None

class AuthMiddleware(MiddlewareMixin):
    # 方法名固定
    """ 此函数返回什么，则用户就接收什么。
        无返回值或返回为None 则表示通过中间件。
    """
    def process_request(self, request):
        noauth_paths = ['/pic_code/',]
        """ 如果用户已经登录，则request中会保存已登录的信息 """
        path = request.path
        if not path in noauth_paths:
            request.user = User()

            user_id = request.session.get('user_id', None)
            user_object = models.UserInfo.objects.filter(id=user_id).first()
            # 当前已登录的用户
            request.user.user = user_object

            # 访问的url在白名单内则直接放行
            if path in WHITE_URL_LIST:
                print("中间件-白名单中：", path)
                return
            # 用户未登录且访问的url不在白名单 不允许访问
            if not user_object:
                print("中间件-用户未登录禁止访问：", path)
                return redirect('web:login')

            # 自己想的(避免了排序,提高效率) 在用户表 添加了一个 Transaction 的外键
            if not user_object.project_order :
                # 不存在 使用免费策略
                request.user.price_policy = models.PricePolicy.objects.filter(category=1, title="个人免费版").first()
            elif user_object.project_order.end_datetime > datetime.datetime.now():
                # 存在 但是 已过期
                request.user.price_policy = models.PricePolicy.objects.filter(category=1, title="个人免费版").first()
                # 将过期策略清空
                user_object.project_order = None
            else:
                # 存在 且 未过期 使用未过期的策略
                request.user.price_policy = user_object.project_order.price_policy

            print("当前url:", path, "当前用户:", request.user.user.username, "当前价格策略:",request.user.price_policy.title)

            # 登录成功后访问后台时，获取当前用户的价格策略信息
            # 方式一: 免费的额度也存在交易记录中
            # 从交易记录中查找当前用户的价格策略
            # price_object = models.Transaction.objects.filter(user=user_object, status=2).order_by("-id").first()
            # # 判断当前价格策略是否过期
            # if price_object.end_datetime and price_object.end_datetime < datetime.datetime.now():
            #     # 过期
            #     # price_object = models.Transaction.objects.filter(user=user_object, status=2).order_by("id").first()
            #     price_object = models.Transaction.objects.filter(user=user_object, status=2, price_policy__category=1).first()
            # # 存值,将当前用户的价格策略对象保存
            # request.price_policy = price_object.price_policy

            # 方式二: 只有付费的存在交易记录中
            # 从交易记录中查找当前用户的价格策略
            # price_object = models.Transaction.objects.filter(user=user_object, status=2).order_by("-id").first()
            # # 判断是否存在价格策略对象 同时 判断当前价格策略是否过期
            # if price_object and (price_object.end_datetime and price_object.end_datetime > datetime.datetime.now()):
            #     # 存在且 未过期
            #     request.price_policy = price_object.price_policy
            # else:
            #     # 不存在 或者 过期则使用 免费策略
            #     request.price_policy = models.PricePolicy.objects.filter(category=1, title="个人免费版").exists()





