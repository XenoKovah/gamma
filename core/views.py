from django.shortcuts import render
from django.views.generic import View
from django.contrib.auth import logout
from django.http import HttpResponseRedirect

from .services import MongoConnector
from .models import GameProfile


def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')


class DashboardView(View):
    """
    Provide base information for user.
    """
    conn = MongoConnector()

    def get(self, request):
        user_achievements, progress_data, charted_progress = None, None, None
        if request.user.is_authenticated:
            progress_data = self.conn.get_progress(request.user)
            data = self.conn.get_charted_progress(request.user)
            if data:
                charted_progress = [[_type, points] for _type, points in data.items()]
            user_achievements = request.user.userachievement_set.select_related('achievement').all()
        return render(request, 'dashboard_new.html', {
            'progress_data': progress_data,
            'charted_progress': charted_progress,
            'user_achievements': user_achievements
        })


class AdminPanelView(View):

    def get(self, request):
        if request.user.is_authenticated and request.user.is_superuser:
            return render(request, 'admin_panel.html', {})


class LeaderBoardView(View):
    """
    Render top 100 users.
    """
    def get(self, request):
        top = [
            _id
            for i in GameProfile.objects.order_by('-points')[:100].values_list('id')
            for _id in i
        ]
        try:
            rank = top.index(request.user.gameprofile.id) + 1
        except ValueError:
            pass
        data = GameProfile.objects.order_by('-points')
        return render(request, 'leaderboard.html', {
            'data': data,
            'top': top,
            'rank': rank,
        })
