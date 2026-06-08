Changelog
=========

Versions follows PEP440 version scheme.

[Unreleased]
************

## Added
* feat: Add `leaderboard/badge/<slug>` API returning the top-100 users who earned a badge (ranked by points) in leaderboard-member shape, plus the badge's display data, for the dashboard's per-badge leaderboard page
* feat: The `leaderboard/badge/<slug>` API also returns an `in_progress` list — users with non-zero progress toward the badge who have not completed it, ranked by their computed progress percentage — for the per-badge page's "In progress" section


release/teak.2 (2026-05-22)
---

## Fixed
* fix: [TEA-176] Avatar for user is not available after completing task
* fix: Leaderboard is not updated with points

release/teak.1 (2025-06-11)
---
Also tagged as `release/teak-rc.1` (identical content).

## Added
* feat: [NAU-534] Corrected rules validation
* feat: [NAU-541] Setup logging (local + on environment)
* feat: [NAU-521] Create data migration for edX common events
* feat: [NAU-530] Performance page doesn't render with failed achievements
* feat: [NAU-457] Changed logout url for Gamma settings header
* feat: [NAU-457] Implement permissions
* feat: [NAU-465] Extend rules with new actions
* feat: [NAU-449] Extend rules with new actions
* feat: [NAU-432] Implement internal events management commands
* feat: [NAU-320] Added deletion confirmation modal for evolution step
* feat: [NAU-419] SSO with edX is set up
* feat: [NAU-315] Added close button for Avatar stepper
* feat: [NAU-356] get Points and Charts form MySQL
* feat: [NAU-396] Leaderboards initialization is improved
* feat: [NAU-368] Changed slug behavior inside Manage entity modal
* feat: [NAU-404] Course leaderboard implementation
* feat: [NAU-397] Apply s2s requests for Avatars Config
* feat: [NAU-340] Updated achievements serializer
* feat: [NAU-388] Gamma user score by course persisting is implemented
* feat: [NAU-314] Added translations for Portuguese
* feat: [NAU-357] Leaderboard refactoring
* feat: [NAU-339] Receive badges from SQL
* feat: [NAU-329] Add avatars to game profile response
* feat: [NAU-312] Create new gamma-profile endpoint
* feat: improved display of student avatar
* feat: [NAU-293] Added event_configuration for Avatar rule
* feat: [NAU-286, NAU-286-290, NAU-286-287] Edit functional for Avatar set stepper
* feat: [NAU-285] Implement finish step in avatars setup
* feat: [NAU-347] Refactor previous event processing implementation
* feat: [NAU-284] Implement finish AvatarSet API
* feat: [NAU-276] Created Avatars stepper step
* feat: [NAU-275] Created Evolution stepper step
* feat: [NAU-274] Created Title stepper step
* feat: [NAU-257] Implement Avatar backend
* feat: [NAU-273] Connect Avatar sets API and implement deletion
* feat: [NAU-210] Edit badges modal
* feat: [NAU-258] Created base Avatars structure
* feat: [NAU-256] Implement Avatar API View
* feat: [NAU-255] Implement AvatarSet API
* feat: [NAU-250, NAU-251] Create API for actions and badge serializer refactoring
* feat: [NAU-209] Added rules form set, header and footer
* feat: [NAU-208] Added BadgeModal React component
* feat: [NAU-160] Added BadgesList React component
* feat: [NAU-207] Added generic React components
* feat: [NAU-204] Added Loader React component
* feat: [NAU-203] Added SubHeader React component
* feat: [NAU-195] Rules refactoring with updating
* feat: [NAU-199] Configured CI for React, translations for modules, Django routing
* feat: [NAU-194] Frontend application structure updating
* feat: [NAU-142] Rules refactoring
* feat: [NAU-143] Draft Avatar solution implementation
* feat: [NAU-150] Create API for events
* feat: Project skeleton is prepared for refactoring
* feat: [RGOeX-26916] add s3 requirements

## Fixed
* fix: [NAU-535, NAU-536, NAU-533] Correct calculation badges with points rule
* fix: achievement processing for users
* fix: [NAU-509] Fix getting last achieved avatar
* fix: event configuration issue
* fix: [NAU-376] Fixed image size validation
* fix: assign user avatar issue
* fix: change user config serializer
* fix: [NAU-289] Redirect broken links
* fix: [NAU-426] Handle non existent content type
* fix: [NAU-417] Badges list retrieving error is fixed
* fix: [NAU-332] Get rid of filters for avatar
* fix: [NAU-375] Fix rewriting badge images
* fix: [NAU-321, NAU-331] Fixed modal title, toast delay and some refactoring
* fix: [NAU-305] Fixed avatar duplication
* fix: update rules serializers with event configuration
* fix: [NAU-150] Migration is missing for events

