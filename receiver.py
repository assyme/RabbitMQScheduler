#!usr/local/bin python
import pika
from settings import config
from rabbitmessenger.emailsender import EmailSender
from rabbitmessenger.SchedSms import SchedSms
import ast
from rabbitmessenger.RabbitThreadedConsumers import RabbitThreadedConsumer
import logging
import time

#logging.basicConfig(level=logging.DEBUG,format='[%(levelname)s] (%(threadName)-10s) %(message)s',)

class receiver():
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
		
		#by now we recieved a message. 
		if message["type"] == "email":
			print "[Info] : recieved email message"
			isSuccess = self.emailer.Send(message)
		elif message["type"] == "sms":
			print "[Info] : recieved sms message"
			isSuccess = self.smser.Send(message);
		else:
			print "[Error] : Unkown message type. System can handle only emails and smses yet."

		if (isSuccess):
			ch.basic_ack(delivery_tag=method.delivery_tag)
		return


	def start_listening(self,host,queue):
		self.__rabbit_consumer = RabbitThreadedConsumer(host,queue,self.messageHandler)
		self.__rabbit_consumer.setDaemon(True)
		self.__rabbit_consumer.start()

	def stop_listening(self):
		if self.__rabbit_consumer != None:
			self.__rabbit_consumer.stop_consuming()
			self.emailer.Stop();
			self.smser.Stop();
		

if __name__ == "__main__":
	current_reciever = receiver()
	current_reciever.start_listening('localhost','jrd_main_messages')
	try:
		print "Messenger started. press ctrl + c to exit."
		while True:
			time.sleep(1)
	except KeyboardInterrupt:
		print "stopping the app."
		current_reciever.stop_listening()

