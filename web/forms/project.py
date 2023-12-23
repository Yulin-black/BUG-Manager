from django import forms
from django.core.exceptions import ValidationError
from web.forms.widgets import ColorRadioSelect
from web.forms.account import AddCssCodeFrom
from web import models

class ProjectModelForm(AddCssCodeFrom, forms.ModelForm):
    noAddCss_label = ["color"]

    class Meta:
        model = models.Project
        fields = ['name','color','desc']
        widgets = {
            "desc": forms.Textarea(),
            "color": ColorRadioSelect(attrs={"class":"color_radio"}),
        }

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    def clean_name(self):
        name = self.cleaned_data.get('name')
        # 当前用户是否已经创建此项目
        exists = models.Project.objects.filter(name=name, createdBy = self.request.user.user).exists()
        if exists:
            raise ValidationError("项目名已存在。")
        # 当前用户额度是否还支持继续创建
        # 获取已经创建的项目数量
        count = models.Project.objects.filter(createdBy = self.request.user.user).count()
        print(count, self.request.user.price_policy.project_num)
        if count >= self.request.user.price_policy.project_num:
            raise ValidationError("创建失败，免费项目额度超限。")

        return name

