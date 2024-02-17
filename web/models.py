from django.db import models
from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

# Create your models here.

""" 用户 """


class UserInfo(models.Model):
    username = models.CharField(verbose_name="用户名", max_length=64)
    password = models.CharField(verbose_name="密码", max_length=255)
    email = models.EmailField(verbose_name="邮箱", max_length=32)
    mobile_phone = models.CharField(verbose_name="手机号", max_length=32, blank=True, null=True)

    project_order = models.ForeignKey(verbose_name="价格策略订单", to="Transaction", on_delete=models.CASCADE,
                                      blank=True, null=True)

    bucket = models.CharField(verbose_name="COS桶名称", max_length=64)

    def __str__(self):
        return self.username


""" 价格策略 """


class PricePolicy(models.Model):
    """ 价格策略 """
    category_choices = (
        (1, "免费版"), (2, "收费版"), (3, "其它")
    )

    category = models.SmallIntegerField(verbose_name="收费类型", default=2, choices=category_choices)
    title = models.CharField(verbose_name='标题', max_length=64)

    price = models.PositiveIntegerField(verbose_name="价格")
    project_num = models.PositiveIntegerField(verbose_name="项目数")
    project_number = models.PositiveIntegerField(verbose_name="项目成员数", help_text="人数")
    project_space = models.PositiveIntegerField(verbose_name="单项目空间", help_text="GB")
    per_file_size = models.PositiveIntegerField(verbose_name="单文件大小", help_text="MB")

    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)


""" 交易记录 """


class Transaction(models.Model):
    status_choice = (
        (1, "未支付"), (2, "已支付")
    )
    status = models.SmallIntegerField(verbose_name="状态", choices=status_choice, default=1)
    order = models.CharField(verbose_name="订单号", max_length=64, unique=True)  # 唯一索引

    user = models.ForeignKey(UserInfo, verbose_name="用户", on_delete=models.CASCADE)
    price_policy = models.ForeignKey(PricePolicy, on_delete=models.CASCADE, verbose_name="价格策略")

    count = models.IntegerField(verbose_name="数量（年）", help_text="0为无期限")
    price = models.IntegerField(verbose_name="实际支付价格", default=0)

    start_datetime = models.DateTimeField(verbose_name="开始时间", auto_now_add=True)
    end_datetime = models.DateTimeField(verbose_name="结束时间")
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)


""" 项目 """


class Project(models.Model):
    """ 项目 """
    COLOR_CHOICES = (
        (1, "#56b8eb"), (2, "#f28033"), (3, "#ebc656"), (4, "#a2d148"),
        (5, "#20BFA4"), (6, "#7461c2"), (7, "#20bfa3")
    )

    name = models.CharField(verbose_name="项目名称", max_length=32)
    desc = models.CharField(verbose_name="描述", max_length=255, null=True, blank=True)
    code = models.CharField(verbose_name="邀请码", max_length=64, null=True, blank=True)

    color = models.SmallIntegerField(verbose_name="颜色", choices=COLOR_CHOICES, default=1)
    star = models.BooleanField(verbose_name="收藏", default=False)

    join_count = models.SmallIntegerField(verbose_name="参与人数", default=1)
    createdBy = models.ForeignKey(UserInfo, on_delete=models.CASCADE, verbose_name="创建者")
    usespace = models.BigIntegerField(verbose_name="已使用空间", default=0, help_text="BY")

    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)


""" 项目参与者 """


class ProjectUser(models.Model):
    user = models.ForeignKey(UserInfo, related_name="admin", verbose_name="用户", on_delete=models.CASCADE)
    project = models.ForeignKey(Project, verbose_name="项目", on_delete=models.CASCADE)

    invitee = models.ForeignKey(UserInfo, related_name="member", on_delete=models.CASCADE, verbose_name="被邀请者")
    star = models.BooleanField(verbose_name="收藏", default=False)

    create_datetime = models.DateTimeField(verbose_name="加入时间", auto_now_add=True)

@receiver(post_save, sender=ProjectUser)
@receiver(post_delete, sender=ProjectUser)
def update_project_usespace(sender, instance, **kwargs):
    project = instance.project
    added_value = ProjectUser.objects.filter(project=project).count()
    project_object = Project.objects.filter(id=project.id).first()
    project_object.join_count = added_value
    project_object.save()

