# 免除 csrf 认证 装饰器
import time

from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.urls import reverse
from SAAS.settings import MEDIA_URL, MEDIA_ROOT
from web import models
from web.forms import wikiForm


def wiki(request, pro_id):
    """ wiki首页 """
    wiki_id = request.GET.get("wiki_id")
    # wiki_id 存在 并且 为一个数字
    if wiki_id and wiki_id.isnumeric():
        wiki_pro = models.Wiki.objects.filter(id=wiki_id).first()
        return render(request, "detailWiki.html", {'wiki_id':wiki_id,"wiki_pro":wiki_pro})

    return render(request, "wiki.html")

# 目录
def catalogWiki(request, pro_id):
    data = (models.Wiki.objects.filter(project_id=pro_id)
            .values("id",'title',"parent")  # 查找到的数据只获取 "id",'title',"parent" 三个字段
            .order_by("level","id"))        # 按level排序 level相同按id排序
    # print(data)
    return JsonResponse({"status": True, "data": list(data)})
    # 使用DRF中的序列化
    # from web.forms import my_serializers
    # data = models.Wiki.objects.filter(project=request.user.project).all()
    # ser = my_serializers.CatalogSerializers(instance=data,many=True)
    # print(ser.data)
    # return JsonResponse({"status":True, "data":ser.data})

def addWiki(request, pro_id):

    if request.method == 'POST':
        form = wikiForm.AddOrEditWikiModelForm(data=request.POST)
        if form.is_valid():
            # 判断是否选择了父类
            if form.instance.parent:
                # 获取父类的层次 +1 设置的当前的层次
                 form.instance.level = form.instance.parent.level + 1
            form.instance.project = request.user.project
            form.save()
            # 使用 reverse() 获取 'wiki' 的 URL，并将其传递给 redirect() 函数：
            return redirect(reverse("web:manage:wiki", kwargs={'pro_id':pro_id}))
    else:
        form = wikiForm.AddOrEditWikiModelForm(request=request)
    return render(request, "addWiki.html",{"form":form})


def wiki_delete(request, pro_id, wiki_id):
    project = models.Wiki.objects.filter(project_id = pro_id, id = wiki_id).first()
    if project:
        project.delete()
    return render(request, "wiki.html")

def wiki_edit(request, pro_id, wiki_id):
    wiki_project = models.Wiki.objects.filter(project_id=pro_id, id=wiki_id).first()
    if request.method == 'POST':
        form = wikiForm.AddOrEditWikiModelForm(data=request.POST, instance=wiki_project)
        if form.is_valid():
            # 判断是否选择了父类
            if form.instance.parent:
                # 获取父类的层次 +1 设置的当前的层次
                 form.instance.level = form.instance.parent.level + 1
            form.instance.project = request.user.project
            form.save()
            # 使用 reverse() 获取 'wiki' 的 URL，并将其传递给 redirect() 函数：
            url = reverse("web:manage:wiki", kwargs={'pro_id':pro_id})
            return redirect(f"{url}?wiki_id={wiki_id}")
    else:
        if not wiki_project:
            # 反向生成URL
            url = reverse("web:manage:wiki", kwargs={'pro_id': pro_id})
            return redirect(url)

        form = wikiForm.AddOrEditWikiModelForm(request=request, instance=wiki_project)
    return render(request, "editWiki.html",{"form":form})



@csrf_exempt
def wiki_upload_cos(request, pro_id):
    """ 保存到腾讯COS """
    pass

@csrf_exempt
def wiki_upload_local(request, pro_id):
    """ 保存到本地 """
    # 显示不了在setting中加入这一句：X_FRAME_OPTIONS = 'SAMEORIGIN'
    # requst.FILES.get('editormd-image-file') 用户上传的图片文件
    file = request.FILES.get('editormd-image-file')
    if file:
        file_name = str(file).split(".")
        # 读取文件内容并创建 ContentFile 对象
        file_content = file.read()  # 获取文件内容的字节流
        new_file = ContentFile(file_content)
        new_file.name = f"{request.user.user.id}-{file_name[0]}-{str(time.time()).split('.')[0]}.{file_name[-1]}"
        instance = models.UploadedFile(file=new_file)
        instance.save()
        url = MEDIA_URL+ 'uploads/' + new_file.name

        result = {
            "success":1,
            "message":None,
            "url":url,
        }
    else:
        result = {
            "success":0,
            "message":None,
            "url":None,
        }
    return JsonResponse(result)