## Maintenance
* refactor: [NAU-507] Repository cleanup
* test: [NAU-415] Rewrite tests for achievements processing
* chore: [NAU-474, NAU-472] Corrected Delete buttons on Avatar and Badges pages
* test: [NAU-465] User config is tested
* chore: [NAU-316] Added support text for avatar stepper
* chore: [NAU-336, NAU-366] Added UI/UX improvements and hasFilters for EntityRules component
* chore: [NAU-286, NAU-287, NAU-290] Corrected some tests and refactoring
* chore: [NAU-293] Replaced rule actions endpoint
* temp: student experience with avatars
* refactor: [NAU-264] Apply TDD for achievement processing
* refactor: [NAU-260] Fronted translations refactoring
* refactor: [NAU-253] Refactor Avatar models
* refactor: [NAU-159] Users app refactoring

## Docs
* docs: [NAU-365] Update technical documentation
* docs: [NAU-282] Document the logic of the achievements earning

gamma-core 3.6.1 (2023-08-20)
---

## Maintenance
* fix: pin the pip version to 24.0
* chore: update pytest and pytest plugins


gamma-core 3.6.0 (2023-11-09)
---

## Added
* feat!: [RGG-984] implement json_formating for RGG Notifications
* feat: add kind Notif atrribute

gamma-core 3.5.1 (2023-11-09)
---

## Maintenance
* build: add compose backward compatibility


gamma-core 3.5.0 (2023-11-02)
---

## Maintenance
* chore: Update to Django 3.2
* chore: update to Nodejs 14
* build: optimize docker build process
* !build: move to native docker compose
  * Doesn't work on pre-Palm deployments


## Fixed
* fix: [RGG-935] it's possible to set "End interval" date earlier than "Start interval"
* fix: [RGG-936] Interval filter breaks after clicking "CLEAR" on empty field
* fix: [RGG-908] Fix for custom selects in active state
* fix: dockerignore doesn't include .conf/ directory

gamma-core 3.4.0 (2023-06-08)
---
## Fixed
* fix: [RGG-915] Hotfix for leaderboard when the current user is duplicated in the top10
* fix: [RGG-677] fixed badge achievement dropdowns overflow

## Added
* feat: [RGG-870] Added validation for using "courses" and "organization" filters simultaneously
* feat: [RGG-644] Create python linting configuration
* feat: [RGG-867] Added an API for updating the signup_source field for game profiles
* feat: [RGG-805] Added filtering of game profiles for the leaderboard depending on the tenant

gamma-core 3.3.0 (2023-02-24)
---
Features
* feat: added Django console logging by Andrey Kryachko
* chore: [RGG-782] improve fields description

gamma-core 3.2.4 (2022-12-16)
---
Fixes
===
* fix: [RGG-670] Null value is removed from the Badge Achievement Dropdowns
* fix: [RGG-440] add more accurate selector to fix select max-height options list
* fix: [RGG-594] event title doesn't change
* fix: [RGG-591] dependence of the badge on itself
* fix: [RGG-591] badges cannot be configured with the pre-condition depend on itself
* fix: [RGG-593] reduce more max-height of the select dropdown element
* fix: [RGG-594] editing mode for the 1st achievement
* fix: [RGG-595] admin cannot delete status badge
* fix: [RGG-593] values in Event type dropdown in Editing rules for Achievement are not fit into the window
* fix: add permission class and redirect if error
* fix: use relative url for view on site
* 'Event Title' changes in the admin site immediately reflect in the user dashboard chart
* admin permissions are required to access Badge API
* View on site button in the admin panel on the StatusBadge edit page opens correct URL for image
* reduced height of the select dropdown 'Event type' in the 'Edit rules' popup

Docs
====
* docs: add local installation steps

gamma-core 3.2.3 (2022-08-08)
---
* build: [RGG-552] do not expose mongo container port

gamma-core 3.2.2 (2022-04-16)
---
* fix: [RGOeX-1121] use additional check for rules.filters
* fix: [RGOeX-1126|RGOeX-1127|RGOeX-1128] Update daily progress selection logic
* fix: [RGOeX-1072] Unicode support is added for relative urls in CustomURLType
* tests: [RGOeX-1126|RGOeX-1127|RGOeX-1128] add DailyProgress tests

gamma-core 3.2.1 (2022-04-08)
---
* fix:  [RGOeX-756] change update_progress query and increment logic
* fix:  [RGOeX-1025] add limit for achievement titles
* docs: [RGOeX-1004] update documentation for local installation
* fix:  [RGOeX-758] adjust frequency filter UI behaviour

gamma-core 3.2 (2021-10-18)
---
* 677d2de fix: [RGG-520] translation typo in achievements_list_new_ui.html
* e458a75 feat: Translations to chinese for Gamification
* e0ab186 fix: [harrow-695] added scroll to a select dropdowns

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
