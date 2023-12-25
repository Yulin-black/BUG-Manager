from django.urls import reverse

from web import models
from django import template

register = template.Library()

# simple_tag
@register.simple_tag
def peroject_list(request):
    my = models.Project.objects.filter(createdBy=request.user.user).all()
    join = models.ProjectUser.objects.filter(invitee=request.user.user).all()
    return {"my": my , "join": join }


# inclusion_tag
@register.inclusion_tag("inclusion/project_list.html")
def project_list(request):
    my = models.Project.objects.filter(createdBy=request.user.user).all()
    join = models.ProjectUser.objects.filter(invitee=request.user.user).all()
    return {"my": my , "join": join }


@register.inclusion_tag('inclusion/manage_menu_list.html')
def manage_menu_list(request):
    data_list = [
        {'title': '概览','url': reverse("web:manage:dashboard", kwargs={'pro_id': request.user.project.id})},
        {'title': '问题','url': reverse("web:manage:issues", kwargs={'pro_id': request.user.project.id})},
        {'title': '统计','url': reverse("web:manage:statistics", kwargs={'pro_id': request.user.project.id})},
        {'title': 'wiki','url': reverse("web:manage:wiki",kwargs = {'pro_id': request.user.project.id})},
        {'title': '文件','url': reverse("web:manage:file" ,kwargs = {'pro_id': request.user.project.id})},
        {'title': '配置','url': reverse("web:manage:setting", kwargs={'pro_id': request.user.project.id})},
    ]

    for data in data_list:
        if data['url'] in request.path:
            data['class'] = "active"
            break

    return {"data_list":data_list}


