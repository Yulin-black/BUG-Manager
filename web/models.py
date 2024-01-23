from django.db import models

# Create your models here.

""" 用户 """
class UserInfo(models.Model):
    username = models.CharField(verbose_name="用户名", max_length=64)
    password = models.CharField(verbose_name="密码", max_length=255)
    email = models.EmailField(verbose_name="邮箱", max_length=32)
    mobile_phone = models.CharField(verbose_name="手机号", max_length=32, blank=True, null=True)

    project_order = models.ForeignKey(verbose_name="价格策略订单", to="Transaction", on_delete=models.CASCADE, blank=True, null=True)

    bucket = models.CharField(verbose_name="COS桶名称", max_length=64)




""" 价格策略 """
class PricePolicy(models.Model):
    """ 价格策略 """
    category_choices = (
        (1,"免费版"),(2,"收费版"),(3,"其它")
    )

    category = models.SmallIntegerField(verbose_name="收费类型", default=2, choices=category_choices)
    title = models.CharField(verbose_name='标题',max_length=64)

    price = models.PositiveIntegerField(verbose_name="价格")
    project_num = models.PositiveIntegerField(verbose_name="项目数")
    project_number = models.PositiveIntegerField(verbose_name="项目成员数", help_text="人数")
    project_space = models.PositiveIntegerField(verbose_name="单项目空间", help_text="GB")
    per_file_size = models.PositiveIntegerField(verbose_name="单文件大小", help_text="MB")

    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

""" 交易记录 """
class Transaction(models.Model):

    status_choice = (
        (1, "未支付"),(2, "已支付")
    )
    status = models.SmallIntegerField(verbose_name="状态", choices=status_choice,  default=1)
    order = models.CharField(verbose_name="订单号", max_length=64, unique=True) # 唯一索引

    user = models.ForeignKey(UserInfo, verbose_name="用户", on_delete=models.CASCADE)
    price_policy = models.ForeignKey(PricePolicy, on_delete=models.CASCADE, verbose_name="价格策略")

    count = models.IntegerField(verbose_name="数量（年）", help_text="0为无期限")
    price = models.IntegerField(verbose_name="实际支付价格",  default=0)

    start_datetime = models.DateTimeField(verbose_name="开始时间", auto_now_add=True)
    end_datetime = models.DateTimeField(verbose_name="结束时间")
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

""" 项目 """
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
    # usespace = models.PositiveIntegerField(verbose_name="已使用空间", default=0, help_text="KB")
    # usespace = models.PositiveBigIntegerField(verbose_name="已使用空间", default=0, help_text="BY")
    usespace = models.BigIntegerField(verbose_name="已使用空间", default=0, help_text="BY")

    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)

""" 项目参与者 """
class ProjectUser(models.Model):
    user = models.ForeignKey(UserInfo, related_name="admin", verbose_name="用户", on_delete=models.CASCADE)
    project = models.ForeignKey(Project, verbose_name="项目", on_delete=models.CASCADE)

    invitee = models.ForeignKey(UserInfo, related_name="member", on_delete=models.CASCADE, verbose_name="被邀请者")
    star = models.BooleanField(verbose_name="收藏", default=False)

    create_datetime = models.DateTimeField(verbose_name="加入时间", auto_now_add=True)

""" Wiki """
class Wiki(models.Model):
    title = models.CharField(verbose_name="标题", max_length=64)
    text = models.TextField(verbose_name="文本内容")
    project = models.ForeignKey(to=Project, verbose_name="项目", on_delete=models.CASCADE)
    parent = models.ForeignKey('self', verbose_name="父级", related_name='children', on_delete=models.CASCADE, null=True, blank=True)

    level = models.PositiveSmallIntegerField(verbose_name="层次", default=1)

class UploadedFile(models.Model):

    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)


class CosFileDir(models.Model):
    FileDir_TYPR = (
        (1,"目录"),(2,"文件")
    )
    project = models.ForeignKey(to=Project, verbose_name= "项目", on_delete=models.CASCADE)
    name = models.CharField(verbose_name="文件名或目录名", max_length=64)

    file_type = models.SmallIntegerField(verbose_name="类型", choices=FileDir_TYPR)
    file_size = models.PositiveIntegerField(verbose_name="文件大小", default=0)
    file_size_text = models.CharField(verbose_name="文件大小(kb,mb,gb)", default=0, max_length=16)
    file_path = models.CharField(verbose_name="文件路径",max_length=255, null=True, blank=True, default="/")

    parent = models.ForeignKey('self', verbose_name="父级", related_name='children', on_delete=models.CASCADE, null=True, blank=True)
    key = models.CharField(verbose_name="cosKey",blank=True, null=True, max_length=128)

    update_user = models.ForeignKey(UserInfo, verbose_name="上传者", on_delete=models.SET_DEFAULT,default="已注销")
    update_time = models.DateTimeField(verbose_name="最近更新时间", auto_now_add=True)


from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
@receiver(post_save,sender=CosFileDir)
@receiver(post_delete,sender=CosFileDir)
def update_project_usespace(sender, instance, **kwargs):
    # 获取与当前 CosFileDir 实例关联的 Project 模型实例。
    project = instance.project
    # 计算累加值
    # 计算一个模型中 file_size 字段的总和，并将结果存储在 total_size 变量中。如果没有匹配的记录，它将返回 0 作为默认值。
    # .aggregate() 方法来计算一个模型中特定字段的总和。
    added_value = CosFileDir.objects.filter(project=project).aggregate(total_size=models.Sum('file_size'))['total_size'] or 0
    # 更新 usespace 字段
    project.usespace = added_value
    project.save()