from django.urls import path
from . import views

# app_name = "app01"



urlpatterns = [
    path('verify/', views.verify, name='verify'),
    path("register/", views.register, name='register'),
    path('redis/',views.testredis,name='redis'),
]
