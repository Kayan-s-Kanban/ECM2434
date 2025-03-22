from django.core.exceptions import PermissionDenied

def gamekeeper_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_gamekeeper:
            raise PermissionDenied("You are not authorized to view this page.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view
