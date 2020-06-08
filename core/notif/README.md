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
badge = db.badges.read_one_as_ob("badge_uid")

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
