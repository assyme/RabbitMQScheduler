#!usr/local/bin python
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

class EmailSender():
	def __init__(self,smtp_server,smtp_port,smtp_user,smtp_password,keep_alive = True):
		self._smtp_server = smtp_server
		self._smtp_port = smtp_port
		self._smtp_user = smtp_user
		self._smtp_password = smtp_password
		self._keep_alive = keep_alive
		self._server = None

	def Send(self,message):
		'''
		Helper function to send emails. 
		@Parameters : emailMessageDetails : a dictionary with from, recipients, text, html to send jrd_main_messages
		@Returns : success boolean for the operation
		'''
		server = self.__establish_connection()

		if (self._keep_alive):
			self._server = server

		fromAddress = message["from"]
		toAddress = ",".join(message["recipients"])
		#TODO: Validate the email addresses. 
		msg = MIMEMultipart('alternative')
		msg['Subject'] = "TestMail"
		msg['From'] = fromAddress
		msg['To'] = toAddress

		messageBody = None
		if message["text"] != None:
			messageBody = MIMEText(message["html"], 'html')
			msg.attach(messageBody)
		if message["html"] != None:
			messageBody = MIMEText(message["html"], 'plain') 
			msg.attach(messageBody)

		#send the message
		try:
			response = server.sendmail(fromAddress,message["recipients"],msg.as_string())
			print "[Info] : Email was sent successfully"
			return True
		except SMTPException:
			print "[Error] : Could not send email. Will try again"
			return False

		if (self._keep_alive != True):
			server.quit()


	def __establish_connection(self):
		if (self._server != None):
			return self._server

		server = smtplib.SMTP(self._smtp_server,self._smtp_port)

		if (self._smtp_user != None and self._smtp_password != None):
			response = server.login(self._smtp_user,self._smtp_password) 
			#TODO: Password CRAM-MD5
			#TODO : Verify response and that the connection was established.

		return server

	def Stop(self):
		if (self._server != None):
			self._server.quit()

