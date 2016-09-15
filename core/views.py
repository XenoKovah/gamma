from django.shortcuts import render
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin

from .utils import MongoConnector


class DashboardView(View):
    """
    Provide base information for user.
    """
    conn = MongoConnector()

    def get(self, request):
        user_achievements = None
        progress_data = self.conn.get_progress(request.user)
        if request.user.is_authenticated():
            user_achievements = request.user.userachievement_set.select_related('achievement').all()
        return render(request, 'dashboard.html', {
            'progress_data': progress_data,
            'user_achievements': user_achievements
        })
