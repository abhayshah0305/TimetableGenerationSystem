import re
import sys
import time
import json
import urllib
import threading

import requests

__version__ = '1.5.2b'

class Event(object):
	def __init__(self, connection):
		self.connection = self.parse(connection)

	def parse(self, connection):
		returned = {}
		if connection["event"] == "join":
			connection["data"] = json.loads(connection["data"])
		elif connection["event"] != "disableReconnect":
			connection["data"] = json.loads(connection["data"])
		if connection["event"] == "kick":
			returned["user"] = [connection["data"]["attrs"]["kickedUserName"],
								connection["data"]["attrs"]["moderatorName"]]
			returned["text"] = None
			returned["status"] = None
			returned["time"] = None
			returned["madechatmod"] = False
		elif connection["event"] == "chat:add" and connection["data"]["attrs"].has_key("wfMsg"):
			returned["user"] = [connection["data"]["attrs"]["msgParams"][1],
								connection["data"]["attrs"]["msgParams"][0]]
			returned["text"] = None
			returned["status"] = None
			returned["time"] = None
			returned["madechatmod"] = True
		elif connection["event"] == "ban":
			returned["user"] = [connection["data"]["attrs"]["kickedUserName"],
								connection["data"]["attrs"]["moderatorName"]]
			returned["text"] = None
			returned["status"] = None
			returned["time"] = connection["data"]["attrs"]["time"]
			returned["madechatmod"] = False
		elif connection["event"] == "logout":
			returned["user"] = connection["data"]["attrs"]["name"]
			returned["text"] = None
			returned["status"] = None
			returned["time"] = None
			returned["madechatmod"] = False
		elif connection["event"] == "updateUser":
			returned["user"] = connection["data"]["attrs"]["name"]
			returned["text"] = None
			returned["status"] = connection["data"]["attrs"]["statusState"]
			returned["time"] = None
			returned["madechatmod"] = False
		elif connection["event"] == "join":
			returned["user"] = connection["data"]["attrs"]["name"]
			returned["text"] = None
			returned["status"] = "here"
			returned["time"] = None
			returned["madechatmod"] = False
		elif connection["event"] == "part":
			returned["user"] = connection["data"]["attrs"]["name"]
			returned["text"] = None
			returned["status"] = None
			returned["time"] = None
			returned ["madechatmod"] = False
		elif connection["event"] == "chat:add":
			returned["user"] = connection["data"]["attrs"]["name"]
			returned["text"] = connection["data"]["attrs"]["text"]
			returned["status"] = None
			returned["time"] = None
			returned["madechatmod"] = False
		else:
			returned["user"] = None
			returned["text"] = None
			returned["status"] = None
			returned["time"] = None
			returned["madechatmod"] = False
		return returned

	@property
	def user(self):
		if self.connection['user']:
			return self.connection["user"]
		else:
			return None

	@property
	def text(self):
		if self.connection['text']:
			return self.connection["text"]
		else:
			return None

	@property
	def status(self):
		if self.connection['status']:
			return self.connection["status"]
		else:
			return None

	@property
	def time(self):
		if self.connection['time']:
			return self.connection["time"]
		else:
			return None

	@property
	def made_chat_mod(self):
		if self.connection['madechatmod']:
			return self.connection["madechatmod"]
		else:
			return False

#class PrivateMessage(ChatBot):
#	def __init__(self, username, password):
#		ChatBot.__init__(self)
#		self.c = Client(username, password, wiki)
#		self.changed = False
#		self.message = ""
#
#	def send(self, message):
#		self.changed = True
#		self.message = message
#
#	def on_message(self, c, e):
#		if self.changed:
#			c.send(c, message)
#			self.changed = False



