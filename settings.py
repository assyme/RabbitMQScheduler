#!usr/local/bin python

config = {}
config["RabbitMQConnectionString"] = "localhost"
config["SMTPServer"] = "mailtrap.io"
config["SMTPPort"] = 2525
config["SMTPUserName"] = "3321856fe60860009"
config["SMTPPassword"] = "1d21e5c26c2256"

# Settings for our scheduler
config["PauseSMS"] = ("08:34",1) # time in HH:MM (24h) format, Minutes to puase for. 