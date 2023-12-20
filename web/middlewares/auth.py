from django.utils.deprecation import MiddlewareMixin
from web import models

class AuthMiddleware(MiddlewareMixin):
    # 方法名固定
    """ 此函数返回什么，则用户就接收什么。无返回值则继续向后执行视图 """
    def process_request(self, request):
        noauth_paths = ['/pic_code/',]
        """ 如果用户已经登录，则request中会保存已登录的信息 """
        if not request.path in noauth_paths:
            print("中间件：", request.path )
            user_id = request.session.get('user_id', None)
            if not user_id:
                user_object = models.UserInfo.objects.filter(id=user_id).first()
                request.user =user_object