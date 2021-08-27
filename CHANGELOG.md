Changelog
===

Versions follows PEP440 version scheme.
---

gamma-core 3.1 (2021-08-27)
---
* ad603fe feat: implement pluggable notification for edx
* 3417029 docs: fix typo in README
* 898c645 feat: add description to badges models

gamma-core 3.0.1 (2020-12-01)
---
* 6278fd0 Fix AppClient rewriting issue

gamma-core 3.0.0 (2020-10-06)
---
* f79801e Fix relative urls storing settings
* e4ac1a1 Fix filter.interval undefined issue
* 58cb93c celery[redis]==4.3.0. Pinned dependency vine==1.3.0.
* f9ad8e0 [RGG-443][RGG-444] Store URLs as relative by default
* 4a1701e [RGG-412] Fix interval filter dates representation at admin form is shifted due to user timezone

gamma-core 2.0.0 (2020-07-20)
---

Implements GEP-006+Move+data+to+MongoDB

* 640d4c2 Update docker-compose configuration for prod.yml
* 12f56e9 [RGG-395] Change color for readonly fields
* ab42864 Notify on recalculation, fix granting logic
* 96c2e25 [RGG-404] Make status_points required for StatusBadge and greater than 0
* 6b57f8e [RGG-206] Fix interval filter time
* d97405c [RGG-387] Deny status slug changing
* 138f6c3 Add system events info within game profile data
* 02c3bc9 [RGG-327] Change Frequency Filter logicq
* 5cb2bdc [RGG-365] Add Event title to the GameProfile API response
* 3cca061 [RGG-344] Deny deletion if badge/status is dependency for other badge
* cabed11 Refactor db.badges, core.tasks, core.utils
* 9e5ab26 [RGG-329] Fix badge recreated with same slug as was deleted stay unactive
* ecbf62e Refactor db/utils.py, add logging
* fb4a874 [RGG-343] Fix badges granting by status requirement
* 1eb4bac Fix Leaderboard API response
* 6dc6a57 Fix Badges activation/deactivation logic
* 66f806f [RGG-329] Make badges and statuses inactive on delete
* 76886db Add sentry integration for Django and Celery
* 566ac8e Save title for user badge status, remove redundant field
* 4e48787 [RGG-310] fix user statues at leaderboard api at refactoring branch
* 0fef21a Remove all user APIs except game profile, rewrite db module
* 07f2b9d [RGG-180, RGG-189] Apply push notifications for new Badge or Status achievement
* c4faa77 Basic implementation of Provider Builders
* 11e71e4 Use null as an empty values, delete null values from filter
* 41eabc5 RGG-281: Add leaderboard's API endpoint tests
* 72a7d50 Change progress year to datetime type
* 126bd99 Use traefik in the dev deployment scheme
* bda1fc8 Fixed for Statuses, leaderboard
* ad065d4 Add traefik and nginx to dev and deployment scheme
* ebe645c Refactor application
