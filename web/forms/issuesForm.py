from django import forms
from web import models
from web.forms.BOOT_STYLE import AddCssCodeFrom
from web.forms.widgets import ColorPrioritySelect

class IssuesModelForm(AddCssCodeFrom, forms.ModelForm):
    class Meta:
        model = models.Issues
        fields = ['issues_type','subject',"module","desc","state","priority","assign","attention","mode","parent","start_date","end_date"]
        widgets = {
            "parent": forms.Select(attrs={"data-live-search": "true"}),
            "assign": forms.Select(attrs={"data-live-search":"true"}),
            "attention": forms.SelectMultiple(attrs={"data-actions-box": "true"}),
            "priority": ColorPrioritySelect(),
        }
    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        super().__init__(*args, **kwargs)
        if request:
            for name, field in self.fields.items():
                if name in ["subject","desc"]:
                    continue
                old_class = field.widget.attrs.get("class", "")
                field.widget.attrs['class'] = f"{old_class} selectpicker"

            # 处理数据库初始化
            # 关注者 和 参与者
            total_user = list(models.ProjectUser.objects.filter(project=self.request.user.project).values_list("invitee__id","invitee__username"))
            self.fields['attention'].choices = [(self.request.user.user.id,self.request.user.user.username)] + total_user
            self.fields['assign'].choices = [("","没有选中任何选项")] + total_user

            # 父问题
            parent_list = list(models.Issues.objects.filter(project=self.request.user.project).values_list("id","subject"))
            self.fields['parent'].choices = [("","没有选中任何选项")] + parent_list

            # 问题类型 和 模块
            self.fields['issues_type'].choices = models.IssuesType.objects.filter(project=self.request.user.project).values_list("id","title")
            self.fields['module'].choices = [("", "没有选中任何选项")] + list(models.Module.objects.filter(project=self.request.user.project).values_list("id","title"))

















