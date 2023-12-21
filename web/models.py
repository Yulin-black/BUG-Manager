from django.db import models

# Create your models here.

class UserInfo(models.Model):
    username = models.CharField(verbose_name="用户名", max_length=64)
    password = models.CharField(verbose_name="密码", max_length=255)
    email = models.EmailField(verbose_name="邮箱", max_length=32)
    mobile_phone = models.CharField(verbose_name="手机号", max_length=32, blank=True, null=True)


class PricePolicy(models.Model):
    category_choices = ((1,"免费版"),(2,"收费版"),(3,"其它"))

    category = models.SmallIntegerField(verbose_name="收费类型", default=2, choices=category_choices)
    title = models.CharField(verbose_name='标题',max_length=64)
    price = models.PositiveIntegerField(verbose_name="价格")

    project_num = models.PositiveIntegerField(verbose_name="项目数")
    project_number = models.PositiveIntegerField(verbose_name="项目成员数")
    project_space = models.PositiveIntegerField(verbose_name="单项目空间")
    per_file_size = models.PositiveIntegerField(verbose_name="单文件大小")

    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

class Project(models.Model):
    COLOR_CHOICES = (
        (1,""),(1,""),(1,""),(1,""),(1,""),
        (1,""),(1,""),(1,""),(1,""),(1,"")
    )

    projectname = models.CharField(verbose_name="项目名称")
    desc = models.TextField(verbose_name="描述")
    color = models.CharField(verbose_name="颜色", choices=COLOR_CHOICES)
    coll = models.BinaryField(verbose_name="收藏")
    participatenumber = models.CharField(verbose_name="参与人数")
    createdBy = models.ForeignKey(UserInfo, on_delete=models.CASCADE, verbose_name="创建者")
    usespace = models.CharField(verbose_name="已使用空间")
