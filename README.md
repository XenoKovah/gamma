GAMMA - Gamification for OpenEdx.
===

GAMMA is a microservice for gamification.
We provide REST API to work with users coins,
manage Badges or Achievements.


Usage
===
For local development
---

Set up `.env` variables. Copy content of the `private.local.example.env` into `private.env` (`<devstack root>/gamma/envs/private.env`). Note that `LOCAL_IP_ADDRESS` can be found using shell command `ifconfig en0` right after `inet` keyword.

Install Gamma application. Note that the Node.js supported version is 12.

```
# Build cloned Gamma repo:
✗ npm install
✗ npm run build:dev
✗ make build

# To run gamma use:
✗ make debug

# You'll need to create a superuser to access the gamma admin site:
✗ make shell
✗ python manage.py createsuperuser
```
Optionally we can use
```
✗ make dev.up env=dev
```

Install [edx-gamma-bridge](https://gitlab.raccoongang.com/products/rg-gamification/gamification-bridge)
and [edx-gamma-dashboard](https://gitlab.raccoongang.com/products/rg-gamification/edx-gamma-dashboard) to the **edx-platform**.

```
# Go to the <devstack root>/src (sibling to the devstack repository)
cd src
git clone https://gitlab.raccoongang.com/products/rg-gamification/gamification-bridge.git
git clone https://gitlab.raccoongang.com/products/rg-gamification/edx-gamma-dashboard.git
cd ../devstack
make lms-shell
pip install -e /edx/src/edx-gamme-bridge
pip install -e /edx/src/edx-gamma-dashboard
exit # exit lms-shell. CTRL + D works as well
make studio-shell
pip install -e /edx/src/edx-gamme-bridge
pip install -e /edx/src/edx-gamma-dashboard
exit # exit lms-shell. CTRL + D works as well
make lms-restart
make studio-restart
```

Gamification settings should be added to the `edx-platform`.

1. Log into the http://0.0.0.0:9000/admin/#/
2. Add new `App client` http://0.0.0.0:9000/admin/core/appclient/add/#/
3. Further settings will use `key` and `secret` from the created `App client`
#### Next step works for Nutmeg only. Use `lms.yml` and `cms.yml` files from `/edx/etc/` inside the container for older edx releases.
4. Go to the `edx-platform/lms/envs/devstack-experimental.yml`
5. Add the following settings.
Note that `LOCAL_IP_ADDRESS` can be found using shell command `ifconfig en0` right after `inet` keyword.

```yml
FEATURES:
    ...
    RG_GAMIFICATION:
        ENABLED: true
        RG_GAMIFICATION_ENDPOINT: http://<LOCAL_IP_ADDRESS>:9000/
        KEY: key
        SECRET: secret
        IGNORED_EVENT_TYPES: []
```
6. The same for the `edx-platform/cms/envs/devstack-experimental.yml`
7. Restart `lms` and `studio` (`make lms-restart && make studio-restart`)

For staging/production usage
---
```
✗ make build
✗ make dev.up env=prod
```

Configuration
===
For docker-compose deployment `env/private.env` file can changed to pass sensitive data into container.
Following sections can be edited to add any sensitive data:

```
# Celery
CELERY_BROKER_URL=amqp://guest@rabbit
CELERY_RESULT_BACKEND=redis://redis:6379

# DB
DB_ENGINE=django.db.backends.postgresql
DB_NAME=postgres
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=postgres
DB_PORT=5432

# Django
# For devstack use DJANGO_SETTINGS_MODULE=gamma.settings.devstack
DJANGO_SETTINGS_MODULE=gamma.settings.production

# React
# Optional react backend base url
# For local deployment we can use REACT_APP_LOCALHOST=http://0.0.0.0:9000
REACT_APP_LOCALHOST=

# EDX integrarion
EDX_LMS_BASE_URL=<edx_lms_base_url>
# For local deployment the default setting is EDX_API_KEY="PUT_YOUR_API_KEY_HERE"
EDX_API_KEY=<edx_api_key>
```

### For local installation:

IP address in the EDX_LMS_BASE_URL setting must be your private IP address. You can find how to get your private IP 
here: https://www.avg.com/en/signal/find-ip-address. For example, the value may be http://192.168.140.191:18000.  
Note that the private ip can be changed because it is issued by a router, so it will be necessary to change this setting
in the future.

Run loadtests
---

1. export all needed env variables:
```
export APP_KEY=****************
export APP_SECRET=****************
export EVENT_TYPE=edx_bookmark_added
```

2. Create virtualenv
```
mkvirtualenv gamma --python=python3.8
pip install -r requirements/test.txt
```

Currently only one event type is supported.

3. Run locust
```
locust --host=http://localhost:9000 -f loadtests/locustfile.py
```

or use Makefile

```
make loadtests
```

4. Open url http://localhost:8089

5. Start tests


Run Python tests for Local Development
---

It is possible to run Python tests in `rgg` container. This is quite convenient for local development.

1. Enter `rgg` container bash:
```
tutor dev exec rgg bash
```
2. Make sure all test `requirements` are installed:
```
pip install -r requirements/test.txt
```
3. Setup test `DJANGO_SETTINGS_MODULE`:
```
export DJANGO_SETTINGS_MODULE=gamma.settings.test
```
4. Now you can run tests:
```
pytest .
pytest <application name>
pytest users/tests/test_models.py
```

# Badge and Avatar Achievement Configuration in Gamification Service

The gamification service tracks user activities and rewards them with achievements such as **badges** and **avatars**. This document describes the setup process for enabling achievements based on tracked events. Below are admin models for managing the creation and configuration of achievements for following rules generated by events.

---

## 1. Event Types

**Reference:** [Tracking Logs - edX Documentation](https://edx.readthedocs.io/projects/devdata/en/stable/internal_data_formats/tracking_logs.html)

Event types define the actions that the gamma microservice can process.

### Fields:
- `name` - The name of the event type.

**Example:**
- `stop_video` - Triggered when the video player reaches the end and stops automatically.

### Important Note

**Event names generated by the platform are converted on the `gamification-bridge` side.**
Dots (`.`) are replaced with underscores (`_`).

**Example:**
- `edx.bookmark.added` -> `edx_bookmark_added`
- `edx.course.enrollment.activated` -> `edx_course_enrollment_activated`

When defining event names, **always use underscores (`_`) instead of dots (`.`)** to ensure proper processing.

---

## 2. Event Configurations

Event configurations define how events are handled in the system.

### Fields:
- `event_type` - The associated event type.
- `title` - A human-readable name for the event configuration.
- `is_depends_on_achievement` - (use only for dependend) If enabled, marks this event as dependent on an achievement.
- `content_type` - (use only for dependend) Specifies the related object type. Uses only for dependent event (e.g., **badge** or **avatar**).
- `points_to_award` - Points granted when the event occurs.

---

## 3. Rules

Rules determine how users can earn achievements.

### Fields:
- `event_configurations` - The linked event configurations.
- `action` - The rule logic, defined in JSON format.

### Examples:

#### 3.1. Repeated Action Rule
The user must trigger an event a specified number of times.
```
{
    "stop_video": 2
}
```

This means the user must stop a video twice to meet the rule's criteria.

#### 3.2. Rule with Dependency on Dependent Object

To create a rule where obtaining a new achievement requires a prior dependent object:
```
{
    "rgg.badge.achieved": 5
}
```

Here, the user must already have an achievement of the specified content type (set in step 2, in this case **badge**) with the given ID.

#### 3.3 Filters

Filters can be applied to refine rule conditions:
```
{
  "interval": {
    "start": "2025-02-07T12:38:25",
    "end": "2025-02-07T12:38:25"
  },
  "org": "edx",
  "frequency": 2,
  "course": "course-v1:test+0001+0001"
}
```

## 4. Badges & Avatars

Badges and avatars represent achievements(badges & avatars) within the system.

### Fields:
- **title** - The name of the achievement.
- **description** - A short explanation of the achievement.
- **image** - Associated image.
- **is_active** - Status indicator.
- **slug** - A unique identifier.
- **rules** - Linked rules defining how the achievement is earned.

---

## 5. Events (Auto-generated)

The gamification microservice stores processed events, including user data, course details, and event context.

### Process:
- Events are triggered by `edx-platform` and sent via `gamification-bridge` - tracking event listener.
- Events are then forwarded to the `gamma` using `EventsAPIView` endpoint for processing.

---

## 6. Achievements (Auto-generated)

Achievements store the relationship between users and the badges/avatars they have earned. They are created automatically during generating an event. The corresponding rules are processed, and if they are fulfilled, this affects the corresponding achievements.

### Fields:
- **user** - The recipient of the achievement.
- **content_type** - The type of achievement (badge/avatar).
- **object_id** - The associated achievement ID.
- **title** - The achievement's name.
- **description** - A short explanation of the achievement.
- **rule** - The rule that was satisfied to earn this achievement.

---

## 7. Example of an Achievement Award

This section provides an example of how a user can progress through **avatar achievements** by meeting specific conditions.

---

### 7.1 Avatar Achievement Progression

Each avatar level requires users to fulfill certain conditions before they can unlock the next level.

---

#### 7.1.1 Rules for Avatar Level 1

To earn **Avatar Level 1**, the following rule applies when creating the avatar object:


```
{
    "edx_course_enrollment_activated": 1, # The user must enroll in a course once to receive the first avatar.
}
```
---

#### 7.1.2 Rules for Avatar Level 2

To unlock **Avatar Level 2**, the user must already possess **Avatar Level 1** and fulfill an additional condition:


```
{
    "rgg.avatar.achieved": 1, # The user must already have Avatar Level 1 (ID 1 from the Avatars model).
    "edx_bookmark_added": 5, # The user must add 5 bookmarks.
}
```

#### 7.1.3 Rules for Avatar Level 3

To unlock **Avatar Level 3**, the user must already possess **Avatar Level 2** and meet an additional requirement:
```
{
    "rgg.avatar.achieved": 2, # The user must already have Avatar Level 2 (ID 2 from the Avatars model).
    "edx_forum_comment_created": 5, # The user must create 5 forum comments.
}
```

### 7.2 Achievement Generation Process

Once a user enrolls in a course, they receive **Avatar Level 1** based on the rule in **7.1.1**.

1. **Achievement Record Creation**:  
   - Upon meeting the conditions, an entry is created in the **Achievements model**.
   - The system verifies whether the user has fulfilled the rules before awarding the achievement.

2. **Progression to Higher Levels**:  
   - Once the first avatar is awarded, the user can work towards **Avatar Level 2** and **Avatar Level 3** by fulfilling the respective conditions.
   - Each subsequent level follows the same logic:  
     - The user must possess the previous avatar.
     - The required actions (bookmarks, forum comments, etc.) must be completed.

3. **Continuous Strategy**:  
   - The process repeats as the user advances through different avatar levels.
   - The system ensures achievements are granted only when all defined rules are satisfied.
