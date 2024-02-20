from django.http import JsonResponse
from django.shortcuts import render

def statistics(request, pro_id):


    return render(request, "statistics.html")


