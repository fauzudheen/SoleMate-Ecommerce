
def admin_username(request):
    user = request.user
    if user.is_superuser:
        admin_username = user.username
    else:
        admin_username = None
    return {'admin_username': admin_username}
