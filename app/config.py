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
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))  # Base directory of the app
    UPLOAD_FOLDER = os.path.join(BASE_DIR, 'static', 'image')  # Upload folder path
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

    @staticmethod
    def allowed_file(filename):
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS
