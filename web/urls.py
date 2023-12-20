from django.urls import path
from .views import account

app_name = 'web'

urlpatterns = [
    path('', account.index, name='index'),
    path('send_email_info/', account.send_email_info, name='send_email'),
    path("register/", account.register, name='register'),
    path('login_email/', account.login_email, name='login_email'),
    path('login/', account.login, name='login'),
    path('logout/', account.logout, name='logout'),
    path('pic_code/',account.pic_code, name='picCode'),
]
