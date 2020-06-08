from datetime import datetime

from django.shortcuts import render
from django.views.generic import View
from django.contrib.auth import logout
from django.http import HttpResponseRedirect

from core import db


def logout_view(request):
    logout(request)
    return HttpResponseRedirect('/')


class DashboardView(View):
    """
    Provide base information for user.
    """
    def get(self, request):
        progress_data, charted_progress = None, None
        if request.user.is_authenticated:
            user = db.users.read_one(request.user.username)
            progress_data = user.progress[str(datetime.now().year)] if user.progress else []
            data = db.users.read_one(request.user.username).chart
            if data:
                charted_progress = [[_type, points] for _type, points in data.items()]
        return render(request, 'dashboard.html', {
            'progress_data': progress_data,
            'charted_progress': charted_progress
        })
