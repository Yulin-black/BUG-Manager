from django.urls import path, include
from django.conf.urls.static import static
from SAAS import settings
from .views import (
    account, home, project, statistics, wiki, file,
    pro_settting, issues, dashboard
)

app_name = 'web'

urlpatterns = [
    path('', home.index, name='index'),
    path('error_404', home.error_404, name='error_404'),
    path('price', home.price, name="price"),
    path('payment/<policy_id>', home.payment, name="payment"),
    path('pay',home.pay, name="pay"),
    path('pay/notify/', home.pay_notify, name="notify"),

    # 登录-注册
    path('send_email_info/', account.send_email_info, name='send_email'),
    path("register/", account.register, name='register'),
    path('login_email/', account.login_email, name='login_email'),
    path('login/', account.login, name='login'),
    path('logout/', account.logout, name='logout'),
    path('pic_code/', account.pic_code, name='picCode'),

    # 项目列表
    path('project/list/', project.project_list, name="project_list"),
    path('project/star/<type>/<pro_id>', project.project_star, name="project_star"),

    # 项目管理
    path('manage/<pro_id>/', include(([
        path("dashboard/", dashboard.dashboard, name="dashboard"),
        path("zhaoLing/", dashboard.zhaoLing, name="zhaoLing"),

        # 问题管理
        path("issues/", issues.issues, name="issues"),
        path("issues/detail/<iss_id>/", issues.iss_detail, name="issDetail"),
        path("update_issue/<iss_id>", issues.update_issue, name="updateIssue"),
        path("invite/", issues.invite_member, name='invite'),

        path("statistics/", statistics.statistics, name="statistics"),
        path("applicationData/", statistics.ApplicationData, name='ApplicationData'),

        # 文件管理
        path("file/", file.file, name="file"),
        path("file/operateFolder", file.operateFolder, name="operateFolder"),
        path("file/downloadFile", file.downloadFile, name="downloadFile"),
        path("file/COS_CREDENTIAL", file.COS_CREDENTIAL, name='COS_CREDENTIAL'),
        path('file/save_File', file.save_File, name="save_File"),

        # wiki 管理
        path("wiki/", wiki.wiki, name="wiki"),
        path("wiki/add/", wiki.addWiki, name='add_wiki'),
        path("wiki/del/<wiki_id>/", wiki.wiki_delete, name='wiki_delete'),
        path("wiki/wiki_edit/<wiki_id>/", wiki.wiki_edit, name='wiki_edit'),
        path('wiki/catalogWiki/', wiki.catalogWiki, name='catalogWiki'),
        path('wiki_upload/', wiki.wiki_upload_cos, name="wiki_upload"),

        # 设置
        path("setting/", pro_settting.setting, name="setting"),
        path('setting/del', pro_settting.deldete, name="set_deldete"),
        path('setting/password', pro_settting.changeYourPassword,
           name="changeYourPassword"),
        path('setting/personalData', pro_settting.personalData, name='personalData'),
        ], "manage"))),
    path('join/<code>', issues.join_project, name='join'),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
