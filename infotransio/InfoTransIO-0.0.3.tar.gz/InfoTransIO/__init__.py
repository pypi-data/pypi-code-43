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
class Client:
	def __init__(self, ClientPin):
		self.ClientPin=ClientPin
	def Catch(self):
		inbox = ClientReceive.inbox.unread()
		for i in inbox:
			x = str(i.subject)
			Received = i.body
			if x == self.ClientPin:
				return Received
	def Transmit(self, message):
		self.message = message
		ClientSend.redditor('InfoTransIO').message(self.ClientPin, self.message)