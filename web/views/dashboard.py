from datetime import datetime, timedelta
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from web import models
from django.db.models import Count


def dashboard(request, pro_id):
    # 问题数据处理
    status_dict = {}
    for k, v in models.Issues.state_ch:
        status_dict[k] = {"title": v, "count": 0}
    issues_data = models.Issues.objects.filter(project_id=pro_id).values("state").annotate(count=Count('id'))
    for item in issues_data:
        status_dict[item['state']]['count'] = item['count']
    # 项目成员
    project_join_user = models.ProjectUser.objects.filter(project_id=pro_id).values_list("invitee_id",
                                                                                         "invitee__username")
    # 动态
    top_10 = models.Issues.objects.filter(project_id=pro_id, assign__isnull=False).order_by("-id")[0:10]

    context = {
        "status_dict": status_dict,
        "project_join_user": project_join_user,
        "top": top_10
    }
    return render(request, "dashboard.html", context=context)


def zhaoLing(request, pro_id):
    # 获取过去30天的日期
    start_date = datetime.now().date() - timedelta(days=30)
    # 使用聚合函数统计每天创建的问题数量
    data_dict = models.Issues.objects.filter(
        project_id=pro_id,
        create_datetime__gte=start_date
    ).values('create_datetime__date').annotate(count=Count('id'))

    # 将结果转换为字典
    data_dict = {str(item['create_datetime__date']): item['count'] for item in data_dict}
    data_dict_l = {}
    # 获取当前日期
    current_date = datetime.now().date()
    for i in range(30, 0, -1):
        past_date = str(current_date - timedelta(days=i-1))
        data_dict_l[past_date] = [int(datetime.strptime(past_date, "%Y-%m-%d").timestamp())*1000, 0]

    for date_string, count in data_dict.items():
        data_dict_l[date_string][1] += count
    # print(list(data_dict_l.values()))

    return JsonResponse({"status": True, "data": list(data_dict_l.values())})
