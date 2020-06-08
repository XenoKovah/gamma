import os
import uuid

from locust import TaskSet, task


class GameProfileTasks(TaskSet):
    """
    Emulate ral user experience.

    Scenario:
      - do action 10 times
      - read dashboard information 2 times
      - read leaderboard information 2 times
    """
    HEADERS = {"App-key": os.environ["APP_KEY"],
               "App-secret": os.environ["APP_SECRET"]}
    USER_UID = "locust"

    @task(weight=10)
    def post_event(self):
        self.client.put(
            "/api/v0/gamma-profile/",
            data={'username': self.USER_UID,
                  'uid': uuid.uuid4().__str__(),
                  "event_type": os.environ["EVENT_TYPE"]},
            headers=self.HEADERS)

    @task(weight=2)
    def read_dashboard(self):
        self.client.get(
            "/api/v0/gamma-profile/",
            params={'username': self.USER_UID},
            headers=self.HEADERS)
