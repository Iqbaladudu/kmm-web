from django.shortcuts import redirect
from django.urls import reverse
import logging

logger = logging.getLogger('data_management.middleware')

class AuthRedirectMiddleware:
    """Redirect authenticated users away from login/registration endpoints.

    Rules:
      - Auth student hitting '/', '/staff/', '/register/' -> /dashboard/profile/
      - Auth staff (or in data_management_staff group) hitting '/', '/staff/', '/register/' -> /dashboard/
    Only applies to safe (GET/HEAD) requests.
    Logs each redirect action.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method in ('GET','HEAD') and request.user.is_authenticated:
            path = request.path
            if path in ('/','/staff/','/register/'):
                is_staff = request.user.is_staff or request.user.groups.filter(name="data_management_staff").exists()
                target_name = 'dashboard' if is_staff else 'profile'
                target_path = reverse(target_name)
                logger.info(
                    "[AuthRedirectMiddleware] redirect user=%s staff=%s from=%s to=%s",
                    request.user.username, is_staff, path, target_path
                )
                return redirect(target_name)
        return self.get_response(request)
