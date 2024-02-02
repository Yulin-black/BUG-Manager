from django import forms
from django.core.exceptions import ValidationError
from web import models
from .BOOT_STYLE import AddCssCodeFrom


class AddOrEditWikiModelForm(AddCssCodeFrom, forms.ModelForm):

    class Meta:
        model = models.Wiki
        fields = ['title','text','parent']

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if request:
            data_list = [("","请选择"),]
            data = models.Wiki.objects.filter(project=request.user.project).values_list("id", "title")
            if self.instance:
                # 将 id 对应的数据 剔除
                data = data.exclude(id=self.instance.id)
            data_list.extend(data)
            # print(data_list)
            self.fields['parent'].choices = data_list


    def clean_title(self):
        title = self.cleaned_data['title']
        if not self.instance:
            exists = models.Wiki.objects.filter(title=title).exists()
            if exists:
                raise ValidationError("该文章已存在")
        return title


