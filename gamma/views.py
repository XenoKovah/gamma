from urllib.parse import urlsplit, urlunsplit

from django.conf import settings
from django.views.generic import TemplateView

from core.mixins import AdminPermissionMixin


class GammaView(AdminPermissionMixin, TemplateView):
    """
    View for rendering the Gamma React application.

    This Django view returns an HTML template that loads the Gamma React
    application. It injects a small ``gamma_header_config`` blob (current
    user + the LMS/MFE base URLs and logo) so the standalone React header
    can render the OST2 logo and the per-user navigation dropdown that the
    rest of the platform shows -- the app itself only knows
    ``window.location.origin`` (the gamma host), so these cross-host values
    must come from the backend.

    Attributes:
        template_name (str): The path to the template containing the React application.
    """

    template_name = 'gamma-app/gamma.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Browser-facing LMS root (e.g. https://dev.ost2.fyi). EDX_LMS_BASE_URL is
        # the in-cluster http://lms:8000 and is NOT usable from the browser.
        lms_base_url = settings.SOCIAL_AUTH_EDX_OAUTH2_URL_ROOT
        # The platform MFEs live on apps.<lms_host> by tutor convention (the same
        # host-prefix scheme that puts gamma on gamma.<lms_host>).
        parts = urlsplit(lms_base_url)
        mfe_base_url = urlunsplit((parts.scheme, f'apps.{parts.netloc}', '', '', ''))

        user = self.request.user
        # gamma authenticates via OAuth/social-auth against the LMS and stores its own
        # local auth user, whose ``username`` social-auth may have collision-suffixed
        # (e.g. the LMS "Xeno" becomes "Xeno89ed5e48c5354abc"). Prefer the social-auth
        # UID -- the upstream LMS username -- which is what the platform header shows and
        # what the public-profile URL (/profile/u/<username>) expects. Fall back to the
        # local username when there is no social-auth record (e.g. a direct superuser).
        social = user.social_auth.first() if hasattr(user, 'social_auth') else None
        lms_username = social.uid if (social and social.uid) else user.username
        context['gamma_header_config'] = {
            'username': lms_username,
            'name': user.get_full_name() or lms_username,
            'lmsBaseUrl': lms_base_url,
            'mfeBaseUrl': mfe_base_url,
            'logoUrl': f'{lms_base_url}/theming/asset/images/logo.png',
        }
        return context
