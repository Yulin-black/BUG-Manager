from django.shortcuts import render, redirect
from utils.tenxun_cos import delete_file_list
from web import models

def setting(request, pro_id):
    return render(request, "setting.html")

def deldete(request, pro_id):
    if request.method == "POST":
        pro_name = request.POST.get('project-name', None)
        if pro_name != request.user.project.name:
            return render(request, "set_delete.html",{"error":"项目名输入错误！"})
        if request.user.user != request.user.project.createdBy:
            return render(request, "set_delete.html", {"error": "无权删除本项目！"})
        # 从COS中删除
        project = models.Project.objects.filter(id=pro_id).first()
        file_list = models.CosFileDir.objects.filter(project = project).all()
        if file_list:
            list = [{"Key": request.user.project.name + "/"}]
            for file in file_list:
                delfile_path = request.user.project.name + file.file_path + file.key + ("/" if file.file_type == 1 else "")
                list.append({"Key" : delfile_path})
            delete_file_list(request.user.user.bucket, list)  # 批量删除
            # for i in list:
            #     print(i)
        # 从 数据库中删除
        project.delete()
        return redirect("web:project_list")

    return render(request, "set_delete.html")

def personalData(request, pro_id):
    return render(request, "set_personalData.html")

def changeYourPassword(request, pro_id):
    return render(request, "set_changeYourPassword.html")