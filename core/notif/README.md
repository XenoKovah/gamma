Usage
===


OneSignal Provider
---
```python
from core.notif import push
from core.notif.cfg import Config, Provider

from core import db


cfg = {
    Config.ONE_SIGNAL_APP_AUTH_KEY: "app_auth_key",
    Config.ONE_SIGNAL_APP_ID: "app_id",
    ...
}


onesignal_provider = push.factory.get(Provider.ONESIGNAL, **cfg)

user = db.users.read_one("username1")
badge = db.badges.read_one("badge_uid")

heading = "Message heading"
content = "Hello username"

data = {
    "head": heading,             # required
    "body": content,             # required
    "lang": "en",                # required
    "icon": badge.url,           # not required
    "url":  "http://localhost"   # not required
}


result = onesignal_provider.send_notif(user, data)
assert isinstance(result, dict)
```

Edx Provider
---
```python
from core.notif import push
from core.notif.cfg import Config, Provider

from core import db


cfg = {
    Config.EDX_API_KEY: environ.get("EDX_API_KEY"),
    ...
}


edx_provider       = push.factory.get(Provider.EDX, **cfg)

user = db.users.read_one("username1")
badge = db.badges.read_one("badge_uid")

heading = "Message heading"
content = "Hello username"

data = {
    "head": heading,             # required
    "body": content,             # required
    "lang": "en",                # not required
    "icon": badge.url,           # not required
    "url":  "http://localhost"   # not required
}


result = edx_provider.send_notif(user, data)
```


Deployment
===


Configure Edx Notifications API in private.env

```
EDX_LMS_BASE_URL=<edx_base_url>
EDX_API_KEY=<edx_api_key>

EDX_NOTIFICATION_API_SUFFIX=notifications/api/v0/send-notification/
EDX_NOTIFICATION_ENABLED=True
```
