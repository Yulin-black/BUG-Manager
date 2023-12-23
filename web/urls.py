from django.urls import path
from .views import account, home, project

app_name = 'web'

urlpatterns = [
    path('', home.index, name='index'),
    path('error_404', home.error_404, name='error_404'),

    path('send_email_info/', account.send_email_info, name='send_email'),
    path("register/", account.register, name='register'),
    path('login_email/', account.login_email, name='login_email'),
    path('login/', account.login, name='login'),
    path('logout/', account.logout, name='logout'),
    path('pic_code/',account.pic_code, name='picCode'),

    path('project/list/', project.project_list, name="project_list"),
    path('project/star/<type>/<pro_id>', project.project_star, name="project_star"),

]
