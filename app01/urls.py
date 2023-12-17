from django.urls import path
from . import views

# 定义命名空间
app_name = 'app01'

urlpatterns = [
    path('verify/', views.verify, name='verify'),
    path("register/", views.register, name='register'),
    path('redis/',views.testredis,name='redis'),
]
