#!usr/local/bin python
import pika
import threading

class RabbitThreadedConsumer(threading.Thread):

	def __init__(self,queue_name,callback):
		'''
		RabbitMQ consumer that listens to a particular queue in a separate thread.
		@input: 
			queue_name: name of the queue to listen to. 
			callback: callback function to call when a new message is encountered.
		'''
		threading.Thread.__init__(self)
		self.__callback = callback
		self.__connection = None
		self.__channel = None
		self.__queue_name = queue_name

	def run(self):
		self.__stop = False;
		connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
		
		channel = connection.channel()
		
		channel.queue_declare(
			queue=self.__queue_name,
			durable=True
			)

		channel.basic_consume(
			self.__callback,
			queue=self.__queue_name
			)

		self.__connection = connection
		self.__channel = channel

		if (self.__stop == False):
			try:
				print "[Info] : SMS listener started."
				channel.start_consuming()
			except:
				print "[Info] : SMS listener stopped."
				channel.stop_consuming()
				connection.close()


	def stop_consuming(self):
		'''
		Stops listening to the RabbitMQ queue and closes the connection.  
		'''
		print "[Info] : SMS listerner stopped by parent thread"
		self.__stop = True
		if (self.__channel != None):
			self.__channel.stop_consuming()
		if (self.__connection != None):	
			self.__connection.close()
