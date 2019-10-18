import pika

host = '127.0.0.1'
port = 5672
user = 'guest'
password = 'guest'
connection_attempts = 1

connection_parameters = pika.ConnectionParameters(
        host=host,
        port=port,
        credentials=pika.credentials.PlainCredentials(user, password),
        heartbeat=0,
        connection_attempts=connection_attempts
)