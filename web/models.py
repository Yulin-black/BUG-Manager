from django.db import models

# Create your models here.

class UserInfo(models.Model):
    username = models.CharField(verbose_name="用户名", max_length=64)
    password = models.CharField(verbose_name="密码", max_length=255)
    email = models.EmailField(verbose_name="邮箱", max_length=32)
    mobile_phone = models.CharField(verbose_name="手机号", max_length=32, blank=True, null=True)


class PricePolicy(models.Model):
    """ 价格策略 """
    category_choices = (
        (1,"免费版"),(2,"收费版"),(3,"其它")
    )

    category = models.SmallIntegerField(verbose_name="收费类型", default=2, choices=category_choices)
    title = models.CharField(verbose_name='标题',max_length=64)

    price = models.PositiveIntegerField(verbose_name="价格")
    project_num = models.PositiveIntegerField(verbose_name="项目数")
    project_number = models.PositiveIntegerField(verbose_name="项目成员数")
    project_space = models.PositiveIntegerField(verbose_name="单项目空间")
    per_file_size = models.PositiveIntegerField(verbose_name="单文件大小")

    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

class Transaction(models.Model):
    """ 交易记录 """
    status_choice = (
        (1, "未支付"),(2, "已支付")
    )
    status = models.SmallIntegerField(verbose_name="状态", choices=status_choice,  default=1)
    order = models.CharField(verbose_name="订单号", max_length=64, unique=True) # 唯一索引

    user = models.ForeignKey(UserInfo, verbose_name="用户", on_delete=models.CASCADE)
    price_policy = models.ForeignKey(PricePolicy, on_delete=models.CASCADE, verbose_name="价格策略")

    count = models.IntegerField(verbose_name="数量（年）", help_text="0为无期限", default=0)
    price = models.IntegerField(verbose_name="实际支付价格",  default=0)

    start_datetime = models.DateTimeField(verbose_name="开始时间", null=True, blank=True)
    end_datetime = models.DateTimeField(verbose_name="结束时间", null=True, blank=True)
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

class Project(models.Model):
    """ 项目 """
    COLOR_CHOICES = (
        (1,"#56b8eb"),(2,"#f28033"),(3,"#ebc656"),(4,"#a2d148"),
        (5,"#20BFA4"),(6,"#7461c2"),(7,"#20bfa3")
    )

    name = models.CharField(verbose_name="项目名称", max_length=32)
    desc = models.CharField(verbose_name="描述", max_length=255, null=True, blank=True)
    color = models.SmallIntegerField(verbose_name="颜色", choices=COLOR_CHOICES, default=1)
    star = models.BooleanField(verbose_name="收藏", default=False)

    join_count = models.SmallIntegerField(verbose_name="参与人数", default=1)
    createdBy = models.ForeignKey(UserInfo, on_delete=models.CASCADE, verbose_name="创建者")
    # usespace = models.CharField(verbose_name="已使用空间")

    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

class ProjectUser(models.Model):
    """ 项目参与者 """
    user = models.ForeignKey(UserInfo, related_name="admin", verbose_name="用户", on_delete=models.CASCADE)
    project = models.ForeignKey(Project, verbose_name="项目", on_delete=models.CASCADE)

    invitee = models.ForeignKey(UserInfo, related_name="member", on_delete=models.CASCADE, verbose_name="被邀请者")
    star = models.BooleanField(verbose_name="收藏", default=False)

    create_datetime = models.DateTimeField(verbose_name="加入时间", auto_now_add=True)









