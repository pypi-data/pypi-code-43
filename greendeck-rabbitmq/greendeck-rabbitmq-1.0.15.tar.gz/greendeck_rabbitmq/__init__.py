print("you are using greendeck_rabbitmq package")

# your package information
name = "greendeck_rabbitmq"
__version__ = "1.0.15"
author = "chandan mishra"
author_email = "chandan.mishra@greendeck.co"
url = ""

# import sub packages
from .src.rabbitmq.rabbitmq import RabbitMQ
