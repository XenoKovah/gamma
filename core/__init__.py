from os import environ
from core.notif import push
from core.notif.cfg import Config, Provider

from core import db

cfg = {
    Config.ONE_SIGNAL_APP_AUTH_KEY: environ.get("ONE_SIGNAL_APP_AUTH_KEY"),
    Config.ONE_SIGNAL_APP_ID: environ.get("ONE_SIGNAL_APP_ID"),
    Config.EDX_API_KEY: environ.get("EDX_API_KEY"),
}


onesignal_provider = push.factory.get(Provider.ONESIGNAL, **cfg)
edx_provider       = push.factory.get(Provider.EDX, **cfg)
