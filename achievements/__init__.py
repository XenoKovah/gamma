# coding:utf-8

from __future__ import unicode_literals
from django.apps import AppConfig


class MyAppConfig(AppConfig):
    name = 'achievements'
    verbose_name = "Gamification Administration"

default_app_config = 'achievements.MyAppConfig'