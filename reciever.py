#!usr/local/bin python
import pika
from settings import config
from rabbitmessenger.emailsender import EmailSender
from rabbitmessenger.SchedSms import SchedSms
import ast

class receiver:
	def __init__(self):
		self.emailer = EmailSender(
			config["SMTPServer"],
			config["SMTPPort"],
			config["SMTPUserName"],
			config["SMTPPassword"]
			)

		self.smser = SchedSms(config["PauseSMS"])


	def messageHandler(self,ch,method,properties,body):
		message = None
		#parse the body message
		try:
			message = ast.literal_eval(body)
		except ValueError:
			print "[Error] : This reciever does not accept non dictionary messages."
			ch.basic_ack(delivery_tag=method.delivery_tag) #thrash the message from the queue
			return

		isSuccess = False
		print "[Info] : recieved message : ", message
		#by now we recieved a message. 
		if message["type"] == "email":
			isSuccess = self.emailer.Send(message)
		elif message["type"] == "sms":
			isSuccess = self.smser.Send(message);
		else:
			print "[Error] : Unkown message type. System can handle only emails and smses yet."

		if (isSuccess):
			ch.basic_ack(delivery_tag=method.delivery_tag)
		return


	def start_listening(self,host,queue_name):

		connection = pika.BlockingConnection(pika.ConnectionParameters(host))
		channel = connection.channel()

		channel.queue_declare(
			queue=queue_name,
			durable=True #even if rabbitmq quits or crashes, messages will be persisted. 
			)

		channel.basic_consume(
			self.messageHandler,
			queue_name
			)

		print "[Info] : Waiting for messages. to exit, press CTRL + C"

		try:
			channel.start_consuming()
		except:
			print "[Info] : stopping from main thread."
			channel.stop_consuming()
			connection.close()
			self.emailer.Stop()
			self.smser.Stop()


if __name__ == "__main__":
	current_reciever = receiver()
	current_reciever.start_listening('localhost','jrd_main_messages')
