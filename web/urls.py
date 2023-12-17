from django.urls import path
from .views import account

app_name = 'web'

urlpatterns = [
    path('', account.index, name='index'),
    path('verify/', account.verify, name='verify'),
    path("register/", account.register, name='register'),
]
