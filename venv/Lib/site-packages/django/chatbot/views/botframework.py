from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from background_task import background
from django.conf import settings
from ..chatbot import chat
import requests
import datetime
import json


def respond(service_url, reply_to_id, from_data,
            recipient_data, message, message_type, conversation):
    if settings.APP_CLIENT_ID != "<Microsoft App ID>":
        url = "https://login.microsoftonline.com/common/oauth2/v2.0/token"
        data = {
            "grant_type": "client_credentials",
            "client_id": settings.APP_CLIENT_ID,
            "client_secret": settings.APP_CLIENT_SECRET,
            "scope": "https://api.botframework.com/.default"
        }
        response = requests.post(url, data)
        response_data = response.json()
        headers = {
            "Authorization": "%s %s" % (response_data["token_type"], response_data["access_token"])
        }
    else:
        headers = {}
    if service_url[-1] != "/":
        service_url += "/"
    response_url = service_url + "v3/conversations/%s/activities/%s" % (conversation["id"], reply_to_id)
    requests.post(
        response_url,
        json={
            "type": message_type,
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f%zZ"),
            "from": from_data,
            "conversation": conversation,
            "recipient": recipient_data,
            "text": message,
            "replyToId": reply_to_id
        },
        headers=headers
    )


@background(schedule=1)
def initiate_conversation(data):
    conversation_id = data["id"]
    sender_id = data["conversation"]["id"]
    message = chat.start_new_session(sender_id)
    respond(data["serviceUrl"],
            conversation_id,
            data["recipient"],
            {"id": sender_id},
            message,
            "message",
            data["conversation"])


@background(schedule=1)
def respond_to_client(data):
    conversation_id = data["id"]
    message = data["text"]
    sender_id = data["conversation"]["id"]
    result = chat.respond(message, session_id=sender_id)
    respond(
        data["serviceUrl"],
        conversation_id,
        data["recipient"],
        data["from"],
        result,
        "message",
        data["conversation"]
    )
    del chat.attr[sender_id]


def conversation_handler(request):
    data = json.loads(request.body)
    # Send text message
    if data["type"] == "conversationUpdate":
        initiate_conversation(data)
    if data["type"] == "message":
        respond_to_client(data)
    return HttpResponse("It's working")


@csrf_exempt
def web_hook(request):
    if request.method == "POST":
        return conversation_handler(request)
    return HttpResponse("Invalid request method")
