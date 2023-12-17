from django import forms
# 这种类型的异常可以用于验证表单、模型或其他数据。
from django.core.exceptions import ValidationError
from django_redis import get_redis_connection
from web import models
from django.core.validators import RegexValidator
from SAAS import settings

class RegisterModelForm(forms.ModelForm):
    email = forms.EmailField(label="邮箱", )
    password = forms.CharField(label="密码", widget=forms.PasswordInput())
    code = forms.CharField(label="验证码", max_length=32)
    confirm_password = forms.CharField(label="重复密码", widget=forms.PasswordInput())

    class Meta:
        # 表单将使用 models.UserInfo 中的所有字段，并根据这些字段创建表单的web_userinfo HTML 表单域。
        model = models.UserInfo
        fields = ["username", "password", "confirm_password", "email", "code"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs['class'] = "form-control"
            field.widget.attrs['placeholder'] = f"请输入{field.label}"

    def clean_confirm_password(self):
        password = self.cleaned_data['password']
        if password != self.cleaned_data['confirm_password']:
            raise ValidationError("俩次密码不一致！")
        return password

    def clean_code(self):
        # 验证 验证码是否正确
        conn = get_redis_connection()
        code = self.cleaned_data['code']
        bemail = conn.get(self.cleaned_data['email'])
        email = bemail.decode('utf-8')
        if email != code:
            raise ValidationError("验证码错误！")
        return code

class EmailForm(forms.Form):
    email = forms.EmailField(label="邮箱账号")
    # email = forms.CharField(label="邮箱账号")
    tpl = forms.CharField(label="验证类型")

    def clean_tpl(self):
        tpl = self.cleaned_data['tpl']
        tpl_id = settings.EMAIL_AUTO_TEMPLATE.get(tpl)
        if not tpl_id:
            # self.add_error("tpl",'短信信息模板错误')
            # 上下代码等价，区别于 下面会直接跳出程序
            raise ValidationError('短信信息模板错误')
        # print("类型验证通过", tpl_id)
        return tpl_id

    def clean_email(self):
        email = self.cleaned_data['email']
        exists = models.UserInfo.objects.filter(email=email).exists()
        if exists:
            raise ValidationError("此邮箱已注册！")
        # print("邮箱验证通过")
        return email







