from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from ..chatbot import chat
from ..models import Conversation


@csrf_exempt
@login_required
def web_hook(request):
    sender_id = request.user.username
    last_message_id = None
    if sender_id not in chat.conversation:
        chat.start_new_session(sender_id)
    if request.method == "POST":
        message = request.POST.get("message")
        last_message_id = request.POST.get("last_message_id")
        if message:
            chat.respond(message, session_id=sender_id)
    msgs = Conversation.objects.filter(sender__sender_id=sender_id)
    if last_message_id:
        msgs = msgs.filter(id__gt=last_message_id)
    count = msgs.count()
    msgs = msgs.order_by("id")
    if count > 50:
        msgs = msgs[50:]
    return JsonResponse({
        "status": "Success",
        "messages": [{"id": msg.id,
                      "text": msg.message,
                      "created": msg.created.strftime('%Y-%m-%d %H:%M:%S'),
                      "by": "bot" if msg.bot else "user"
                      } for msg in msgs]
        })
