from django.urls import path, include
from django.conf.urls.static import static
from SAAS import settings
from .views import (
    account, home, project, manage, wiki, file
)

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

        # 文件管理
        path("file/", file.file, name="file"),
        path("file/operateFolder", file.operateFolder, name="operateFolder"),
        path("file/downloadFile", file.downloadFile, name="downloadFile"),
        path("file/COS_CREDENTIAL",file.COS_CREDENTIAL, name='COS_CREDENTIAL'),
        path('file/save_File',file.save_File, name="save_File"),

        # wiki 管理
        path("wiki/", wiki.wiki, name="wiki"),
        path("wiki/add/", wiki.addWiki, name='add_wiki'),
        path("wiki/del/<wiki_id>/", wiki.wiki_delete, name='wiki_delete'),
        path("wiki/wiki_edit/<wiki_id>/", wiki.wiki_edit, name='wiki_edit'),
        path('wiki/catalogWiki/', wiki.catalogWiki, name='catalogWiki'),
        path('wiki_upload/',wiki.wiki_upload_cos, name="wiki_upload"),

        path("setting/", manage.setting, name="setting"),
    ],"manage"))),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