class Client(object):
	def __init__(self, username, password, site):
		self.username = username
		self.password = password
		self.session = requests.session()
		self.wiki = site.rstrip('/')
		self.__login(username, password)
		data = self.__wikia_request(controller="Chat", format="json")
		self.settings = {}
		self.settings['chatkey'] = data['chatkey']
		self.settings["port"] = data["nodePort"]
		self.settings["host"] = data["nodeHostname"]
		self.settings["room"] = data["roomId"]
		self.settings["chatmod"] = data["isChatMod"]
		self.settings["session"] = self.__get_session(self.settings)
		self.xhr = self.__initialize(self.settings)
		self.priv_dict = {}

	def __login(self, username, password):
		login_data = {
			'action': 'login',
			'lgname': username,
			'lgpassword': password,
			'format':'json'}
		data = urllib.urlencode(login_data)
		response = self.session.post(self.wiki + "/api.php",data=login_data)
		content = json.loads(response.content)
		login_data['lgtoken'] = content['login']['token']
		data = urllib.urlencode(login_data)
		response = self.session.post(self.wiki + "/api.php",data=login_data)
		content = json.loads(response.content)
		if content['login']['result'] != 'Success':
			print 'Couldn\'t log in: Quitting.'
			sys.exit(1)

	def __wikia_request(self, **kwargs):
		request = {}
		for karg in kwargs:
			request[karg] = kwargs[karg]
		response = self.session.get(self.wiki + "/wikia.php",params=request)
		content = json.loads(response.content)
		return content

	def __get_session(self, settings):
		data = self.session.get("http://" + settings["host"] + ":" + settings["port"] + "/socket.io/1/?name=" +
			self.username + "&key=" + settings["chatkey"]
			+ "&roomId=" + str(settings["room"]) + "&jsonp=1")
		return data.text

	def __initialize(self, settings):
		data = self.session.get("http://" + settings["host"] + ":" + settings["port"] + "/socket.io/1/xhr-polling/?name=" +
			self.username + "&key=" + settings["chatkey"]
			+ "&roomId=" + str(settings["room"]) + "&jsonp=1")
		return data.content

	def __timestamp(self):
		unix = time.time()
		return str(round(unix, 0))

	def __get_code(self, xhr):
		regex = re.compile(r'io\..*?\(\"(.*?):.*?\"\);')
		array = regex.findall(xhr)
		if array:
			return array[0]
		else:
			return None

	def __send(self, settings, xhr, message):
		xhr_polling = self.__get_code(xhr)
		extras =  json.dumps({'attrs': {'msgType': 'chat', 'text': message}})
		data = self.session.post("http://" + settings["host"] + ":" + settings["port"] + "/socket.io/1/xhr-polling/" + xhr_polling + "?name=" +
			self.username + "&key=" + 
			settings['chatkey'] + "&roomId=" + str(settings['room']) + "&t=" + self.__timestamp(),
			'5:::' + json.dumps({'name':'message','args': [extras]}))
		return

	def __go_away(self, settings, xhr):
		xhr_polling = self.__get_code(xhr)
		extras = json.dumps({'attrs': {'msgType':'command','command':'setstatus','statusState':'away'}})
		data = self.session.post("http://" + settings["host"] + ":" + settings["port"] + "/socket.io/1/xhr-polling/" + xhr_polling + "?name=" +
			self.username + "&key=" + 
			settings['chatkey'] + "&roomId=" + str(settings['room']) + "&t=" + self.__timestamp(),
			'5:::' + json.dumps({'name': 'message','args': [extras]}))
		return

	def __come_back(self, settings, xhr):
		xhr_polling = self.__get_code(xhr)
		extras = json.dumps({'attrs': {'msgType':'command','command':'setstatus','statusState':'here'}})
		data = self.session.post("http://" + settings["host"] + ":" + settings["port"] + "/socket.io/1/xhr-polling/" + xhr_polling + "?name=" +
			self.username + "&key=" +
			settings['chatkey'] + "&roomId=" + str(settings['room']) + "&t=" + self.__timestamp(),
			'5:::' + json.dumps({'name': 'message','args': [extras]}))
		return

	def __kick_user(self, settings, xhr, user):
		xhr_polling = self.__get_code(xhr)
		extras = json.dumps({'attrs': {'msgType':'command','command':'kick','userToKick':user}})
		data = self.session.post("http://" + settings["host"] + ":" + settings["port"] + "/socket.io/1/xhr-polling/" + xhr_polling + "?name=" +
			self.username + "&key=" + 
			settings['chatkey'] + "&roomId=" + str(settings['room']) + "&t=" + self.__timestamp(),
			'5:::' + json.dumps({'name': 'message', 'args': [extras]}))
		return

	def __ban_user(self, settings, xhr, user, time, reason):
		xhr_polling = self.__get_code(xhr)
		extras = json.dumps({'attrs': {'msgType':'command','command':'ban','userToBan':user,
			'time':time,'reason':reason}})
		data = self.session.post("http://" + settings["host"] + ":" + settings["port"] + "/socket.io/1/xhr-polling/" + xhr_polling + "?name=" +
			self.username + "&key=" + 
			settings['chatkey'] + "&roomId=" + str(settings['room']) + "&t=" + self.__timestamp(),
			'5:::' + json.dumps({'name': 'message','args': [extras]}))
		return

	def __end_ban(self, settings, xhr, user, reason):
		xhr_polling = self.__get_code(xhr)
		extras = json.dumps({'attrs': {'msgType':'command', 'command':'ban', 'userToBan':user,
			'time':'0', 'reason':reason}})
		data = self.session.post("http://" + settings["host"] + ":" + settings["port"] + "/socket.io/1/xhr-polling/" + xhr_polling + "?name=" +
			self.username + "&key=" + 
			settings['chatkey'] + "&roomId=" + str(settings['room']) + "&t=" + self.__timestamp(),
			'5:::' + json.dumps({'name': 'message', 'args': [extras]}))
		return

	def __give_chatmod(self, settings, xhr, user):
		xhr_polling = self.__get_code(xhr)
		extras = json.dumps({'attrs': {'msgType': 'command','command': 'givechatmod', 'userToPromote': user}})
		data = self.session.post("http://" + settings["host"] + ":" + settings["port"] + "/socket.io/1/xhr-polling/" +
								xhr_polling + "?name=" + self.username + "&key=" + 
								settings['chatkey'] + "&roomId=" + str(settings['room']) +
								"&t=" + self.__timestamp(),
								'5:::' + json.dumps({'name': 'message',
								'args': [extras]}))
		return

	def __disconnect(self, settings, xhr, nodisconnect=False):
		xhr_polling = self.__get_code(xhr)
		extras = json.dumps({'attrs': {'msgType': 'command','command': 'logout'}})
		data = self.session.post("http://" + settings["host"] + ":" + settings["port"] + "/socket.io/1/xhr-polling/" +
								xhr_polling + "?name=" + self.username + "&key=" + 
								settings['chatkey'] + "&roomId=" + str(settings['room']) +
								"&t=" + self.__timestamp(),
								'5:::' + json.dumps({'name': 'message',
								'args': [extras]}))
		if not nodisconnect:
			sys.exit(0)
		return

	def __private_message_id(self, user):
		data = self.session.post(self.wiki + "/index.php?action=ajax&rs=ChatAjax&method=getPrivateRoomId&users=[\"" +
									user + "\",\"" + self.username + "\"]")
		content = json.loads(data.content)
		roomid = content['id']
		return roomid

	def __open_private_chat(self, settings, xhr, user, room):
		xhr_polling = self.__get_code(xhr)
		extras = json.dumps({'attrs': {'msgType': 'command','command': 'openprivate', 'roomId':str(room),
										'users': [user]}})
		data = self.session.post("http://" + settings["host"] + ":" + settings["port"] + "/socket.io/1/xhr-polling/" +
								xhr_polling + "?name=" + self.username + "&key=" + 
								settings['chatkey'] + "&roomId=" + str(settings["room"]) +
								"&t=" + self.__timestamp(),
								'5:::' + json.dumps({'name': 'message',
								'args': [extras]}))
		return

	def __private_message(self, settings, user, message):
		if self.priv_dict.has_key(user):
			xhr = self.__initialize(settings)
			self.__open_private_chat(settings, xhr, user, self.__private_message_id(user))
			self.priv_dict[user].send(message, xhr)
		else:
			self.priv_dict[user] = PrivateMessage(user, self.username,
												self.password, self.wiki, settings['chatkey'])
			self.__private_message(settings, user, message)

	def send(self, message, xhr=None):
		if xhr:
			self.__send(self.settings, xhr, message)
		else:
			self.__send(self.settings, self.xhr, message)

	def private_message(self, user, message):
		self.__private_message(self.settings, user, message)

	def go_away(self):
		self.__go_away(self.settings, self.xhr)

	def come_back(self):
		self.__come_back(self.settings, self.xhr)

	def kick_user(self, user):
		self.__kick_user(self.settings, self.xhr, user)

	def ban_user(self, user, time=3600, reason='Misbehaving in chat'):
		self.__ban_user(self.settings, self.xhr, user, time, reason)

	def end_ban(self, user, reason='Ending chat ban'):
		self.__end_ban(self.settings, self.xhr, user, reason)

	def give_chatmod(self, user):
		self.__give_chatmod(self.settings, self.xhr, user, reason)

	def disconnect(self, nodisconnect=False):
		self.__disconnect(self.settings, self.xhr, nodisconnect=nodisconnect)

	def __connection(self, settings, xhr):
		xhr_polling = self.__get_code(xhr)
		time = self.__timestamp()
		data = self.session.get("http://" + settings["host"] + ":" +
								settings["port"] +
								"/socket.io/1/xhr-polling/" + xhr_polling
								+ "?name=" + self.username + "&key=" +
								settings['chatkey'] + "&roomId=" +
								str(settings['room']) + "&t=" +
								time)
		content = re.findall(r'.:::(.*)', data.content.decode('utf8'))
		if content:
			try:
				loads = json.loads(content[0])
				return loads
			except ValueError:
				return None
		else:
			return None

	def connection(self):
		var = self.__connection(self.settings, self.xhr)
		return var


