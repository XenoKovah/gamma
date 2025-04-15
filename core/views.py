from django.views.generic import View
from django.contrib.auth import logout
from django.http import HttpResponseForbidden, HttpResponseRedirect


def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/admin/')


class DashboardView(View):
    """
    Provide base information for user.
    """

    def get(self, request):
        if not request.user.is_authenticated:
            return HttpResponseForbidden('Authentication required to access this resource.')
        return HttpResponseRedirect('/gamma/avatars/')
