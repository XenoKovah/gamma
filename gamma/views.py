from django.views.generic import TemplateView

from core.mixins import AdminPermissionMixin


class GammaView(AdminPermissionMixin, TemplateView):
    """
    View for rendering the Gamma React application.

    This Django view returns an HTML template that loads
    the Gamma React application. It does not handle any
    data processing; it simply serves the static template.

    Attributes:
        template_name (str): The path to the template containing the React application.
    """

    template_name = 'gamma-app/gamma.html'
