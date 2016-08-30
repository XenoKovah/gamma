from django.shortcuts import render
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin

from .utils import get_progress


class DashboardView(View):
    """
    Provide base information for user.
    """
    def get(self, request):
        progress_data = get_progress(request.user)
        return render(request, 'dashboard.html', {'progress_data': progress_data})
