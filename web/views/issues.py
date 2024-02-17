import json
import random
import datetime
import time

from django.urls import reverse
from django.utils import timezone

from utils.iterators_tools import ChoicesButton, ForeignKeySelect
from utils.email_send import random_str
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from utils.pagination import Pagination
from web import models
from web.forms import issuesForm


def issues(request, pro_id):
    """ 添加问题 && 问题页面 """
    if request.method == "POST":
        form = issuesForm.IssuesModelForm(data=request.POST)
        if form.is_valid():
            form.instance.creator = request.user.user
            form.instance.project = request.user.project
            form.save()
            return JsonResponse({"status": True, "data": "添加成功"})
        else:
            return JsonResponse({"status": False, "error": form.errors})

    form = issuesForm.IssuesModelForm(request=request)
    # 筛选 & 分页
    condition = {}
    for name in ['module', 'state', 'priority', 'assign', 'attention']:
        value_list = request.GET.getlist(name)
        if not value_list:
            continue
        condition[f'{name}__in'] = value_list
    issues_object_list = models.Issues.objects.filter(project_id=pro_id).filter(**condition)
    new_page = int(request.GET.get("page", 1))
    page = Pagination(new_page, 5, len(issues_object_list), request)

    project_total_user = [(request.user.project.createdBy.id, request.user.project.createdBy.username)]
    project_join_user = models.ProjectUser.objects.filter(project_id=pro_id).values_list("invitee_id",
                                                                                         "invitee__username")
    project_total_user.extend(project_join_user)
    # 邀请成员
    invite_form = issuesForm.InviteModelForm()

    return render(request, "issues.html", {
        "form": form,
        "invite_form": invite_form,
        "iss_obj": issues_object_list[page.start:page.end],
        "cont": page.page_html,
        "filter_list": [
            {"title": "问题类型",
             "filter_sift": ChoicesButton("module",
                                          models.Module.objects.filter(project_id=pro_id).values_list(
                                              'id',
                                              'title'),
                                          request)},
            {"title": "状态", "filter_sift": ChoicesButton("state", models.Issues.state_ch, request)},
            {"title": "优先级",
             "filter_sift": ChoicesButton("priority", models.Issues.priority_ch, request)},
            {"title": "指派者",
             "filter_sift": ForeignKeySelect("assign", project_join_user, request)},
            {"title": "关注者",
             "filter_sift": ForeignKeySelect("attention", project_total_user, request)},
        ],
    })


def iss_detail(request, pro_id, iss_id):
    """ 添加评论 """
    if request.method == 'POST':
        content = request.POST.get("content", None)

        if (not content) or (not models.Project.objects.filter(id=pro_id).exists()) or (
                not models.Issues.objects.filter(id=iss_id).exists()):
            return JsonResponse({"status": False})

        parent_id = request.POST.get("parent_id", None)
        grandf_id = request.POST.get("grandf_id", None)

        print(parent_id, grandf_id)
        instance = models.IssuesRecord.objects.create(
            record_type=2,
            content=content,
            creator_id=request.user.user.id,
            grandfather_id=None if grandf_id == "null" else grandf_id,
            parent_id=None if parent_id == "null" else parent_id,
            issues_id=iss_id,
        )

        return JsonResponse({"status": True, "data": {
            "id": instance.id,
            "user": instance.creator.username,
            "content": instance.content,
            "type": instance.get_record_type_display(),
            "date": instance.create_date.strftime("%Y年%m月%d日 %H:%M"),
            "parent_name": instance.parent.creator.username if instance.parent else None,
            "grandf_id": instance.grandfather.id if instance.grandfather else None,
            "count": 0 if not instance.grandfather else instance.grandfather.count if instance.grandfather.count else 0,
        }})

    """ 问题详情页 """
    iss_project = models.Issues.objects.filter(id=iss_id, project_id=pro_id).first()
    form = issuesForm.IssuesModelForm(request=request, instance=iss_project)
    record_list = models.IssuesRecord.objects.filter(issues_id=iss_id, issues__project_id=pro_id).order_by(
        "create_date").all()

    return render(request, "issues_detail.html",
                  {"form": form, "record": record_list, "iss_id": iss_id})


