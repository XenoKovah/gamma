from locust import HttpLocust, TaskSet, task, between

from game_profile import GameProfileTasks


class MyTaskSet(TaskSet):
    """
    game_profile.GmaProfileTasks: 100%
    """

    tasks = {
        GameProfileTasks: 1,
    }


class User(HttpLocust):
    task_set = MyTaskSet
    wait_time = between(30, 90)
