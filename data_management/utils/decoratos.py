# utils/decorators.py
from django.http import HttpResponseForbidden
from functools import wraps

def group_required(group_name):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return HttpResponseForbidden("You are not authenticated")
            if not request.user.groups.filter(name=group_name).exists():
                return HttpResponseForbidden(f"You must be in the {group_name} group")
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator