from django.urls import path
from .views import account

app_name = 'web'

urlpatterns = [
    path('', account.index, name='index'),
    path('send_email_info/', account.send_email_info, name='send_email'),
    path("register/", account.register, name='register'),
    path('login/', account.login, name='login'),
]
