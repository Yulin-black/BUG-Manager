import json

from django.views.decorators.csrf import csrf_exempt
from SAAS import settings
from django.shortcuts import render
from django.http import JsonResponse
from web.forms import fileForm
from web import models
from utils.tenxun_cos import delete_file, delete_file_list, get_credential
from utils.pro_tools import del_get_file_size, generateNAV, convert_bytes

def file(request, pro_id):
    form = fileForm.CreateDirForm()
    fid = request.GET.get("fid",None)

    filePath = (models.CosFileDir.objects.filter(parent_id=fid, project_id=pro_id)
                .order_by("file_type","id"))
    # 导航条
    if fid:
        nav_list = []
        nav_list.extend(generateNAV(fid))
        print(nav_list[::-1])
        file_project = models.CosFileDir.objects.filter(id=fid).first()
    else:
        file_project = None
        nav_list = []

    return render(request, "file.html", {
        "form":form, "filepath":filePath,
        "pathdict":nav_list[::-1],
        "parent": file_project
    })
def operateFolder(request, pro_id):
    """ 添加 & 重命名 & 删除"""
    if request.method == "POST":
        cr_parent = request.POST.get("cr_parent","")  # 添加 父级对象
        filePro = request.POST.get("filePro","")     # 当前对象
        rm_re_Pro = request.POST.get("rm_re_Pro","")     # 删除 还是 修改
        # print(request.POST)
        if not filePro:           # 添加 目录
            # print(cr_parent, type(cr_parent))
            form = fileForm.CreateDirForm(data=request.POST, parent=cr_parent, request=request)
            if form.is_valid():
                form.instance.file_type = 1
                if cr_parent:
                    form.instance.parent_id = cr_parent
                form.instance.project_id = pro_id
                form.instance.update_user = request.user.user
                form.save()
                data = {
                    "status":True,
                }
            else:
                data = {
                    "status": False,
                    "error":form.errors,
                }
            return JsonResponse(data)
        elif filePro.isdecimal():
            if rm_re_Pro == "rm":           # 删除
                file = models.CosFileDir.objects.filter(id=int(filePro),project_id=pro_id,update_user=request.user.user).first()
                if file:
                    delfile_path = request.user.project.name + file.file_path
                    if file.file_type == 1 :   # 删除 目录
                        list = [{"Key":delfile_path+file.name+"/"}]
                        list.extend(del_get_file_size(file, pro_id, request))
                        delete_file_list(request.user.user.bucket, list)        # 批量删除
                    else:                       # 删除 文件
                        # 释放 占用的 容量
                        request.user.project.usespace -= int(file.file_size)
                        request.user.project.save()
                        delete_file(request.user.user.bucket, delfile_path, file.name)  # 单文件删除
                    file.delete()
                    data = {
                        "status": True,
                    }
                else:
                    data = {
                        "status": False,
                        "error": "对象不存在。",
                    }
                return JsonResponse(data)
            else:                           # 重命名 目录
                file_project = models.CosFileDir.objects.filter(id=filePro,project_id=pro_id,update_user=request.user.user).first()
                # print(file_project)
                form = fileForm.CreateDirForm(data=request.POST, request=request, parent=file_project.parent, instance=file_project)
                if form.is_valid():
                    form.save()
                    data = {
                        "status": True,
                    }
                else:
                    data = {
                        "status": False,
                        "error":form.errors,
                    }
                return JsonResponse(data)
def delFolder(reqeust):
    pass

@csrf_exempt
def COS_CREDENTIAL(request, pro_id):
    if request.method == "POST":
        info_list = json.loads(request.body.decode("utf-8"))
        print(info_list)
        total_size = 0
        price_policy = request.user.price_policy
        price_policy_one = price_policy.per_file_size * (1024 ** 2)
        price_policy_all = price_policy.project_space * (1024 ** 3)
        for info in info_list:
            if int(info['size']) > price_policy_one:
                _, text = convert_bytes(int(info['size']))
                msg = f"当前套餐单个文件容量上限为：{price_policy.per_file_size}MB，本此添加文件名：{info['name']},文件大小：{text},已超出单个文件容量大小，请升级后在添加。"
                return JsonResponse({"status": False, "error": msg})
            total_size += int(info['size'])
        # print("总容量为：",total_size,"用户:",price_policy_one )

        if (request.user.project.usespace + total_size) > price_policy_all:
            _, text_1 = convert_bytes(request.user.project.usespace)
            _, text_2 = convert_bytes(total_size)
            msg = f"当前套餐总容量为：{price_policy.project_space}GB，当前项目已使用：{text_1}，本此添加：{text_2},超出总容量大小，请升级后在添加。"
            return JsonResponse({"status": False, "error": msg})
        return JsonResponse({"status": True})
    else:
        date = get_credential(request.user.user.bucket)
        return JsonResponse(date)

@csrf_exempt
def save_File(request, pro_id):
    if request.method == "POST":
        info = request.POST
        kb, text = convert_bytes(int(info.get('size')))
        print("名字为：", info.get("name"))
        models.CosFileDir.objects.create(
            name=info.get('name'),
            file_type = 2,
            file_size = kb,
            file_size_text = text,
            file_path = info.get('parent_file_path')+info.get('parent_name')+"/",
            parent_id = info.get('parent_id'),
            project_id = pro_id,
            update_user = request.user.user
        )
        file = models.Project.objects.filter(id=pro_id).first()
        file.usespace += int(kb)
        file.save()

        return JsonResponse({"status": True})


