

from django.contrib.auth import logout

class BlockMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user
        if not user.is_active:
            logout(request)
        return self.get_response(request)

