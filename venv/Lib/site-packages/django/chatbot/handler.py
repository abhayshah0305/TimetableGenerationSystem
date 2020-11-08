from chatbot import Chat
from .models import Conversation, Memory, Sender
from django.conf import settings
from django.db.utils import OperationalError, ProgrammingError


class UserMemory:

    def __init__(self, sender_id, *args, **kwargs):
        self.sender_id = sender_id
        self.update(*args, **kwargs)

    def __getitem__(self, key):
        try:
            return Memory.objects.get(sender__sender_id=self.sender_id,
                                      key__iexact=key).value
        except Memory.DoesNotExist:
            raise KeyError(key)

    def __setitem__(self, key, val):
        try:
            memory = Memory.objects.get(sender__sender_id=self.sender_id, key__iexact=key)
            memory.value = val
            memory.save()
        except Memory.DoesNotExist:
            sender = Sender.objects.get(sender_id=self.sender_id)
            Memory.objects.create(sender=sender, key=key.lower(), value=val)

    def update(self, *args, **kwargs):
        for k, v in dict(*args, **kwargs).items():
            self[k] = v
    
    def __delitem__(self, key):
        try:
            return Memory.objects.get(sender__sender_id=self.sender_id, key=key).delete()
        except Memory.DoesNotExist:
            raise KeyError(key)

    def __contains__(self, key):
        return Memory.objects.filter(sender__sender_id=self.sender_id, key=key)


class UserConversation:

    def __init__(self, sender_id, *args):
        self.sender_id = sender_id
        self.extend(list(*args))

    def get_sender(self):
        return Sender.objects.get(sender_id=self.sender_id)

    def get_conversation(self, index):
        try:
            conversations = Conversation.objects.filter(sender__sender_id=self.sender_id)
            if index < 0:
                index = -index - 1
                conversations = conversations.order_by('-id')
            return conversations[index]
        except:
            raise IndexError("list index out of range")

    def __getitem__(self, index):
        return self.get_conversation(index).message

    def __setitem__(self, index, message):
        conversation = self.get_conversation(index)
        conversation.message = message
        conversation.save()

    def extend(self, items):
        for item in items:
            self.append(item)
            
    def append(self, message):
        Conversation.objects.create(sender=self.get_sender(), message=message)
    
    def append_bot(self, message):
        Conversation.objects.create(sender=self.get_sender(),message=message,bot=True)
    
    def append_user(self, message):
        Conversation.objects.create(sender=self.get_sender(), message=message,
                                    bot=False)

    def __delitem__(self, index):
        self.get_conversation(index).delete()
        
    def pop(self):
        try:
            conversation = self.get_conversation(-1)
            message = conversation.message
            conversation.delete()
            return message
        except IndexError:
            raise IndexError("pop from empty list")

    def __contains__(self, message):
        return Conversation.objects.filter(sender__sender_id=self.sender_id,
                                           message=message)


class UserTopic:

    def __init__(self, *args, **kwargs):
        self.update(*args, **kwargs)

    def __getitem__(self, sender_id):
        try:
            sender = Sender.objects.get(sender_id=sender_id)
        except Sender.DoesNotExist:
            raise KeyError(sender_id)
        return sender.topic

    def __setitem__(self, sender_id, topic):
        try:
            sender = Sender.objects.get(sender_id=sender_id)
            sender.topic = topic
            sender.save()
        except Sender.DoesNotExist:
            Sender.objects.create(sender_id=sender_id, topic=topic)
    
    def update(self, *args, **kwargs):
        for k, v in dict(*args, **kwargs).items():
            self[k] = v
    
    def __delitem__(self, sender_id):
        try:
            return Sender.objects.get(sender_id=sender_id).delete()
        except Sender.DoesNotExist:
            raise KeyError(sender_id)
        
    def __contains__(self, sender_id):
        return Sender.objects.filter(sender_id=sender_id).count() > 0


class UserSession:

    def __init__(self, object_class, *args, **kwargs):
        self.objClass = object_class
        self.update(*args, **kwargs)

    def __getitem__(self, sender_id):
        try:

            return self.objClass(Sender.objects.get(sender_id=sender_id).sender_id)
        except:raise KeyError(sender_id)

    def __setitem__(self, sender_id, val):
        Sender.objects.get_or_create(sender_id=sender_id)
        self.objClass(sender_id, val)

    def update(self, *args, **kwargs):
        for k, v in dict(*args, **kwargs).items():
            self[k] = v
    
    def __delitem__(self, sender_id):
        try:
            return Sender.objects.get(sender_id=sender_id).delete()
        except:
            raise KeyError(sender_id)
        
    def __contains__(self, sender_id):
        return Sender.objects.filter(sender_id=sender_id).count() > 0


class MyChat(Chat):

    def __init__(self, *arg, **kwargs):
        super(MyChat, self).__init__(*arg, **kwargs)
        self._memory = UserSession(UserMemory, self._memory)
        self.conversation = UserSession(UserConversation, self.conversation)
        self.topic.topic = UserTopic(self.topic.topic)

    def respond(self, message, session_id):
        self.attr[session_id] = {
            'match': None,
            'pmatch': None,
            '_quote': False,
            'substitute': True
        }
        self.conversation[session_id].append_user(message)
        response = super().respond(message.rstrip(".! \n\t"),
                                   session_id=session_id)
        self.conversation[session_id].append_bot(response)
        del self.attr[session_id]
        return response
    
    def start_new_session(self, session_id, topic=""):
        super().start_new_session(session_id)
        start_message = getattr(settings, "START_MESSAGE", "Welcome to ChatBotAI")
        self.conversation[session_id].append_bot(start_message)
        return start_message


def initiate_chat(*arg, **kwargs):
    try:
        return MyChat(*arg, **kwargs)
    except (OperationalError, ProgrammingError):  # No DB exist
        print("No DB exist")
        return Chat(*arg, **kwargs)
