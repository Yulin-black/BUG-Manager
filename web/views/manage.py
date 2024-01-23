from django.http import JsonResponse
from django.shortcuts import render


def dashboard(request, pro_id):
    # return JsonResponse({"status":True,"pro_id":pro_id})
    return render(request, "dashboard.html")

def issues(request, pro_id):
    return render(request, "issues.html")


def statistics(request, pro_id):
    return render(request, "statistics.html")


def setting(request, pro_id):
    return render(request, "setting.html")