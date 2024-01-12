from web import models
from utils.tenxun_cos import delete_file

# 释放 该目录下所有文件的 容量  并 从cos中删除 该目录下所有文件
def del_get_file_size(file, pro_id, request):
    list = []
    files_pro = models.CosFileDir.objects.filter(parent=file, project_id=pro_id, update_user=request.user.user).all()
    for files in files_pro:
        # print(files.name)
        delfile_path = request.user.project.name + files.file_path
        if files.file_type == 1:
            # delete_file(request.user.user.bucket, delfile_path, files.name+"/")
            list.append({"Key":delfile_path+files.name+"/"})
            list.extend(del_get_file_size(files, pro_id, request))
        elif files.file_type == 2:
            print(request.user.project.usespace, files.file_size,
                  type(request.user.project.usespace), type(files.file_size))
            request.user.project.usespace -= int(files.file_size)
            request.user.project.save()
            list.append({"Key":delfile_path+files.name})
            # delete_file(request.user.user.bucket, delfile_path, file.name)
    return list


# 生成导航条
def generateNAV(fid):
    list = []
    file = models.CosFileDir.objects.filter(id = fid).first()
    list.append({"name":file.name,"id":file.id})
    if file.parent:
        list.extend(generateNAV(file.parent_id))
    return list