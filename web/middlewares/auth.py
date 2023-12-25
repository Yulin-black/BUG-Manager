import datetime

from django.utils.deprecation import MiddlewareMixin
from SAAS.settings import WHITE_URL_LIST
from django.shortcuts import redirect
from web import models


class User:
    def __init__(self):
        self.user = None
        self.price_policy = None
        self.project = None
        # self.path = None

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


    def process_view(self, request, view, args, kwargs):
        # 判断是否为 manage 开头
        if not request.path.startswith('/manage/'):
            return
        pro_id = kwargs.get('pro_id')
        # path = request.path.split("/")

        pro_object = models.Project.objects.filter(id=pro_id).first()
        if pro_object:      # 判断项目是否存在
            if pro_object.createdBy == request.user.user:   #此项目是否为当前用户的
                request.user.project = pro_object
                # request.user.path = path[3]
                return
        else:
            print("无此项目")
            return redirect("web:project_list")

        join_pro = models.ProjectUser.objects.filter(project=pro_object, invitee=request.user.user).first()
        if join_pro:    # 判断当前用户是否加入了此项目
            request.user.project = join_pro.project
            # request.user.path = path[3]
            return

        print("无权访问此项目")
        return redirect("web:project_list")
