from core.notif.utils import ObjectFactory
from core.notif.onesignal_provider import OneSignalServiceBuilder
from core.notif.edx_provider import EdxServiceBuilder
from core.notif.cfg import Config, Provider


class PushServiceProvider(ObjectFactory):
    def get(self, service_id, **kwargs):
        return self.create(service_id, **kwargs)


factory = PushServiceProvider()
factory.register_builder(Provider.ONESIGNAL, OneSignalServiceBuilder())
factory.register_builder(Provider.EDX, EdxServiceBuilder())
