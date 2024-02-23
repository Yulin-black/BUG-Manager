from django import forms
from web.forms.BOOT_STYLE import AddCssCodeFrom
from web import models


class DeleteProjectForm(AddCssCodeFrom, forms.ModelForm):
    name = forms.CharField(validators="")

    class Meta:
        model = models.Project
        fields = ['name']




