from django.contrib import admin
from .models import Sender, Conversation, Memory

admin.site.register(Sender)
admin.site.register(Conversation)
admin.site.register(Memory)