@csrf_exempt
def update_issue(request, pro_id, iss_id):
    if request.method == 'POST':
        print(request.POST)
        post_dict = json.loads(request.body.decode('utf-8'))
        name = post_dict.get('name', None)
        value = post_dict.get("value", None)

        issue_project = models.Issues.objects.filter(project_id=pro_id, id=iss_id).first()
        if not issue_project:
            return JsonResponse({"status": False, "error": "找不到对应的问题"})

        field = models.Issues._meta.get_field(name)  # 获取 字段中的属性
        field_type = field.get_internal_type()  # 获取 字段的类型

        content = None

        # 处理文本类型字段
        if (field_type in ['CharField', 'TextField', 'DateField']) and (not field.choices):
            old_value = getattr(issue_project, name)
            if not value:
                if field.null:
                    setattr(issue_project, name, None)
                else:
                    return JsonResponse({"status": False, "error": f"{field.verbose_name}不能为空！", "id": name})
            else:
                setattr(issue_project, name, value)
            issue_project.save()

            new_value = getattr(issue_project, name)
            if name != 'desc':
                content = f"修改了 {field.verbose_name}：'{old_value}'-->'{new_value}'"
            else:
                content = f"修改了 {field.verbose_name}"
        # 处理外键类型字段
        elif field_type == 'ForeignKey':
            old_value = getattr(issue_project, name)
            if not value:
                if field.null:
                    setattr(issue_project, name, None)
                else:
                    return JsonResponse({"status": False, "error": f"{field.verbose_name}不能为空！", "id": name})
            else:
                setattr(issue_project, f"{name}_id", value)
            issue_project.save()

            new_value = getattr(issue_project, name)
            print(new_value, type(new_value))
            if old_value:
                content = f"修改了 {field.verbose_name}：'{old_value}'-->'{new_value if new_value else '空'}'"
            else:
                content = f"添加了 {field.verbose_name}：-->'{new_value}'"
        # 处理选择类型字段
        elif field.choices:
            old_value = getattr(issue_project, f"get_{name}_display")()

            setattr(issue_project, name, value)
            issue_project.save()

            new_value = None
            for item in getattr(issue_project, f"{name}_ch"):
                if value == str(item[0]):
                    new_value = item[1]
                    break
            content = f"修改了 {field.verbose_name}：'{old_value}'-->'{new_value}'"
        # 处理多对多类型字段
        elif field_type == 'ManyToManyField':
            if not isinstance(value, list):
                return JsonResponse({"status": False, "error": "数据错误"})

            old_value_list = []
            new_value_list = []
            createdBy_id = request.user.project.createdBy.id
            for item in value:
                if int(item) == createdBy_id:
                    old_value_list.append({"id": createdBy_id, "username": request.user.project.createdBy.username})
                pro_user = models.ProjectUser.objects.filter(invitee_id=int(item), project_id=pro_id).first()
                if pro_user:
                    old_value_list.append({"id": pro_user.invitee.id, "username": pro_user.invitee.username})

            attention_project = issue_project.attention.all()
            for item in attention_project:
                new_value_list.append({"id": item.id, "username": item.username})

            unique_to_list1 = [item for item in old_value_list if item not in new_value_list]
            unique_to_list2 = [item for item in new_value_list if item not in old_value_list]

            for item in unique_to_list1:
                issue_project.attention.add(item['id'])

            for item in unique_to_list2:
                issue_project.attention.remove(item['id'])
            issue_project.save()

            content = f"""{(f"添加了关注者：{[item['username'] for item in unique_to_list1]}") if unique_to_list1 else ""}{f"取消了关注者：{[item['username'] for item in unique_to_list2]}" if unique_to_list2 else ""}"""

        if not content:
            return JsonResponse({"status": False, "error": "找不到对应的问题"})

        instance = models.IssuesRecord.objects.create(
            record_type=1,
            content=content,
            creator_id=request.user.user.id,
            issues_id=iss_id,
        )

        return JsonResponse({"status": True, "data": {
            "id": instance.id,
            "user": instance.creator.username,
            "content": instance.content,
            "type": instance.get_record_type_display(),
            "date": instance.create_date.strftime("%Y年%m月%d日 %H:%M")
        }})

    return JsonResponse({"status": False})


def invite_member(request, pro_id):
    if request.method == "POST":
        print(request.POST)
        form = issuesForm.InviteModelForm(request.POST)
        if form.is_valid():
            if request.user.user != request.user.project.createdBy:
                form.add_error("period", "无此权限")
                return JsonResponse({"status": False, "error": form.errors})

            code = random_str(random.randint(20, 32))
            invite_project = models.ProjectInvite.objects.filter(project_id=pro_id).first()
            if not invite_project:
                form.instance.project = request.user.project
                form.instance.code = code
                form.instance.creator = request.user.user
                form.save()
            else:
                invite_project.code = code
                invite_project.count = form.cleaned_data.get('count')
                invite_project.period = form.cleaned_data.get('period')
                invite_project.save()

            url = f"{request.scheme}://{request.get_host()}{reverse('web:join', kwargs={'code':code})}"
            return JsonResponse({"status": True, "data": url})

        return JsonResponse({"status": False, "error": form.errors})


def join_project(request, code):
    """ 访问邀请码 """
    invite_object = models.ProjectInvite.objects.filter(code=code).first()
    # 不存在
    if not invite_object:
        return render(request, "invite_join.html", {"error":"邀请码不存在"})
    # 创建者
    if invite_object.project.createdBy == request.user.user:
        return render(request, "invite_join.html", {"error":"创建者无需加入"})
    # 已加入
    if models.ProjectUser.objects.filter(invitee=request.user.user,project=invite_object.project).exists():
        return render(request, "invite_join.html", {"error": "已加入此项目无需再加入"})
    # 超出限制
    if request.user.price_policy.project_number <= invite_object.project.join_count:
        return render(request, "invite_join.html", {"error": "项目成员已满，请联系项目主升级套餐"})
    # 邀请码 是否过期
    if ((timezone.now()-invite_object.creator_datetime).total_seconds() / 60) >= invite_object.period:
        return render(request, "invite_join.html", {"error": "邀请码已过期"})
    # 超出人数限制
    if invite_object.count:
        if invite_object.use_count >= invite_object.count:
            return render(request, "invite_join.html", {"error": "邀请码数量已使用完"})
        invite_object.use_count += 1
        invite_object.save()
    # 加入
    models.ProjectUser.objects.create(invitee=request.user.user, project=invite_object.project,
                                      user=invite_object.creator)
    return render(request, "invite_join.html",{'id':invite_object.project.id})