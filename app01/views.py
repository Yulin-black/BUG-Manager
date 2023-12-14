from django.http import HttpResponse
from django.shortcuts import render
from SAAS.utils.email_send import send_email


def Send_eamil(request):

    data = send_email("1875916498@qq.com")

    return HttpResponse(data)