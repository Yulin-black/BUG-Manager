from django.core.exceptions import ValidationError
from django_redis import get_redis_connection


class AddCssCodeFrom:
    noAddCss_label = []
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name in self.noAddCss_label:
                continue
            # 查找是否存在 class 样式，如需要从这里添加样式有需要在额外添加
            # 如使用这个在添加了一个样式  widgets = { "parent": forms.Select(attrs={"class":"selectpicker"}) }
            old_class = field.widget.attrs.get("class","")
            field.widget.attrs['class'] = f"{old_class} form-control"
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
