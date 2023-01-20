import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")
LOCATION = os.getenv("LOCATION")
SSL_CA_CERTS = os.getenv("SSL_CA_CERTS")
USERNAME_DB = os.getenv("USERNAME_DB")
PWD_DB = os.getenv("PWD_DB")
IP_EC2 = os.getenv("IP_EC2")
SSH_PKEY = os.getenv("SSH_PKEY")
REMOTE_BIND_ADDRESS = os.getenv("REMOTE_BIND_ADDRESS")