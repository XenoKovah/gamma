from django.views.generic import TemplateView


class AvatarView(TemplateView):
    template_name = 'avatar-app/avatar.html'
