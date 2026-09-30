from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from django.contrib import messages

def admin_required(function):
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.user_type in ['admin', 'librarian']:
            return function(request, *args, **kwargs)
        messages.error(request, "You don't have permission to access this page.")
        return redirect('core:dashboard')
    return wrap

def member_required(function):
    def wrap(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.user_type == 'member':
            return function(request, *args, **kwargs)
        messages.error(request, "You don't have permission to access this page.")
        return redirect('core:dashboard')
    return wrap