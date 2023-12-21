from django.shortcuts import render




def project_list(request):
    """ 项目列表 """
    print(request.user.user.username)
    print(request.user.price_policy.title)
    return render(request, "project_list.html")
