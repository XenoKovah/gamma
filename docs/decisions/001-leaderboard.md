# Leaderboard

## Background
The system has 2 leaderboard types: general leaderboard that contains user 
progress across the entire system and course-wide leaderboard that contains
user progress data for a specific course. Each leaderboard type has a 
separation by signup source, so the user can see the leaderboard members with
the same signup source. A leaderboard contains information about its top 
members, a user rank, his competitors, point count and badges related to
the leaderboard type.

## Solution
The points earned by a user as stored in RDBMS that is managed by Django 
ORM. General user progress persists in `users.models.GammaUser` model's
`points` field, while points earned for the course activities are stored in
`GammaUserCoursePoints`'s `points` field.

While it's a good solution for persistent data storing, it's inefficient to 
provide a personalized user leaderboard in real-time, so it was decided to 
use Redis's Sorted Set for this purpose.

For general leaderboards, all signup source-specific leaderboard data is placed
by `leaderboard:<user_signup_source>` cache key pattern, the course-wide 
leaderboards use `leaderboard:<user_signup_source>:<course_id>` pattern.
So, even leaderboards of the same type are stored by different cache keys 
based on the use cases they can be accessed, so no additional filtration is 
required during the data accessing.

### Leaderboards initialization
`initialize_leaderboard` management command was created to collect the user 
progress data and define corresponding user scores. It splits the entire user 
set into chunks (their size is controlled by 
`LEADERBOARD_INITIALIZATION_BATCH_SIZE` setting) and process their score 
initialization separately in a Celery task. To understand whether the 
initialization state (not started, in progress, completed), the 
`leaderboards_initialization_batches_left` Redis cache key is introduced.
Before batches processing starts, its value is set to batches count. At the end
of each batch processing, the value is decremented. So, we can determine the 
state based on the `leaderboards_initialization_batches_left` value:
- is not set: the leaderboards initialization is not started;
- 0 < x <= batches count: in progress;
- 0: completed.

If for any reason, this cache value is in inconsistent state (e.g., because of a
batch initialization task failure or a Redis connection failure), you can run
`reset_leaderboards_initialization_status` management command to reset it and
run an initialization command again.

#### Auto-recovery
`AutoRecoverLeaderboardsUseCase` runs before every leaderboard update cycle
(every minute). It detects two failure scenarios:
- **NOT_STARTED** — Redis was restarted or initialization was never run.
- **Stuck IN_PROGRESS** — a batch task failed and the counter never reached 0.
  Considered stuck after `LEADERBOARDS_INITIALIZATION_TIMEOUT_SECONDS` (default
  10 minutes) since the `leaderboards_initialization_started_at` timestamp.

In both cases it resets the initialization status and schedules a fresh
initialization automatically, without manual intervention.

### Leaderboards update
During the work on the course, students progress is updated, so cached
leaderboards must be rebuilt. It would be inefficient to update them after
each progress update event, so the Celery task that performs the recalculation
for users whose points were updated are run by Celery Beat (by default, once
per minute, but it can be configured by `CELERY_BEAT_SCHEDULE` setting).
The usernames of the users with updated progress are stored in Redis set with
`pending_leaderboard_update` cache key, so the task takes from it, update
leaderboard scores and empties the set.
Leaderboards update is not run if leaderboards initialization was not completed.

#### Resilient enqueue
The `pre_save` signal on `GammaUser` dispatches a Celery task to add the user
to the pending update set. If the Celery `.delay()` call fails (e.g. transient
broker connection issue), a fallback writes directly to the Redis pending set
via `RedisLeaderboardsPendingUpdateRepository.schedule_user_leaderboards_update`.
Both the primary and fallback failures are logged and swallowed so the Django
request is never broken by a leaderboard enqueue error.

#### Periodic reconciliation
As a safety net, `task_reconcile_leaderboards` runs hourly (configurable via
`CELERY_BEAT_SCHEDULE`). It iterates all `GammaUser` records in batches and
compares each user's DB points with their Redis general leaderboard score. Any
mismatch (wrong score or user missing from Redis) causes the user to be added
to the pending update set, so the next minute-level update cycle corrects it.
This guarantees that even if both the Celery enqueue and the direct Redis
fallback fail (e.g. Redis is temporarily down), stale data self-heals within
at most one hour.
