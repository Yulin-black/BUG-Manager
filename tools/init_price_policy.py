import os
import sys
import django

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(base_dir)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "SAAS.settings")
django.setup()

from web import models

models.UserInfo.objects.create(username="撒肯",password="123123",email="qq@qq.com")


