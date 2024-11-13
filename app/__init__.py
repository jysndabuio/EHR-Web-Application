from flask import Flask, session, redirect, url_for, request
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_bcrypt import Bcrypt
from .config import Config
from flask_mail import Mail
from flask_login import LoginManager, current_user


db = SQLAlchemy()
migrate = Migrate()
bcrypt = Bcrypt()
login_manager = LoginManager()
mail = Mail()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = Config.secret_key
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    bcrypt.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = "main.login" # Redirect to login if not authenticatedä
    mail.init_app(app)
    
    # Import models after db is initialized
    from . import models

    # Register routes
    from . import routes
    app.register_blueprint(routes.bp)

    # Redirect logged-in users to their dashboards if they try to access login, register, or home page
    #@app.before_request
    #def check_login_redirect():
        #if 'user_id' in session:
            #role = session.get('role')
            #if request.endpoint in ['main.login', 'main.register', 'main.index']:
               #return routes.redirect_dashboard(role)  # Call `redirect_dashboard` from routes
            
    # Redirect authenticated users if they attempt to access login, register, or home
    @app.before_request
    def check_login_redirect():
        if current_user.is_authenticated:
            if request.endpoint in ['main.login', 'main.register', 'main.index']:
                return routes.redirect_dashboard(current_user.role)  # Call `redirect_dashboard`


    return app

# User loader function
@login_manager.user_loader
def load_user(user_id):
    from .models import User
    return User.query.get(user_id)