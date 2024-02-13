from django.shortcuts import redirect
from django.urls import reverse

class SuperuserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        if request.user.is_authenticated and not request.user.is_superuser:
            if request.path.startswith('/admin-'):
                return redirect('AdminHome:login')

        return response