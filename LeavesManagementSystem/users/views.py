from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_view
from django.core.exceptions import PermissionDenied
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse


@login_required
def logout(request):
    """
    Add logout message and call auth_view.logout-then-login

    :request:
    """

    messages.success(request, 'You have been logged out successfully!')
    return auth_view.logout_then_login(request, login_url=reverse('login'))

@login_required
def login_success(request):
    """
    Check logged-in user permissions and redirect accordingly
    
    :request:
    """

    if request.user.has_perm('leaves.request_leave'):
        return HttpResponseRedirect(reverse('applied-leaves-list'))

    if request.user.has_perm('leaves.view_leave_requests'):
        return HttpResponseRedirect(reverse('leave-requests'))

    return PermissionDenied()
