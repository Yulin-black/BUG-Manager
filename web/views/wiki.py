from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.urls import reverse
from web import models
from web.forms import wikiForm

def wiki(request, pro_id):
    """ wiki首页 """
    wiki_id = request.GET.get("wiki_id")
    # wiki_id 存在 并且 为一个数字
    if wiki_id and wiki_id.isnumeric():
        wiki_pro = models.Wiki.objects.filter(id=wiki_id).first()
        return render(request, "detailWiki.html", {'wiki_id':wiki_id,"form":wiki_pro})

    return render(request, "wiki.html")

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