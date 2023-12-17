from django import forms
from . import models
from django.core.validators import RegexValidator


class RegisterModelForm(forms.ModelForm):
    password = forms.CharField(label="密码", widget=forms.PasswordInput())
    mobile_phone = forms.CharField(label="手机号", validators=[RegexValidator(
        r'^(1[3|4|5|6|7|8|9]\d{9}$','手机号格式错误'
    ), ])
    confirm_password = forms.CharField(label="重复密码", widget=forms.PasswordInput())
    code = forms.CharField(label="验证码", widget=forms.TextInput(
        attrs={'class':'form-control'}
    ))
    class Meta:
        # 表单将使用 models.UserInfo 中的所有字段，并根据这些字段创建表单的 HTML 表单域。
        model = models.UserInfo
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs['class'] = "form-control"
            field.widget.attrs['placeholder'] = f"请输入{field.label}"


class VerifyModelForm(forms.Form):
    # email = forms.EmailField(label="邮箱账号", )
    email = forms.CharField(label="邮箱账号", )
    code = forms.CharField(label="验证码", max_length=32)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs['class'] = "form-control"
            field.widget.attrs['placeholder'] = f"请输入{field.label}"

class EmailForm(forms.Form):
    email = forms.CharField(label="邮箱账号")