""" Wiki """


class Wiki(models.Model):
    title = models.CharField(verbose_name="标题", max_length=64)
    text = models.TextField(verbose_name="文本内容")
    project = models.ForeignKey(to=Project, verbose_name="项目", on_delete=models.CASCADE)
    parent = models.ForeignKey('self', verbose_name="父级", related_name='children', on_delete=models.CASCADE,
                               null=True, blank=True)

    level = models.PositiveSmallIntegerField(verbose_name="层次", default=1)


class UploadedFile(models.Model):
    file = models.FileField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)


class CosFileDir(models.Model):
    FileDir_TYPR = (
        (1, "目录"), (2, "文件")
    )
    project = models.ForeignKey(to=Project, verbose_name="项目", on_delete=models.CASCADE)
    name = models.CharField(verbose_name="文件名或目录名", max_length=64)

    file_type = models.SmallIntegerField(verbose_name="类型", choices=FileDir_TYPR)
    file_size = models.PositiveIntegerField(verbose_name="文件大小", default=0)
    file_size_text = models.CharField(verbose_name="文件大小(kb,mb,gb)", default=0, max_length=16)
    file_path = models.CharField(verbose_name="文件路径", max_length=255, null=True, blank=True, default="/")

    parent = models.ForeignKey('self', verbose_name="父级", related_name='children', on_delete=models.CASCADE,
                               null=True, blank=True)
    key = models.CharField(verbose_name="cosKey", blank=True, null=True, max_length=128)

    update_user = models.ForeignKey(UserInfo, verbose_name="上传者", on_delete=models.SET_DEFAULT, default="已注销")
    update_time = models.DateTimeField(verbose_name="最近更新时间", auto_now_add=True)


@receiver(post_save, sender=CosFileDir)
@receiver(post_delete, sender=CosFileDir)
def update_project_usespace(sender, instance, **kwargs):
    # 获取与当前 CosFileDir 实例关联的 Project 模型实例。
    project = instance.project
    # 计算累加值
    # 计算一个模型中 file_size 字段的总和，并将结果存储在 total_size 变量中。如果没有匹配的记录，它将返回 0 作为默认值。
    # .aggregate() 方法来计算一个模型中特定字段的总和。
    added_value = CosFileDir.objects.filter(project=project).aggregate(total_size=models.Sum('file_size'))[
                      'total_size'] or 0
    # 更新 usespace 字段
    project.usespace = added_value
    project.save()


class Issues(models.Model):
    """ 问题 """
    priority_ch = (("danger", "高"), ("warning", "中"), ("success", "低"))
    state_ch = ((1, "新建"), (2, "处理中"), (3, "已解决"), (4, "已忽略"),
                (5, "待反馈"), (6, "已关闭"), (7, "重新打开"),)
    mode_ch = ((1, "公开模式"), (2, "隐私模式"))

    subject = models.CharField(verbose_name="主题", max_length=64)
    desc = models.TextField(verbose_name="问题描述", blank=True, null=True)

    project = models.ForeignKey(verbose_name="项目", to="Project", on_delete=models.CASCADE)
    issues_type = models.ForeignKey(verbose_name="问题类型", to="IssuesType", on_delete=models.CASCADE)
    module = models.ForeignKey(verbose_name="模块", to="Module", on_delete=models.CASCADE)
    assign = models.ForeignKey(verbose_name="派指", to="UserInfo", on_delete=models.SET_NULL, blank=True, null=True,
                               related_name="assign_problems")
    attention = models.ManyToManyField(verbose_name="关注者", to='UserInfo', related_name="observer", blank=True)
    creator = models.ForeignKey(verbose_name="创建者", to='UserInfo', on_delete=models.SET_NULL, null=True, blank=True,
                                related_name="create_problems")
    parent = models.ForeignKey(verbose_name="父问题", to='self', related_name="child", null=True, blank=True,
                               on_delete=models.SET_NULL)

    state = models.PositiveSmallIntegerField(verbose_name="状态", choices=state_ch, default=1)
    priority = models.CharField(verbose_name="优先级", max_length=12, choices=priority_ch, default="danger")
    mode = models.PositiveSmallIntegerField(verbose_name="模式", choices=mode_ch, default=1)

    start_date = models.DateField(verbose_name="开始时间", null=True, blank=True)
    end_date = models.DateField(verbose_name="结束时间", null=True, blank=True)
    create_datetime = models.DateTimeField(verbose_name="创建时间", auto_now_add=True)
    latest_update_datetime = models.DateTimeField(verbose_name="最后更新时间", auto_now_add=True)

    def __str__(self):
        return self.subject


