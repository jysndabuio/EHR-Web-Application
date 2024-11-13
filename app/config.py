from dotenv import load_dotenv
import os 

# Load env file with override global variables
# Without override one variable is loaded from global env not from custom env.
load_dotenv(override=True)

class Config:
    # Secure Credentials 
    username = os.getenv("USERNAME")
    password = os.getenv("PASSWORD")
    secret_key = os.getenv("SECRET_KEY")
    TOKEN_SECRET_KEY = os.getenv('TOKEN_SECRET_KEY') 
    SQLALCHEMY_TRACK_MODIFICATIONS = False 
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{username}:{password}@localhost/EHR_DB_MODEL"