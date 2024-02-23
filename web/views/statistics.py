from django.db.models import Count
from web import models
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from datetime import datetime, timedelta


def statistics(request, pro_id):
    today = datetime.now().strftime("%Y-%m-%d")
    create_datetime = request.user.project.create_datetime
    tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

    date = {"today": today, "create_datetime": create_datetime.strftime('%Y-%m-%d'), "tomorrow": tomorrow}

    return render(request, "statistics.html", {"date": date})


@csrf_exempt
def ApplicationData(request, pro_id):
    if request.method == "POST":
        issues_project = models.Issues.objects.filter(project_id=pro_id,
                                                       latest_update_datetime__gte=request.POST.get('start_time'),
                                                       latest_update_datetime__lt=request.POST.get('end_time'))

        issues_data = issues_project.values("priority").annotate(count=Count('id'))
        priority_ch = models.Issues.priority_ch
        # 优先级
        priority_list = []
        for item in priority_ch:
            priority_list.append({"name": item[1], "y": 0})

        for item in issues_data:
            for pri in priority_ch:
                if item['priority'] == pri[0]:
                    for li in priority_list:
                        if li['name'] == pri[1]:
                            li['y'] = item['count']
                            break
                    break

        state_ch = models.Issues.state_ch
        progress_dict = {
            "categories": [],
            "series": []
        }
        test = []

        issues_project_assigned = issues_project.filter(assign__isnull=False)
        issues_project_notAssigned = issues_project.filter(assign__isnull=True)
        for item in issues_project_assigned:
            if not (item.assign.username in progress_dict['categories']):
                progress_dict['categories'].append(item.assign.username)
        progress_dict['categories'].append("未指派")

        for i in state_ch:
            test.append({"name":i[1],"data":[None for _ in range(len(progress_dict['categories']))]})

        for i in state_ch:
            progress_data = issues_project_assigned.filter(state=i[0]).values("assign__username").annotate(count=Count('id'))
            for item in progress_data:
                index = progress_dict['categories'].index(item['assign__username'])
                test[int(i[0])-1]['data'][index] = item['count']

            progress_data_notAssigned = issues_project_notAssigned.filter(state=i[0]).values("id").annotate(count=Count('id'))
            for item in progress_data_notAssigned:
                test[int(i[0])-1]['data'][-1] = item['count']
        progress_dict['series'] = test

        return JsonResponse({"status": True, "priority_data": priority_list, "progress_data": progress_dict})
