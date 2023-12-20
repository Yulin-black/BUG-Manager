from django import forms
# 这种类型的异常可以用于验证表单、模型或其他数据。
from django.core.exceptions import ValidationError
from django_redis import get_redis_connection
from web import models
from SAAS import settings
from django.contrib.auth.hashers import make_password, check_password

class AddCssCodeFrom:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            field.widget.attrs['class'] = "form-control"
            field.widget.attrs['placeholder'] = f"请输入{field.label}"

    def clean_code(self):
        # 验证 验证码是否正确
        conn = get_redis_connection()
        code = self.cleaned_data['code']
        # print(self.cleaned_data)
        print(self.data.get)
        email = self.data.get('email')
        value = conn.get(email)
        if not value:
            raise ValidationError("验证码未发送或者已失效！")
        email_code = value.decode('utf-8')
        if email_code != code:
            raise ValidationError("验证码错误！")
        # 验证成功后从redis中删除验证码
        conn.delete(email)
        return code

class RegisterModelForm(AddCssCodeFrom, forms.ModelForm):
    """ 用户注册 """
    email = forms.EmailField(label="邮箱")
    password = forms.CharField(label="密码",
                               min_length=2,
                               error_messages={
                                   'min_length':'密码长度不能小于8个字符',
                               },
                               widget=forms.PasswordInput())
    code = forms.CharField(label="验证码", max_length=32)
    confirm_password = forms.CharField(label="重复密码", widget=forms.PasswordInput())

    class Meta:
        # 表单将使用 models.UserInfo 中的所有字段，并根据这些字段创建表单的web_userinfo HTML 表单域。
        model = models.UserInfo
        fields = ["username", "password", "confirm_password", "email", "code"]

    def clean_email(self):
        email = self.cleaned_data['email']
        exists = models.UserInfo.objects.filter(email=email).exists()
        if exists:
            raise ValidationError("此邮箱已注册！")
        # print("邮箱验证通过")
        return email

    def clean_password(self):
        # 对密码 加密
        password = self.cleaned_data['password']
        return make_password(password)

    def clean_confirm_password(self):
        password = self.cleaned_data['password']
        confirm_password = self.cleaned_data['confirm_password']
        # print(password,confirm_password)
        if not check_password(confirm_password, password):
            raise ValidationError("俩次密码不一致！")
        return confirm_password

class EmailForm(forms.Form):
    """
    邮件校验
    """
    email = forms.EmailField(label="邮箱账号")
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
        print(self.data)
        email = self.cleaned_data['email']
        if self.data['tpl'] == "register":
            exists = models.UserInfo.objects.filter(email=email).exists()
            if exists:
                raise ValidationError("此邮箱已注册！")
            # print("邮箱验证通过")
        elif self.data['tpl'] == "login" or self.data['tpl'] == "retpasswd":
            exists = models.UserInfo.objects.filter(email=email).exists()
            if not exists:
                raise ValidationError("此邮箱未注册！")
        # elif self.data['tpl'] == "retpasswd":
        #     exists = models.UserInfo.objects.filter(email=email).exists()
        #     if not exists:
        #         raise ValidationError("此邮箱未注册！")
        else:
            raise ValidationError('短信信息模板错误')
        return email

class EmailLoginForm(AddCssCodeFrom, forms.Form):
    """ 用户登录 """
    email = forms.EmailField(label="邮箱账号")
    code = forms.CharField(label="验证码")

class PicCodeLoginForm(AddCssCodeFrom, forms.Form):
    email = forms.EmailField(label="邮箱账号")
    password = forms.CharField(label="密码", widget=forms.PasswordInput())
    pic_code = forms.CharField(label="验证码")

    def __init__(self, request=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = request

    def clean_email(self):
        email = self.cleaned_data['email']
        user_object = models.UserInfo.objects.filter(email=email).first()
        if not user_object:
            raise ValidationError("此邮箱未注册")
        password = self.data.get('password')

        if not check_password(password, user_object.password):
            raise ValidationError("邮箱账号或者密码错误")
        return user_object

    def clean_pic_code(self):
        code = self.cleaned_data['pic_code'].upper()
        session_code = self.request.session.get('picCode')
        if not session_code:
            raise ValidationError("验证码不存在或已过期。")
        if code != session_code:
            raise ValidationError("验证码错误。")
        return code





