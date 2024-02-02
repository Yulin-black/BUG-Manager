from django.shortcuts import render
from django.http import JsonResponse
from utils.pagination import Pagination
from web import models
from web.forms import issuesForm


def issues(request, pro_id):
    if request.method == "POST":
        form = issuesForm.IssuesModelForm(data=request.POST)
        if form.is_valid():
            form.instance.creator = request.user.user
            form.instance.project = request.user.project
            form.save()
            return JsonResponse({"status": True,"data": "添加成功"})
        else:
            return JsonResponse({"status": False,"error": form.errors})

    form = issuesForm.IssuesModelForm(request=request)
    issues_object_list = models.Issues.objects.filter(project_id=pro_id).all()
    new_page = int(request.GET.get("page",1))
    page = Pagination(new_page,5,len(issues_object_list), request)

    return render(request, "issues.html", {"form": form,"iss_obj":issues_object_list[page.start:page.end],"cont":page.page_html})


def iss_detail(request, pro_id, iss_id):
    iss_project = models.Issues.objects.filter(id=iss_id, project_id=pro_id).first()
    form = issuesForm.IssuesModelForm(request=request, instance=iss_project)
    record = models.IssuesRecord.objects.filter(issues_id=iss_id,issues__project_id=pro_id).all()
    for rec in record:
        print(rec.content)
        if rec.parent:
            print(rec.parent.content)

    return render(request, "issues_detail.html",{"form":form})