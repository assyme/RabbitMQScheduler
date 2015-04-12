#!usr/bin/env python
import sys
import pika
from settings import config


def main():
	''' 
	Main function that kickstarts the module.
	'''

	queue_name = "jrd_main_messages"

	#establish a connection to the rabbitMQ Queue
	#TODO : pick the connection string for a settings file. 
	connection = pika.BlockingConnection(pika.ConnectionParameters(config["RabbitMQConnectionString"]))
	channel = connection.channel();

	channel.queue_declare(
		queue=queue_name, # Name of the queue
		durable=True # even if rabbitmq quits or crashes, the messages will be persisted. 
		)

	emailMessage = {
	'type': 'email',
	'from': 'no-reply@company.com',
  	'recipients': ['someone@mail.com','another@mail.com'],
  	'html': 'This is a test email. It can <i>also</i> contain HTML code',
  	'text': 'This is a test email. It is text only'
	}

	smsMessage = {
	'type': 'sms',
	'from': 'JRD',
	'recipients': ['+971501478902'],
	'body': 'Test SMS message body'
	}


	messageCount = int(sys.argv[1]) if (len(sys.argv) > 1) else 1

	for i in range(messageCount):
		channel.basic_publish(
			exchange='',
			routing_key=queue_name,
			body=str(emailMessage),
			properties = pika.BasicProperties(
				delivery_mode = 2
				)
			)

		print "[x] email message was sent %s" % (str(emailMessage),)
		
		channel.basic_publish(
			exchange='',
			routing_key=queue_name,
			body=str(smsMessage),
			properties = pika.BasicProperties(
				delivery_mode = 2
				)
			)

		print "[x] sms message was sent: %s" % (str(smsMessage))
	
	connection.close()

if __name__ == "__main__":
	main()