class IssuesType(models.Model):
    """ 模块（里程碑） 如: 第一期、第二期、第三期 """
    PROJECT_INIT_LIST = ['第一期', '第二期', '第三期']

    title = models.CharField(verbose_name="模块名称", max_length=32)
    project = models.ForeignKey(verbose_name="项目", to="Project", on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class Module(models.Model):
    """ 问题类型 如： 任务、问题、功能、BUG """
    PROJECT_INIT_LIST = ['任务', '功能', 'BUG']
    COLOR_CHOICES = (
        (1, "#62c9ff"), (2, "#f28033"), (3, "#ebc656"), (4, "#a2d148"),
        (5, "#20BFA4"), (6, "#7461c2"), (7, "#20bfa3")
    )
    title = models.CharField(verbose_name="类型名称", max_length=32)
    project = models.ForeignKey(verbose_name="项目", to="Project", on_delete=models.CASCADE)
    color = models.PositiveSmallIntegerField(verbose_name="颜色", choices=COLOR_CHOICES, default=1)

    def __str__(self):
        return self.title


class IssuesRecord(models.Model):
    record_type_choices = ((1, "修改记录"), (2, "回复"))
    #  ID 创建者 内容 提交类型 修改时间 父级
    record_type = models.PositiveSmallIntegerField(verbose_name="类型", choices=record_type_choices)
    content = models.TextField(verbose_name="记录内容")
    issues = models.ForeignKey(verbose_name="问题", to="Issues", on_delete=models.CASCADE)
    creator = models.ForeignKey(verbose_name="提交者", to="UserInfo", on_delete=models.SET_NULL, null=True, blank=True)
    parent = models.ForeignKey(verbose_name="父级", to="self", on_delete=models.CASCADE, related_name="child",
                               null=True, blank=True)
    grandfather = models.ForeignKey(verbose_name="祖宗级", to="self", on_delete=models.CASCADE,
                                    related_name="grandchildren", null=True, blank=True)
    create_date = models.DateTimeField(verbose_name="创建日期", auto_now_add=True)
    count = models.PositiveSmallIntegerField(verbose_name="评论计数", null=True, blank=True)


@receiver(post_save, sender=IssuesRecord)
@receiver(post_delete, sender=IssuesRecord)
def update_project_usespace(sender, instance, **kwargs):
    if instance.grandfather:
        grandfather_id = instance.grandfather_id
        count_new = IssuesRecord.objects.filter(grandfather_id=grandfather_id).count()
        grandfather_pro = IssuesRecord.objects.filter(id=grandfather_id).first()
        grandfather_pro.count = count_new
        grandfather_pro.save()


class ProjectInvite(models.Model):
    """项目邀请码"""
    period_choices = (
        (30, "30分钟"), (60, "1小时"), (300, "5小时"), (1440, "24小时")
    )

    project = models.OneToOneField(verbose_name="项目名称", to="Project", on_delete=models.CASCADE)
    creator = models.ForeignKey(verbose_name="创建者", to="UserInfo", on_delete=models.CASCADE,
                                related_name="create_invite")

    code = models.CharField(verbose_name="邀请码", max_length=64, unique=True)

    count = models.PositiveSmallIntegerField(verbose_name="限制数量", null=True, blank=True, help_text="空表示无限制")
    use_count = models.PositiveSmallIntegerField(verbose_name="已使用数量", default=0)
    period = models.PositiveSmallIntegerField(verbose_name="有效期", choices=period_choices, default=1440)
    creator_datetime = models.DateTimeField(verbose_name="更新时间", auto_now=True)
