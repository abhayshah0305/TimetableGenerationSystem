from __future__ import unicode_literals

from django.apps import AppConfig
from .chatbot import start_chatbot_engine


class DjangoChatBotConfig(AppConfig):
    name = 'django.chatbot'

    def ready(self):
        start_chatbot_engine()
