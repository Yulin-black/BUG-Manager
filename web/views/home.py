from django.shortcuts import render


def index(request):
    from django.conf import settings
    print("token",request.COOKIES.get(settings.SESSION_COOKIE_NAME))

    return render(request, "index.html",)

def error_404(request):
    return render(request, "404.html")