class ChatBot(threading.Thread):
	def __init__(self, username, password, site):
		self.username = username
		self.password = password
		self.c = Client(username, password, site)
		threading.Thread.__init__(self)

	def on_welcome(self, c, e):
		pass

	def on_join(self, c, e):
		pass

	def on_leave(self, c, e):
		pass

	def on_message(self, c, e):
		pass

	def on_away(self, c, e):
		pass

	def on_back(self, c, e):
		pass

	def on_kick(self, c, e):
		pass

	def on_ban(self, c, e):
		pass

	def on_chatmod(self, c, e):
		pass

	def on_idle(self, c, e):
		pass

	def run(self):
		in_chat = 0
		while 1:
			connect = self.c.connection()
			if connect:
				in_chat += 1
				e = Event(connect)
				if in_chat == 1:
					self.on_welcome(self.c, e)
				elif connect["event"] == "join":
					self.on_join(self.c, e)
				elif connect["event"] == "logout":
					self.on_leave(self.c, e)
				elif connect["event"] == "part":
					self.on_leave(self.c, e)
				elif connect["event"] == "updateUser" and connect["data"]["attrs"]["statusState"] == 'away':
					self.on_away(self.c, e)
				elif connect["event"] == "updateUser" and connect["data"]["attrs"]["statusState"] == 'here':
					self.on_back(self.c, e)
				elif connect["event"] == "kick":
					self.on_kick(self.c, e)
				elif connect["event"] == "ban":
					self.on_ban(self.c, e)
				elif e.made_chat_mod is True:
					self.on_chatmod(self.c, e)
				elif connect["event"] == "chat:add":
					self.on_message(self.c, e)
				else:
					self.on_idle(self.c, e)

if __name__ == '__main__':
	print("""This file isn't exucutable.
Please go to http://community.wikia.com/wiki/User:Hairr/Chatbot for information
on how to set up. Thanks.""")