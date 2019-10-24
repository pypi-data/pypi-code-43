import praw
ClientReceive = praw.Reddit(client_id='pJiFib-84vzdvw',
					client_secret="GuzjG3LnIhXwM-19-kP6D1YF0HA",
					password='InfoTrans1234567890IO',
					user_agent='USERAGENT',
					username='InfoTransIO')
ClientSend = praw.Reddit(client_id='miJ9pQZDRWJfAQ',
					client_secret="mpMDEK2AnTE2hXNUs3P5HCDHxeA",
					password='InfoTrans1234567890IO',
					user_agent='USERAGENT',
					username='InfoTransIO2')
class Message:
	def __init__(self, time, body, mesid, ServerPin):
		self.time= time
		self.body = body
		self.ServerPin = ServerPin
		self.mesid = mesid
		
class Client:
	def __init__(self, ClientPin):
		self.ClientPin=ClientPin
	def Catch(self):
		inbox = ClientReceive.inbox.unread()
		for i in inbox:
			x = str(i.subject)
			Received = Message(body=i.body, time=i.created_utc, ServerPin=self.ClientPin, mesid=i.id)
			if x == self.ClientPin:
				return Received
	def Listen(self):
		pass
	def GetAll(self):
		inbox = ClientReceive.inbox.unread()
		lis = []
		for i in inbox:
			x = str(i.subject)
			if x == self.ClientPin:
				Received = Message(body=i.body, time=i.created_utc, ServerPin=self.ClientPin, mesid=i.id)
				lis.append(Received)
		return lis
	def Transmit(self, message):
		self.message = message
		ClientSend.redditor('InfoTransIO').message(self.ClientPin, self.message)