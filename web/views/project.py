from django.http import JsonResponse
from django.shortcuts import render, redirect
from tools.project_tools import init_issues_module
from web.forms import project
from web import models


def project_list(request):
    """ 项目列表 """
    if request.method == "POST":
        print(request.POST)
        # 创建项目
        form = project.ProjectModelForm(data= request.POST, request=request)
        if form.is_valid():
            # 额外添加字段数据
            form.instance.createdBy = request.user.user
            instance = form.save()
            # 初始化 项目 问题类型
            init_issues_module(instance, models.IssuesType)
            # 初始化 项目 模块
            init_issues_module(instance, models.Module)

            return JsonResponse({"status": True, "data": "/login/"})
        else:
            return JsonResponse({"status": False, "error": form.errors})
    else:
        # GET
        project_dict = {"star":[], "my":[], "join":[]}
        my_project_list = models.Project.objects.filter(createdBy=request.user.user).all()
        join_project_list = models.ProjectUser.objects.filter(invitee=request.user.user).all()

        for myPro in my_project_list:
            if myPro.star:
                project_dict['star'].append(myPro)
            else:
                project_dict['my'].append(myPro)

        for joinPro in join_project_list:
            if joinPro.star:
                project_dict['star'].append(joinPro.project)
            else:
                project_dict['join'].append(joinPro.project)

        form = project.ProjectModelForm()

    return render(request, "project_list.html", {"form":form, "project_dict":project_dict})


def project_star(request, type, pro_id):
    # print(request.path)
    if type == "my":
        models.Project.objects.filter(createdBy=request.user.user, id=pro_id).update(star=True)

    elif type == "join":
        models.ProjectUser.objects.filter(project_id=pro_id, invitee=request.user.user).update(star=True)

    elif type == "star":
        pro_obj = models.Project.objects.filter(id=pro_id).first()
        # 判断是否为 加入的项目，不是自己创建的 则为 加入别人的项目
        if pro_obj.createdBy != request.user.user:
            pro_obj = models.ProjectUser.objects.filter(project_id=pro_id, invitee=request.user.user).first()
        pro_obj.star = False
        pro_obj.save()
    else:
        return redirect('web:error_404')

    return redirect('web:project_list')
