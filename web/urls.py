from django.urls import path
from .views import account


urlpatterns = [
    path('index/', account.index, name='index'),

]
