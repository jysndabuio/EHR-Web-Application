from dotenv import load_dotenv
import os

load_dotenv(override=True)

print(f"SECRET_KEY loaded: {os.getenv('MAIL_PASSWORD')}")
