import os

# oracle
ORACLE_SERVER = os.getenv("ORACLE_SERVER", "demodb/123456@10.88.190.203:1521/xe")

# edtech
EDTECH_SERVER_URL = os.getenv("EDTECH_SERVER_URL", "http://10.88.190.100:12363")
EDTECH_SERVER_TOKEN = os.getenv("EDTECH_SERVER_TOKEN", 'Token 6c5a192e3e161342489971b10d36dee5250e64dd')

# classcard
CLASS_CARD_SERVER_URL = os.getenv("CLASS_CARD_SERVER_URL", "http://10.88.190.100:14001")
CLASS_CARD_SERVER_TOKEN = os.getenv("CLASS_CARD_SERVER_TOKEN", 'Skeleton gjtxsjtyjsxqsl Z2p0eHNqdHlqc3hxc2w=')

JSON_PATH = ""

SCHOOL_NAME = os.getenv("SCHOOL_NAME", "山东师范大学")
