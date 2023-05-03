import re

from django.conf import settings
from schematics.types.net import URLType, URI_PATTERNS, IPv6Type


URI_PATTERNS["hostl"] = r"localhost:\d{2,5}"


class CustomURLType(URLType):
    """
    Current URLType doesn't validate http://localhost:9000 url.
    """

    if settings.DEBUG:
        # Rewrite URL_REGEX only for local development
        URL_REGEX = re.compile(r"""^(
                (?P<scheme> %(scheme)s ) ://
            (   (?P<user>   %(user)s   ) @   )?
            (\[ (?P<host6>  %(host6)s  ) ]
            | (?P<host4>  %(host4)s  )
            | (?P<hostl>  %(hostl)s  )
            | (?P<hostn>  %(hostn)s  )     )
            ( : (?P<port>   %(port)s   )     )?
                (?P<path> / %(path)s   )?
            (\? (?P<query>  %(query)s  )     )?
            (\# (?P<frag>   %(frag)s   )     )?)$
            """ % URI_PATTERNS, re.I + re.X)

    RELATIVE_URL_REGEX = re.compile(r"^\/[\.a-zA-Z0-9\-_]+(\/[\.a-zA-Z0-9\-_]+)*\/?$")

    def __init__(self, relative=False, **kwargs):
        self.relative = relative
        super().__init__(**kwargs)

    def _validate_absolute_url(self, value):  # pylint: disable=too-many-branches, too-many-return-statements
        """
        Override validation method to support local hostnames with a port.
        """
        match = self.URL_REGEX.match(value)
        if not match:
            return False
        url = match.groupdict()

        if url['scheme'].lower() not in self.schemes:
            return False
        if url['host6']:
            if IPv6Type.valid_ip(url['host6']):  # pylint: disable=no-else-return
                return url
            else:
                return False
        if url['host4']:
            return url

        if 'hostl' in url and url['hostl']:
            return url

        try:
            hostname = url['hostn'].encode('ascii').decode('ascii')
        except UnicodeError:
            try:
                hostname = url['hostn'].encode('idna').decode('ascii')
            except UnicodeError:
                return False

        if hostname[-1] == '.':
            hostname = hostname[:-1]
        if len(hostname) > 253:
            return False

        labels = hostname.split('.')
        for label in labels:
            if not 0 < len(label) < 64:
                return False
            if '-' in (label[0], label[-1]):
                return False
        if self.fqdn:
            if len(labels) == 1 or not self.TLD_REGEX.match(labels[-1]):
                return False

        url['hostn_enc'] = hostname

        return url

    def _validate_relative_url(self, value):
        match = self.RELATIVE_URL_REGEX.match(value)
        if not match:
            return False
        return value

    def valid_url(self, value):
        if self.relative:
            return self._validate_relative_url(value)
        return self._validate_absolute_url(value)
