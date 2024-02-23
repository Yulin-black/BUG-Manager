import json
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import JsonResponse
from web.forms import fileForm
from web import models
from utils.tenxun_cos import delete_file, delete_file_list, get_credential, check_file
from utils.pro_tools import del_get_file_size, generateNAV, convert_bytes
from utils.email_send import random_str


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
            print(cr_parent, type(cr_parent))
            form = fileForm.CreateDirForm(data=request.POST, parent=cr_parent, request=request)
            if form.is_valid():
                form.instance.file_type = 1
                form.instance.key = f"{random_str()}-{form.data.get('name')}"       # 为目录添加唯一key
                if cr_parent:
                    parent = models.CosFileDir.objects.filter(id=cr_parent).first()
                    form.instance.parent = parent
                    form.instance.file_path = f"{parent.file_path}{parent.key}/"
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
                if request.user.project.createdBy == request.user.user:     # 盘都时候为 当前项目的创建者
                    file = models.CosFileDir.objects.filter(id=int(filePro), project_id=pro_id).first()
                else:
                    file = models.CosFileDir.objects.filter(id=int(filePro),project_id=pro_id,update_user=request.user.user).first()
                if file:
                    delfile_path = request.user.project.name + file.file_path
                    if file.file_type == 1 :   # 删除 目录
                        list = [{"Key":delfile_path+file.key+"/"}]
                        list.extend(del_get_file_size(file, pro_id, request))
                        delete_file_list(request.user.project.createdBy.bucket, list)        # 批量删除
                    else:                       # 删除 文件
                        delete_file(request.user.project.createdBy.bucket, delfile_path, file.key)  # 单文件删除
                    file.delete()
                    data = {
                        "status": True,
                    }
                else:
                    data = {
                        "status": False,
                        "error": "无权删除。",
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
def downloadFile(reqeust,pro_id):
    fid = reqeust.GET.get('fid',None)
    if fid:
        fid_pro = models.CosFileDir.objects.filter(id=fid,project_id=pro_id).first()
        if fid_pro:
            data = {
                "status": True,
                "value": fid_pro.key,
            }
        else:
            data = {
                "status": False,
                "error": "项目异常!",
            }
    else:
        data = {
            "status": False,
            "error": "项目不存在。",
        }
    return JsonResponse(data)

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

            form = fileForm.CreateDirForm(data=info, parent=info['parent'], request=request, file_type=2)
            if not form.is_valid():
                return JsonResponse({"status": False, "error":f"当前目录下已存在名为 ‘{info['name']}’ 的文件。"})

            if int(info['size']) > price_policy_one:
                _, text = convert_bytes(int(info['size']))
                msg = f"当前套餐单个文件容量上限为：{price_policy.per_file_size}MB，本此添加文件名：{info['name']},文件大小：{text},已超出单个文件容量大小，请升级后在添加。"
                return JsonResponse({"status": False, "error": msg})
            total_size += int(info['size'])

        print("总容量为：",total_size)

        if (request.user.project.usespace + total_size) > price_policy_all:
            _, text_1 = convert_bytes(request.user.project.usespace)
            _, text_2 = convert_bytes(total_size)
            msg = f"当前套餐总容量为：{price_policy.project_space}GB，当前项目已使用：{text_1}，本此添加：{text_2},超出总容量大小，请升级后在添加。"
            return JsonResponse({"status": False, "error": msg})
        return JsonResponse({"status": True})

    else:
        date = get_credential(request.user.project.createdBy.bucket)
        return JsonResponse(date)

@csrf_exempt
def save_File(request, pro_id):
    if request.method == "POST":
        info = request.POST
        etag = info.get('etag', None)
        if etag:
            by, text = convert_bytes(int(info.get('size')))
            # print("名字为：", info.get("name"),info)
            file_path = info.get('parent_file_path') + info.get('parent_key') + "/"
            key_ = info.get('key')
            key = request.user.project.name + file_path + key_
            data = check_file(request.user.project.createdBy.bucket, key)
            ETag = data.get('ETag',None)
            if ETag and (ETag == etag):
                # 创建CosFileDir
                file_pro = models.CosFileDir.objects.create(
                    name=info.get('name'),
                    file_type=2,
                    file_size=by,
                    key=info.get('key'),
                    file_size_text=text,
                    file_path=file_path,
                    parent_id=info.get('parent_id'),
                    project_id=pro_id,
                    update_user=request.user.user
                )
                result = {
                    "id":file_pro.id,
                    "name":file_pro.name,
                    "size":text,
                    "upload_user":request.user.user.username,
                    "time":file_pro.update_time.strftime("%Y年%m月%d日 %H:%M")
                }
                return JsonResponse({"status": True,"result": result})
            else:
                return JsonResponse({"status": False, 'error': "ETag不匹配"})
        else:
            return JsonResponse({"status": False, 'error':"无ETag"})
