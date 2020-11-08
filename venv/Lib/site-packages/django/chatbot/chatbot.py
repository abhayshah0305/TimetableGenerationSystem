from django.conf import settings


class __Chat:
    pass


chat = __Chat()


def start_chatbot_engine():
    from .handler import initiate_chat
    if hasattr(settings, "CHATBOT_TEMPLATE"):
        chat_obj = initiate_chat(settings.CHATBOT_TEMPLATE)
    else:
        chat_obj = initiate_chat()
    for attribute in dir(chat_obj):
        if attribute[0] != "_":
            setattr(chat, attribute, getattr(chat_obj, attribute))
