from django import forms
from django.core.exceptions import ValidationError

from web.forms.account import AddCssCodeFrom
from web import models


class CreateDirForm(AddCssCodeFrom, forms.ModelForm):
    name = forms.CharField(label="目录名称")
    class Meta:
        model = models.CosFileDir
        fields = ['name']

    def __init__(self,parent=None,request=None,file_type=1,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.parent = parent
        self.request = request
        self.file_type = file_type

    def clean_name(self):
        name = self.cleaned_data['name']
        if self.parent:
            exists = models.CosFileDir.objects.filter(
                project= self.request.user.project ,parent_id=self.parent, name=name, file_type=self.file_type
            ).exists()
        else:
            exists = models.CosFileDir.objects.filter(
                project=self.request.user.project, parent__isnull=True, name=name, file_type=self.file_type
            ).exists()
        if exists:
            raise ValidationError("当前目录下已存在此目录名。")
        return name

