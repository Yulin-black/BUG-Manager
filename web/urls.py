from django.urls import path, include
from .views import account, home, project, manage

app_name = 'web'

urlpatterns = [
    path('', home.index, name='index'),
    path('error_404', home.error_404, name='error_404'),

    # 登录-注册
    path('send_email_info/', account.send_email_info, name='send_email'),
    path("register/", account.register, name='register'),
    path('login_email/', account.login_email, name='login_email'),
    path('login/', account.login, name='login'),
    path('logout/', account.logout, name='logout'),
    path('pic_code/',account.pic_code, name='picCode'),

    # 项目列表
    path('project/list/', project.project_list, name="project_list"),
    path('project/star/<type>/<pro_id>', project.project_star, name="project_star"),

    # 项目管理
    path('manage/<pro_id>/', include(([
        path("dashboard/", manage.dashboard, name="dashboard"),
        path("issues/", manage.issues, name="issues"),
        path("statistics/", manage.statistics, name="statistics"),
        path("file/", manage.file, name="file"),
        path("wiki/", manage.wiki, name="wiki"),
        path("setting/", manage.setting, name="setting"),
    ],"manage"))),
]
