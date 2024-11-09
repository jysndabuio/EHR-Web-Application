import os
from dotenv import load_dotenv


load_dotenv(override=True)
load_dotenv(verbose=True)

# Secure Credentials 
username = os.getenv("USERNAME")
password = os.getenv("PASSWORD")
secret_key = os.getenv("SECRET_KEY")

print("Loaded USERNAME:", os.getenv("USERNAME"))

print("Current Working Directory:", os.getcwd())
