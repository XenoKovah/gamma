from django.views.generic import TemplateView


class AvatarView(TemplateView):
    # TODO: In the future, this TemplateView, which returns the base template for the frontend/gamma React app,
    # will be moved to a separate Django app.
    template_name = 'gamma-app/gamma.html'
