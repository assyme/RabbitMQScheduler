#!usr/local/bin python
import sched, time
from datetime import datetime, timedelta
import threading
import pika
from RabbitThreadedConsumers import RabbitThreadedConsumer

class SchedSms:

	def __init__(self,pauseIntervals):
		'''
		Initialized the scheduler. 
		@Inputs : a tuple that defines pause Intervals (starttime in 24hour format, duration to pause)
		'''

		self.__pauseIntervals = pauseIntervals
		self.__timerThread = None
		self.__currentListener = None

		self.__connection = pika.BlockingConnection(pika.ConnectionParameters(host="localhost"))
		self.__channel = self.__connection.channel()


		self.__channel.queue_declare(
			queue="sms_queue",
			durable=True
			)

		self.Schedule()

	def SendSMS(self,ch,method,properties,body):
		'''
		Callback handler for smses from the local RabbitMQ queue
		'''
		print "[Info] : You recieved a new SMS ", body
		ch.basic_ack(delivery_tag=method.delivery_tag)

	def Send(self,message):
		'''
		Sends the sms to our internal queue
		'''
		try:
			self.__channel.basic_publish(
				exchange="",
				routing_key="sms_queue",
				body=str(message),
				properties = pika.BasicProperties(
					delivery_mode = 2
					)
				)
			return True
		except:
			return False


	def StartSms(self,schedule_again):
		self.__currentListener = RabbitThreadedConsumer("localhost","sms_queue",self.SendSMS)
		self.__currentListener.setDaemon(True)
		self.__currentListener.start()
		if schedule_again:
			self.Schedule()

	def PauseSms(self):
		if (self.__currentListener != None):
			self.__currentListener.stop_consuming()
		self.Schedule()

	def Schedule(self):
		dailyIntervalStartTime = datetime.strptime(self.__pauseIntervals[0],"%H:%M")
		start_time = datetime.now().replace(
			hour=dailyIntervalStartTime.hour,
			minute=dailyIntervalStartTime.minute
			)

		end_time = start_time + timedelta(minutes = self.__pauseIntervals[1])
		now = datetime.now()

		if start_time < now < end_time:
			print "SMS paused until: ", end_time
			delay = (end_time - now).total_seconds()
			self.__timerThread = threading.Timer(delay,self.StartSms,[True])
			self.__timerThread.start()
			
		else:
			if start_time < now:
				#start it tomorrow
				start_time = start_time + timedelta(days = 1)
			
			delay = (start_time - now ).total_seconds()
			print "SMS will pause at " , start_time
			self.__timerThread = threading.Timer(delay,self.PauseSms)
			self.__timerThread.start()
			self.StartSms(False)


	def Stop(self):
		print "Stopping SMS messenger"
		self.__timerThread.cancel()
		if self.__currentListener != None:
			self.__currentListener.stop_consuming()
		self.__connection.close()
		

			
